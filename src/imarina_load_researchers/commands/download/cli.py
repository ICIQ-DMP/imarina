# imarina-load-researchers - Automated iMarina data loads
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

import base64
from pathlib import Path

import requests
import typer

from imarina_load_researchers.core.defines import (
    REQUIRED_INPUT_FILES,
    SHAREPOINT_INPUT_FOLDER,
    SHAREPOINT_LOCAL_INPUT_DIR,
)
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.shared_options import DirectoryOpt, OperationIdOpt
from imarina_load_researchers.core.sharepoint import (
    download_files_in_folder_from_sharepoint,
    get_parameters_list,
    get_token_manager,
)

logger = get_logger(__name__)


def download_controller(
    ctx: typer.Context,
    id_element: OperationIdOpt,
    input_dir: DirectoryOpt = SHAREPOINT_LOCAL_INPUT_DIR,
) -> None:

    logger.info(f"Starting download of input files from SharePoint into: {input_dir}")

    try:
        download_files_in_folder_from_sharepoint(
            read_secret(SecretName.DRIVE_ID), input_dir, Path(SHAREPOINT_INPUT_FOLDER)
        )

        logger.info(
            f"DONE: Input files successfully downloaded to local directory: {input_dir}"
        )
    except Exception:
        # Intentionally broad: this step's real success/failure is verified by the
        # missing-file check below, which is what actually fails the pipeline.
        logger.exception("Error downloading input files from SharePoint")

    try:
        # Function get_parameters_list and download the links(url) of Excels (A3 Excel and iMarina Excel)
        a3_link, imarina_link = get_parameters_list(str(id_element))
        token_manager = get_token_manager()  # get token
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        for url, filename in [(a3_link, "A3.xlsx"), (imarina_link, "iMarina.xlsx")]:
            if not url:
                logger.warning(f"URL not found for {filename}")
                continue

            encoded = base64.b64encode(url.encode()).decode()
            encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
            download_url = (
                f"https://graph.microsoft.com/v1.0/shares/u!{encoded}/driveItem/content"
            )

            response = requests.get(
                download_url, headers=headers, allow_redirects=True, timeout=300
            )
            response.raise_for_status()
            with open(input_dir / filename, "wb") as f:
                f.write(response.content)
            logger.info(f"{filename} download successful")

    except Exception:
        # Intentionally broad: same rationale as above, the missing-file check below
        # is the actual pass/fail signal for this pipeline stage.
        logger.exception("Error getting parameters for MS List")

    missing = [
        filename
        for filename in REQUIRED_INPUT_FILES.values()
        if not (input_dir / filename).exists()
    ]
    if missing:
        logger.error(f"Missing required input file(s) in {input_dir}:")
        for filename in missing:
            logger.error(f"   - {filename}")
        raise typer.Exit(code=1)

    logger.info(f"All required input files are present in {input_dir}")
