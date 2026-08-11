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
    FILENAME_PREFIX,
    FILENAME_SUFFIX,
    MADRID_TZ,
)
from imarina_load_researchers.core.exceptions import NoExcelFilesFoundError
from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


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
        name = file.name

        if not name.startswith(FILENAME_PREFIX) or not name.endswith(FILENAME_SUFFIX):
            logger.debug(
                f"File does not start with {FILENAME_PREFIX} or end with {FILENAME_SUFFIX}"
            )
            continue

        datetime_part = name[len(FILENAME_PREFIX) : -len(FILENAME_SUFFIX)]

        try:
            # Filenames are stamped using NOW (core/defines.py), which is Madrid time.
            parsed_dt = datetime.datetime.strptime(
                datetime_part, DATETIME_FORMAT
            ).replace(tzinfo=MADRID_TZ)
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
