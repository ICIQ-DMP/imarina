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

import datetime
from pathlib import Path

from imarina_load_researchers.core.defines import (
    DATETIME_FORMAT,
    DATETIME_FORMAT_LENGTH,
    FILENAME_IMARINA_SUFFIX,
    MADRID_TZ,
)
from imarina_load_researchers.core.exceptions import NoExcelFilesFoundError
from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


def parse_datetime_from_filename(name: str, suffix: str) -> datetime.datetime | None:
    """Parse the `{DATETIME}__<FTP_FILENAME>`-encoded datetime out of a
    filename, or return None if it doesn't match that shape.

    Shared between `select_file_to_upload` (local files) and
    `select_latest_remote_file` (`core/sharepoint.py`, remote SharePoint
    folder listings) -- both need the exact same "pick the latest by
    filename-encoded datetime" rule (see CLAUDE.md's "What this does" section).
    """
    if not name.endswith(suffix):
        logger.debug(f"File does not end with {suffix}")
        return None

    datetime_part = name[0:DATETIME_FORMAT_LENGTH]

    try:
        # Filenames are stamped using NOW (core/defines.py), which is Madrid time.
        return datetime.datetime.strptime(datetime_part, DATETIME_FORMAT).replace(
            tzinfo=MADRID_TZ
        )
    except ValueError:
        logger.debug(f"Could not parse datetime: {datetime_part}, from file: {name}")
        return None


def select_file_to_upload(upload_dir: Path) -> Path:
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
        raise FileNotFoundError

    excel_files = list(upload_dir.glob("*.xlsx"))
    logger.debug(f"Excel files found: {len(excel_files)}")
    if not excel_files:
        raise NoExcelFilesFoundError

    dated_files: list[tuple[datetime.datetime, Path]] = []
    for file in excel_files:
        parsed_dt = parse_datetime_from_filename(file.name, FILENAME_IMARINA_SUFFIX)
        if parsed_dt is None:
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
