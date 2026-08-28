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
    DEFAULT_DRY_RUN,
    DEFAULT_PUBLISH_FILE_PATH,
    FTP_UPLOAD_PATH,
    SHAREPOINT_LOCAL_OUTPUT_DIR,
    SHAREPOINT_REMOTE_PUBLISHED_DIR,
)
from imarina_load_researchers.core.exceptions import OutputLinkMissingError
from imarina_load_researchers.core.file_select import select_file_to_upload
from imarina_load_researchers.core.ftp import FtpCredentials, upload_file_ftp
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.shared_options import (
    DryRunOpt,
    IdOpt,
    PublishFilePathOpt,
)
from imarina_load_researchers.core.sharepoint import (
    create_sharing_link,
    download_shared_link_content,
    get_list_item_link_field,
    get_token_manager,
    update_list_item_fields,
    upload_file,
)
from imarina_load_researchers.core.sharepoint_fields import (
    FIELD_IMARINA_EXCEL_OUTPUT_LINK,
    FIELD_IMARINA_EXCEL_PUBLISHED_LINK,
    FIELD_WORKFLOW_STATE,
    WorkflowState,
)

logger = get_logger(__name__)


def _resolve_file_path(file_path: Path | None, id_element: int | None) -> Path:
    """Resolve publish's input file (see CLAUDE.md's `publish` section):

    - No path, no ID: autodetect the latest local build output, as before.
    - No path, with an ID: source the file from that request's "iMarina
      Excel output link" field instead of the local output/ folder.
    - Explicit path, no ID: use it as given, but warn -- this keeps no
      record of the publish on any MS List request.
    - Explicit path, with an ID: use it as given, no warning (a record is
      kept via the ID either way).
    """
    if file_path is not None:
        if id_element is None:
            logger.warning(
                "Publishing an explicit --file-path without --id keeps no "
                "record of this publish on the MS List request."
            )
        return file_path

    if id_element is None:
        return select_file_to_upload(SHAREPOINT_LOCAL_OUTPUT_DIR)

    link = get_list_item_link_field(str(id_element), FIELD_IMARINA_EXCEL_OUTPUT_LINK)
    if link is None:
        raise OutputLinkMissingError(str(id_element))
    resolved_path = SHAREPOINT_LOCAL_OUTPUT_DIR / f"from_list_item_{id_element}.xlsx"
    download_shared_link_content(get_token_manager(), link, resolved_path)
    return resolved_path


def _archive_published_file(file_path: Path, id_element: int | None) -> None:
    """After a successful (non-dry-run) publish, archive the file to
    runtime/published unconditionally -- it's what the next `download`'s
    iMarina fallback reads from (see CLAUDE.md's "Where the raw inputs come
    from" section) -- and, if an ID was given, write
    back the published link and Workflow State. Every step here is
    best-effort: the publish itself already succeeded by this point.
    """
    try:
        token_manager = get_token_manager()
        drive_id = read_secret(SecretName.DRIVE_ID)
        item_id = upload_file(
            token_manager, drive_id, SHAREPOINT_REMOTE_PUBLISHED_DIR, file_path
        )
    except Exception:
        logger.exception("Error archiving published file to runtime/published")
        return

    if id_element is None:
        return

    try:
        link = create_sharing_link(token_manager, drive_id, item_id)
        update_list_item_fields(
            str(id_element),
            {
                FIELD_IMARINA_EXCEL_PUBLISHED_LINK: link,
                FIELD_WORKFLOW_STATE: WorkflowState.PUBLISHED,
            },
        )
    except Exception:
        logger.exception(
            "Error writing back iMarina Excel published link / Workflow State"
        )


def publish_controller(
    file_path: PublishFilePathOpt = DEFAULT_PUBLISH_FILE_PATH,
    dry_run: DryRunOpt = DEFAULT_DRY_RUN,
    id_element: IdOpt = None,
) -> None:
    """
    Publishes an Excel file into the SFTP server of iMarina service.
    If the Excel is not provided it will be deduced from the output folder using the date in the filename or the last
    modification date.
    By default, only connects to the SFTP server but does not do the upload. To upload the file the parameter --dry-run
    false must be provided.

    If `id_element` is given and `file_path` is not, the file to publish is
    instead sourced from that request's "iMarina Excel output link" field
    (see CLAUDE.md's `publish` section). Publishing an explicit `file_path`
    with no `id_element` keeps no record of the publish on any MS List
    request, which CLAUDE.md flags as something that can cause problems --
    a warning is shown in that case.
    """

    file_path = _resolve_file_path(file_path, id_element)

    if id_element is not None:
        try:
            update_list_item_fields(
                str(id_element), {FIELD_WORKFLOW_STATE: WorkflowState.PUBLISHING}
            )
        except Exception:
            # Best-effort bookkeeping: must not block the actual publish below.
            logger.exception("Error updating Workflow State to Publishing")

    credentials = FtpCredentials(
        host=read_secret(SecretName.FTP_HOST),
        port=int(read_secret(SecretName.FTP_PORT)),
        username=read_secret(SecretName.FTP_USER),
        password=read_secret(SecretName.FTP_PASSWORD),
    )

    try:
        upload_file_ftp(
            path=file_path,
            credentials=credentials,
            dry_run=dry_run,
            upload_filename=FTP_UPLOAD_PATH,
        )
    # Broad on purpose: CLI boundary turns any failure into a clean exit(1).
    except Exception as e:
        logger.exception("Error publishing file to iMarina FTP server")
        raise typer.Exit(code=1) from e

    if dry_run:
        # upload_file_ftp() returns normally without uploading on a dry run --
        # nothing was actually published, so there is nothing to archive or
        # record.
        return

    _archive_published_file(file_path, id_element)
