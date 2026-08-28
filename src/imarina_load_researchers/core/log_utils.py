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
from pathlib import Path
from typing import Any, cast

from rich.logging import RichHandler

from imarina_load_researchers.core.defines import DATE_FORMAT, DEFAULT_LOG_PATH
from imarina_load_researchers.core.log_level import LogLevel

# ---- extend the logging module with TRACE
TRACE_LEVEL_NUM = 1
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
MESSAGE_FORMAT = "%(asctime)s | %(name)s | %(message)s"


class ExtendedLogger(logging.Logger):
    """A `logging.Logger` with an added `trace()` method, for the custom
    TRACE level (`TRACE_LEVEL_NUM`, below `DEBUG`)."""

    def trace(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
        """
        Logs `message` at the custom TRACE level (below `DEBUG`).

        Args:
            message (str): The message to log, with `%`-style placeholders.
            *args (Any): Values for `message`'s `%`-style placeholders.
            **kwargs (Any): Forwarded to the underlying `Logger._log` call.
        """
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


# Tell the logging system to use your new class
logging.setLoggerClass(ExtendedLogger)


class SecretsFilter(logging.Filter):
    """A `logging.Filter` that redacts known secret values out of log
    records before they reach a handler."""

    def __init__(self, secrets: list[str] | None):
        """
        Args:
            secrets (list[str] | None): Secret values to redact from every
                log record's message, or `None`/`[]` to redact nothing.
        """
        super().__init__()
        self.secrets: list[str] = secrets or []

    def filter(self, record: logging.LogRecord) -> bool:
        """
        Replaces any occurrence of a known secret in `record.msg` with `*****`.

        Args:
            record (logging.LogRecord): The record to redact, mutated in place.

        Returns:
            bool: Always `True` - this filter only redacts, it never drops records.
        """
        if not self.secrets:
            return True

        if isinstance(record.msg, str):
            for secret in self.secrets:
                if secret and secret in record.msg:
                    record.msg = record.msg.replace(secret, "*****")

        return True


def setup_logging(
    level: int | None,
    log_file: str | Path | None = None,
    secrets: list[str] | None = None,
) -> None:
    """
    Configures the root logger with a Rich console handler and, optionally,
    a file handler - both filtered through `SecretsFilter`.

    Args:
        level (int | None): stdlib `logging` level to use for every handler;
            defaults to `logging.INFO` if `None`.
        log_file (str | Path | None): If given, also log to this file
            (parent directories are created as needed).
        secrets (list[str] | None): Secret values to redact from every log
            record via `SecretsFilter`.
    """
    # Default level is INFO
    if level is None:
        level = logging.INFO

    handlers: list[logging.Handler] = []
    secrets_filter = SecretsFilter(secrets)

    # ---- console (Rich)
    console = RichHandler(
        rich_tracebacks=True,
        markup=True,
        show_time=False,
        show_level=True,
        show_path=False,
    )
    common_formatter = logging.Formatter(MESSAGE_FORMAT, DATE_FORMAT)
    console.setLevel(level)
    console.setFormatter(common_formatter)
    console.addFilter(secrets_filter)
    handlers.append(console)

    if log_file:
        path = Path(log_file)
        path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(path, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(common_formatter)
        file_handler.addFilter(secrets_filter)
        handlers.append(file_handler)

    logging.basicConfig(
        level=level,  # root captures everything
        handlers=handlers,
        format=MESSAGE_FORMAT,
        force=True,
    )


def obfuscate_text(text: str | None) -> str:
    """
    Masks a piece of sensitive text (e.g. a secret) for safe logging.

    Args:
        text (str | None): The value to mask.

    Returns:
        str: `"*****"` if `text` has a value, `"None"` if `text` is `None`.
    """
    if text is None:
        return str(text)
    else:
        return "*****"


def get_logger(name: str) -> ExtendedLogger:
    """Return a logger with trace() method available."""
    return cast(ExtendedLogger, logging.getLogger(name))


def process_log_flags(
    very_verbose: bool, verbose: bool, quiet: bool, very_quiet: bool
) -> tuple[LogLevel | None, bool]:
    """
    Resolves the CLI's mutually-exclusive verbosity flags into a `LogLevel`.

    Args:
        very_verbose (bool): `--very-verbose`/TRACE flag.
        verbose (bool): `--verbose`/DEBUG flag.
        quiet (bool): `--quiet`/WARNING flag.
        very_quiet (bool): `--very-quiet`/QUIET flag.

    Returns:
        tuple[LogLevel | None, bool]: The resolved `LogLevel` (`None` if no
            flag was set, so the caller should fall back to its own default),
            and whether more than one of the four flags was set at once.
    """
    more_than_one_flag = False
    flag_counter = 0
    for flag in (very_verbose, verbose, quiet, very_quiet):
        if flag:
            flag_counter += 1
    if flag_counter > 1:
        more_than_one_flag = True

    if very_verbose:
        return LogLevel.TRACE, more_than_one_flag
    elif verbose:
        return LogLevel.DEBUG, more_than_one_flag
    elif quiet:
        return LogLevel.WARNING, more_than_one_flag
    elif very_quiet:
        return LogLevel.QUIET, more_than_one_flag
    else:
        return None, more_than_one_flag


def configure_logging_from_settings(
    level: LogLevel | None = None,
    log_file: Path = DEFAULT_LOG_PATH,
    secrets: list[str] | None = None,
) -> None:
    """
    Sets up logging from a resolved `LogLevel`, defaulting the level if unset.

    Thin wrapper around `setup_logging` that converts a logical `LogLevel`
    into the stdlib level it expects; this is the entry point called from
    `cli_global_callback` for every CLI invocation.

    Args:
        level (LogLevel | None): The logical log level to use; defaults to
            `LogLevel.get_default_log_level()` if `None`.
        log_file (Path): Path to also log to, forwarded to `setup_logging`.
        secrets (list[str] | None): Secret values to redact from log output,
            forwarded to `setup_logging`.
    """
    if level is None:
        level = LogLevel.get_default_log_level()

    setup_logging(
        level=level.to_logging_level(),
        log_file=log_file,
        secrets=secrets,
    )  # Preventive creation of log for logging the loading of settings
