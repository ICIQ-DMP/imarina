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

import typer

from imarina.core.cli_defaults import (
    DEFAULT_TARGET_FOLDER,
    DEFAULT_UPLOAD_FILE_PATH,
    TargetFolderOpt,
    UploadFilePathOpt,
)
from imarina.core.log_utils import get_logger
from imarina.core.sharepoint import upload_file_sharepoint

logger = get_logger(__name__)


def upload_controller(
    ctx: typer.Context,
    file_path: UploadFilePathOpt = DEFAULT_UPLOAD_FILE_PATH,
    target_folder: TargetFolderOpt = DEFAULT_TARGET_FOLDER,
) -> None:
    print(" Uploading the latest Excel file to SharePoint...")

    if file_path is None:
        uploads_dir = Path.cwd() / "output"
        if uploads_dir.exists():
            # recent file in uploads folder
            files = list(uploads_dir.glob("*.xlsx"))
            if files:
                file_path = max(files, key=lambda f: f.stat().st_mtime)
            else:
                print(f"❌ Error: Not files Excel in  {uploads_dir}")
                raise typer.Exit(code=1)
        else:
            print(
                "❌ Error: No file specified and the 'output' folder does not exist.."
            )
            raise typer.Exit(code=1)

    # the file not exist in the path
    if not file_path.exists():
        print(f"❌ Error: The file no exist in the path: {file_path}")
        raise typer.Exit(code=1)

    print(f"📁 Local file detected: {file_path.name}")
    print(f"☁️ Destination SharePoint: {target_folder}")

    try:

        upload_file_sharepoint(file_path, target_folder=str(target_folder))
        print("✅ Upload to SharePoint completed successfully.")
        logger.info(f"Successfully uploaded {file_path.name}")

    # Broad on purpose: CLI boundary turns any failure into a clean exit(1).
    except Exception as e:
        print(f"❌ Error uploading to SharePoint: {e}")
        logger.exception("Error uploading to SharePoint")
        raise typer.Exit(code=1) from e
