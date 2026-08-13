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


import typer

from imarina_load_researchers.core.defines import (
    DEFAULT_PUBLISHED_FILE_PATH,
    DEFAULT_TARGET_DIR,
    SHAREPOINT_LOCAL_OUTPUT_DIR,
)
from imarina_load_researchers.core.file_select import select_file_to_upload
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.shared_options import (
    TargetFolderOpt,
    UploadFilePathOpt,
)
from imarina_load_researchers.core.sharepoint import upload_file
from imarina_load_researchers.core.token_manager import get_token_manager

logger = get_logger(__name__)


def upload_controller(
    ctx: typer.Context,
    file_path: UploadFilePathOpt = DEFAULT_PUBLISHED_FILE_PATH,
    target_folder: TargetFolderOpt = DEFAULT_TARGET_DIR,
) -> None:
    logger.info("Uploading the latest Excel file to SharePoint...")

    if file_path is None:
        file_path = select_file_to_upload(SHAREPOINT_LOCAL_OUTPUT_DIR)

    logger.info(f"Local file detected: {file_path.name}")
    logger.info(f"Destination SharePoint: {target_folder}")

    try:

        upload_file(
            token_manager=get_token_manager(),
            local_file_path=file_path,
            target_folder=target_folder,
            drive_id=read_secret(SecretName.DRIVE_ID),
        )
        logger.info(f"Successfully uploaded {file_path.name}")

    # Broad on purpose: CLI boundary turns any failure into a clean exit(1).
    except Exception as e:
        logger.exception("Error uploading to SharePoint")
        raise typer.Exit(code=1) from e
