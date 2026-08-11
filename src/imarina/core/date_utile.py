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

import datetime
from typing import Any

import pandas as pd

from imarina.core.defines import DATE_FORMAT, MADRID_TZ, PERMANENT_CONTRACT_DATE
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def sanitize_date(date_dirty: Any) -> datetime.datetime:
    if isinstance(date_dirty, pd.Timestamp) or type(date_dirty) is datetime.datetime:
        # Excel stores no timezone; these values are Madrid wall-clock times,
        # same as the string-parsed branch below and PERMANENT_CONTRACT_DATE
        # (core/defines.py), which callers compare/subtract this against.
        if date_dirty.tzinfo is None:
            return date_dirty.replace(tzinfo=MADRID_TZ)
        return date_dirty
    elif type(date_dirty) is pd.isna(date_dirty):
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
    if date is None:
        return ""
    else:
        return date.strftime(DATE_FORMAT)
