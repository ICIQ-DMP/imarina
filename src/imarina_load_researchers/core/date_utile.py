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
from typing import Any

import pandas as pd

from imarina_load_researchers.core.defines import (
    DATE_FORMAT,
    MADRID_TZ,
    PERMANENT_CONTRACT_DATE,
)
from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


def sanitize_date(date_dirty: Any) -> datetime.datetime:
    """
    Normalizes a raw Excel cell value into a Madrid-tz-aware datetime.

    Handles the value shapes pandas/openpyxl can hand back for a date cell:
    a `pandas.Timestamp` or `datetime.datetime` (tz-aware or naive), `pd.NaT`,
    a `dd/mm/yyyy`-formatted string, an empty/`NaN` float cell, or `None`.
    A missing/empty date is treated as a permanent contract, per
    `core/defines.PERMANENT_CONTRACT_DATE`.

    Args:
        date_dirty (Any): The raw cell value to sanitize.

    Returns:
        datetime.datetime: A timezone-aware datetime pinned to `MADRID_TZ`.

    Raises:
        ValueError: If `date_dirty` is of a type this function doesn't know
            how to interpret.
    """
    if isinstance(date_dirty, pd.Timestamp) or type(date_dirty) is datetime.datetime:
        # Excel stores no timezone; these values are Madrid wall-clock times,
        # same as the string-parsed branch below and PERMANENT_CONTRACT_DATE
        # (core/defines.py), which callers compare/subtract this against.
        if date_dirty.tzinfo is None:
            return date_dirty.replace(tzinfo=MADRID_TZ)
        return date_dirty
    elif date_dirty is pd.NaT:
        return PERMANENT_CONTRACT_DATE
    elif isinstance(date_dirty, str):
        return datetime.datetime.strptime(date_dirty.strip("'"), "%d/%m/%Y").replace(
            tzinfo=MADRID_TZ
        )
    elif isinstance(date_dirty, float) or date_dirty is None:
        return PERMANENT_CONTRACT_DATE
    else:
        raise ValueError(
            "Unknown type for date to sanitize: "
            + str(type(date_dirty))
            + " value is: "
            + str(date_dirty)
        )


def unparse_date(date: datetime.datetime | None) -> str:
    """
    Formats a datetime back into the output spreadsheet's date string format.

    Args:
        date (datetime.datetime | None): The date to format, or `None`.

    Returns:
        str: `date` formatted per `core/defines.DATE_FORMAT`, or `""` if
            `date` is `None`.
    """
    if date is None:
        return ""
    else:
        return date.strftime(DATE_FORMAT)
