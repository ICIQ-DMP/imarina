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

import logging
from enum import StrEnum

from imarina_load_researchers.core.exceptions import UnknownLogLevelError


class LogLevel(StrEnum):
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
        if not value:
            return None
        norm = value.strip().lower()
        try:
            return cls(norm)
        except ValueError as exc:
            valid = ", ".join(v.value for v in cls)
            raise UnknownLogLevelError(value, valid) from exc

    @classmethod
    def get_default_log_level(cls) -> LogLevel:
        return LogLevel.INFO

    def to_logging_level(self) -> int:
        r = logging.INFO
        if self is LogLevel.TRACE:
            r = 0
        if self is LogLevel.DEBUG:
            r = logging.DEBUG
        if self is LogLevel.INFO:
            r = logging.INFO
        if self is LogLevel.WARNING:
            r = logging.WARNING
        if self is LogLevel.ERROR:
            r = logging.ERROR
        if self is LogLevel.QUIET:
            r = logging.CRITICAL + 10
        return r
