import datetime
from pathlib import Path
from typing import Optional

import typer

from imarina.core.defines import (
    OUTPUT_DIR,
    FILENAME_PREFIX,
    FILENAME_SUFFIX,
    DATETIME_FORMAT,
    FTP_EXCEL_FILE_DATE_FORMAT,
)
from imarina.core.ftp import upload_file_ftp
from imarina.core.log_utils import get_logger
from imarina.core.secret import read_secret

logger = get_logger(__name__)


def select_file_to_upload(upload_dir: Path) -> Optional[Path]:
    """
    Selects the file to upload from upload_dir.

    Priority:
    1. Latest file matching iMarina_upload_<DATETIME_FORMAT>.xlsx by parsed datetime
    2. Latest .xlsx file by file metadata (modification time)
    3. None if no Excel files exist
    """
    if not upload_dir.exists() or not upload_dir.is_dir():
        logger.debug(
            f"Upload directory {upload_dir} does not exist or is not a directory"
        )
        return None

    excel_files = list(upload_dir.glob("*.xlsx"))
    logger.debug(f"Excel files found: {len(excel_files)}")
    if not excel_files:
        return None

    dated_files: list[tuple[datetime.datetime, Path]] = []
    for file in excel_files:
        name = file.name

        if not name.startswith(FILENAME_PREFIX) or not name.endswith(FILENAME_SUFFIX):
            logger.debug(
                f"File does not start with {FILENAME_PREFIX} or end with {FILENAME_SUFFIX}"
            )
            continue

        datetime_part = name[len(FILENAME_PREFIX) : -len(FILENAME_SUFFIX)]

        try:
            parsed_dt = datetime.datetime.strptime(datetime_part, DATETIME_FORMAT)
        except ValueError:
            logger.debug(
                f"Could not parse datetime: {datetime_part}, from file: {file.name}"
            )
            continue

        dated_files.append((parsed_dt, file))

    if dated_files:
        dated_files.sort(key=lambda x: x[0], reverse=True)
        chosen_file = dated_files[0][1]
        logger.debug(f"Chosen file by date in filename is: {chosen_file}")
        return chosen_file

    # Fallback: latest Excel by modification time
    chosen_file = max(excel_files, key=lambda f: f.stat().st_mtime)
    logger.debug(f"Chosen file by modification date is: {chosen_file}")
    return chosen_file


def publish_controller(
    file_path: Path = typer.Option(
        None, help="Path to the iMarina Excel file to upload to the SFTP server"
    ),
    dry_run: bool = typer.Option(
        True, help="Dry run, connect to FTP server but do not upload files"
    ),
) -> None:
    """
    Publishes an Excel file into the SFTP server of iMarina service.
    If the Excel is not provided it will be deduced from the output folder using the date in the filename or the last
    modification date.
    By default, only connects to the SFTP server but does not do the upload. To upload the file the parameter --dry-run
    false must be provided.
    """

    if file_path is None:
        file_path = select_file_to_upload(OUTPUT_DIR)

        if file_path is None:
            raise RuntimeError(
                f"No Excel file found to upload in directory: {OUTPUT_DIR}"
            )

    host = read_secret("FTP_HOST")
    port = int(read_secret("FTP_PORT"))
    username = read_secret("FTP_USER")
    password = read_secret("FTP_PASSWORD")
    upload_path = f"carga_icolet/icl_ag_personal_12539_{datetime.datetime.now().strftime(FTP_EXCEL_FILE_DATE_FORMAT)}.xlsx"

    logger.trace(
        f"path: {file_path}\n"
        f"host: {host}\n"
        f"port: {port}\n"
        f"username: {username}\n"
        f"password: {password}\n"
        f"dry_run: {dry_run}\n"
        f"upload_path: {upload_path}\n"
    )

    upload_file_ftp(
        path=file_path,
        host=host,
        port=port,
        username=username,
        password=password,
        dry_run=dry_run,
        upload_filename=upload_path,
    )
