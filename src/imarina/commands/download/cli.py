# imarina-load - Automated imarina data loads
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT) and Sonia Sayalero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from pathlib import Path

import requests
import typer

from imarina.core.defines import REQUIRED_INPUT_FILES
from imarina.core.log_utils import get_logger
from imarina.core.shared_options import DirectoryOpt
from imarina.core.sharepoint import (
    download_input_from_sharepoint,
    get_parameters_list,
    get_token_manager,
)

logger = get_logger(__name__)


def download_controller(
    ctx: typer.Context,
    input_dir: DirectoryOpt = None,
    id: str = typer.Option(..., help="Operation ID from MS List"),
) -> None:
    #  path or input default
    target_path = input_dir if input_dir is not None else Path("input")

    print(f" Starting download of input files from SharePoint into: {target_path}")

    try:
        # function download_input_from_sharepoint
        download_input_from_sharepoint(str(target_path))

        print(
            f" DONE : Input files successfully downloaded to local directory: {target_path}"
        )
    except Exception as e:
        # Intentionally broad: this step's real success/failure is verified by the
        # missing-file check below, which is what actually fails the pipeline.
        print(f" Error downloading input files from SharePoint: {e}")
        logger.exception("Error downloading input files from SharePoint")

    try:
        # Function get_parameters_list and download the links(url) of Excels (A3 Excel and iMarina Excel)
        A3_link, imarina_link = get_parameters_list(id)
        token_manager = get_token_manager()  # get token
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        for url, filename in [(A3_link, "A3.xlsx"), (imarina_link, "iMarina.xlsx")]:
            if not url:
                print(f"URL no found {filename}")
                continue

            import base64

            encoded = base64.b64encode(url.encode()).decode()
            encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
            download_url = (
                f"https://graph.microsoft.com/v1.0/shares/u!{encoded}/driveItem/content"
            )

            response = requests.get(download_url, headers=headers, allow_redirects=True)
            response.raise_for_status()
            with open(target_path / filename, "wb") as f:
                f.write(response.content)
            print(f"{filename} download successful")

    except Exception as e:
        # Intentionally broad: same rationale as above, the missing-file check below
        # is the actual pass/fail signal for this pipeline stage.
        print(f" Error getting parameters for MS List: {e}")
        logger.exception("Error getting parameters for MS List")

    missing = [
        filename
        for filename in REQUIRED_INPUT_FILES.values()
        if not (target_path / filename).exists()
    ]
    if missing:
        print(f"Missing required input file(s) in {target_path}:")
        for filename in missing:
            print(f"   - {filename}")
        raise typer.Exit(code=1)

    print(f"All required input files are present in {target_path}")
