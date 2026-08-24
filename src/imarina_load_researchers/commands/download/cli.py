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

from pathlib import Path

import typer

from imarina_load_researchers.core.defines import (
    REQUIRED_INPUT_FILES,
    SHAREPOINT_INPUT_DIR,
    SHAREPOINT_LOCAL_INPUT_DIR,
    SHAREPOINT_REMOTE_A3_DIR,
    SHAREPOINT_REMOTE_IMARINA_DIR,
    SHAREPOINT_REMOTE_PUBLISHED_DIR,
)
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.shared_options import DirectoryOpt, OperationIdOpt
from imarina_load_researchers.core.sharepoint import (
    create_sharing_link,
    download_files_in_folder_from_sharepoint,
    download_item_content,
    download_shared_link_content,
    get_parameters_list,
    get_token_manager,
    select_latest_remote_file,
    update_list_item_fields,
    upload_file,
)
from imarina_load_researchers.core.sharepoint_fields import (
    FIELD_A3_EXCEL_INPUT_LINK,
    FIELD_IMARINA_EXCEL_INPUT_LINK,
    FIELD_WORKFLOW_STATE,
    WorkflowState,
)
from imarina_load_researchers.core.token_manager import TokenManager

logger = get_logger(__name__)


def _fallback_a3(
    token_manager: TokenManager, drive_id: str, id_element: int, input_dir: Path
) -> None:
    """No A3 link was supplied: fall back to the latest dump in runtime/a3.

    No copy step is needed here (unlike the iMarina fallback below):
    runtime/a3 is already both where A3 dumps are manually uploaded and where
    this fallback reads the latest one from (STEPS.md).
    """
    remote_file = select_latest_remote_file(
        token_manager, drive_id, SHAREPOINT_REMOTE_A3_DIR
    )
    download_item_content(
        token_manager, drive_id, remote_file.id, input_dir / "A3.xlsx"
    )
    link = create_sharing_link(token_manager, drive_id, remote_file.id)
    update_list_item_fields(str(id_element), {FIELD_A3_EXCEL_INPUT_LINK: link})
    logger.info(f"A3.xlsx fell back to latest dump: {remote_file.name}")


def _fallback_imarina(
    token_manager: TokenManager, drive_id: str, id_element: int, input_dir: Path
) -> None:
    """No iMarina link was supplied: fall back to the latest published file in
    runtime/published, and re-upload that same local copy into
    runtime/imarina so the "iMarina Excel input link" field always points at
    a file in the folder used as an input, not the published-archive folder
    (STEPS.md — the file is copied, not linked, because the commands' source
    of truth is the files present in the folders).
    """
    remote_file = select_latest_remote_file(
        token_manager, drive_id, SHAREPOINT_REMOTE_PUBLISHED_DIR
    )
    destination = input_dir / "iMarina.xlsx"
    download_item_content(token_manager, drive_id, remote_file.id, destination)
    copied_item_id = upload_file(
        token_manager, drive_id, SHAREPOINT_REMOTE_IMARINA_DIR, destination
    )
    link = create_sharing_link(token_manager, drive_id, copied_item_id)
    update_list_item_fields(str(id_element), {FIELD_IMARINA_EXCEL_INPUT_LINK: link})
    logger.info(f"iMarina.xlsx fell back to latest published file: {remote_file.name}")


def download_controller(
    ctx: typer.Context,
    id_element: OperationIdOpt,
    input_dir: DirectoryOpt = SHAREPOINT_LOCAL_INPUT_DIR,
) -> None:

    logger.info(f"Starting download of input files from SharePoint into: {input_dir}")

    try:
        update_list_item_fields(
            str(id_element), {FIELD_WORKFLOW_STATE: WorkflowState.PREPARING}
        )
    except Exception:
        # Best-effort bookkeeping: must not block the actual download below.
        logger.exception("Error updating Workflow State to Preparing")

    drive_id = read_secret(SecretName.DRIVE_ID)

    try:
        download_files_in_folder_from_sharepoint(
            drive_id, input_dir, Path(SHAREPOINT_INPUT_DIR)
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

        if a3_link:
            download_shared_link_content(token_manager, a3_link, input_dir / "A3.xlsx")
            logger.info("A3.xlsx download successful")
        else:
            logger.warning("URL not found for A3.xlsx, falling back to latest A3 dump")
            _fallback_a3(token_manager, drive_id, id_element, input_dir)

        if imarina_link:
            download_shared_link_content(
                token_manager, imarina_link, input_dir / "iMarina.xlsx"
            )
            logger.info("iMarina.xlsx download successful")
        else:
            logger.warning(
                "URL not found for iMarina.xlsx, falling back to latest published file"
            )
            _fallback_imarina(token_manager, drive_id, id_element, input_dir)

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
