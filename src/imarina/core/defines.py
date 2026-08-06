import datetime
import logging
import os
import pathlib
from enum import Enum

DATETIME_FORMAT = "%Y-%m-%d_%H-%M-%S"
NOW_DATA = datetime.datetime.now()
NOW = NOW_DATA.strftime(DATETIME_FORMAT)

PROJECT_DIR = pathlib.Path.cwd()
OUTPUT_DIR = PROJECT_DIR / "output"
date_str = "31/12/2099"
DATE_FORMAT = "%d/%m/%Y"
PERMANENT_CONTRACT_DATE = datetime.datetime.strptime(date_str, "%d/%m/%Y")
ICIQ_WEBPAGE = "https://iciq.org/"

FILENAME_PREFIX = "iMarina_upload_"
FILENAME_SUFFIX = ".xlsx"
FTP_EXCEL_FILE_DATE_FORMAT = "%y%m%d"

# Single source of truth for the input files `build` needs and `download` must
# provide, under these exact names, in the same flat directory (default:
# PROJECT_DIR / "input"). Keyed by role so callers can refer to files by
# meaning rather than repeating literal filenames.
REQUIRED_INPUT_FILES = {
    "a3": "A3.xlsx",
    "imarina": "iMarina.xlsx",
    "countries": "countries.xlsx",
    "jobs": "Job_Descriptions.xlsx",
    "personal_web": "Personal_web.xlsx",
    "unit_group": "unit_group.xlsx",
    "unit_type": "unit_type.xlsx",
    "job_description_entity": "job_description_entity.xlsx",
}


class LogLevel(str, Enum):
    """
    Logical log levels for the CLI.

    Includes a custom TRACE (more verbose than DEBUG) and QUIET
    (suppresses all output beyond CRITICAL).
    """

    TRACE = "trace"
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    QUIET = "quiet"

    @classmethod
    def parse(cls, value: str | None) -> LogLevel | None:
        """Parse case-insensitively; returns None if value is falsy."""
        print("Executing function parse from LogLevel")
        if not value:
            return None
        norm = value.strip().lower()
        try:
            return cls(norm)
        except ValueError as exc:
            valid = ", ".join(v.value for v in cls)
            raise ValueError(f"Unknown log level '{value}'. Valid: {valid}") from exc

    @classmethod
    def get_default_log_level(cls) -> LogLevel:
        return LogLevel.INFO

    def to_logging_level(self) -> int:
        if self is LogLevel.TRACE:
            return 0
        if self is LogLevel.DEBUG:
            return logging.DEBUG
        if self is LogLevel.INFO:
            return logging.INFO
        if self is LogLevel.WARNING:
            return logging.WARNING
        if self is LogLevel.ERROR:
            return logging.ERROR
        if self is LogLevel.QUIET:
            return logging.CRITICAL + 10
        # Fallback
        return logging.INFO


def get_default_log_path() -> pathlib.Path:
    return pathlib.Path(str(os.path.join(PROJECT_DIR, "logs", NOW + ".log")))
