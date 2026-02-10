import datetime

import pandas as pd

from imarina.core.defines import DATE_FORMAT
from imarina.core.log_utils import get_logger
from typing import Any, Optional
logger = get_logger(__name__)


def sanitize_date(date_dirty: Any) -> Optional[datetime.datetime]:
    if type(date_dirty) is pd._libs.tslibs.timestamps.Timestamp:
        return date_dirty
    elif type(date_dirty) is datetime.datetime:
        return date_dirty
    elif type(date_dirty) is pd._libs.tslibs.nattype.NaTType:
        return None
    elif isinstance(date_dirty, str):
        return datetime.datetime.strptime(date_dirty.strip("'"), "%d/%m/%Y")
    elif isinstance(date_dirty, float):
        return None
    elif date_dirty is None:
        return None
    else:
        raise ValueError(
            "Unknown type for date to sanitize: "
            + str(type(date_dirty))
            + " value is: "
            + str(date_dirty)
        )


def unparse_date(date: datetime.datetime) -> Any:
    if date is None:
        return ""
    else:
        return date.strftime(DATE_FORMAT)
