import logging
from pathlib import Path
from typing import Optional, Any, cast
from rich.logging import RichHandler

from imarina.core.defines import DATE_FORMAT, LogLevel, get_default_log_path

# ---- extend the logging module with TRACE
TRACE_LEVEL_NUM = 1
logging.addLevelName(TRACE_LEVEL_NUM, "TRACE")
MESSAGE_FORMAT = "%(asctime)s | %(name)s | %(message)s"


class ExtendedLogger(logging.Logger):
    def trace(self: logging.Logger, message: str, *args: Any, **kwargs: Any) -> None:
        self._log(TRACE_LEVEL_NUM, message, args, **kwargs)


# Tell the logging system to use your new class
logging.setLoggerClass(ExtendedLogger)


class SecretsFilter(logging.Filter):
    def __init__(self, secrets: list[str] | None):
        super().__init__()
        self.secrets: list[str] = secrets or []

    def filter(self, record: logging.LogRecord) -> bool:
        if not self.secrets:
            return True

        if isinstance(record.msg, str):
            for secret in self.secrets:
                if secret and secret in record.msg:
                    record.msg = record.msg.replace(secret, "*****")

        return True


def setup_logging(
    level: Optional[int | None],
    log_file: Optional[str | Path] = None,
    secrets: list[str] | None = None,
) -> None:
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
    level: Optional[LogLevel] = None,
    log_file: Optional[Path] = None,
    secrets: Optional[list[str]] = None,
) -> None:
    if log_file is None:
        log_file = get_default_log_path()

    if level is None:
        level = LogLevel.get_default_log_level()

    setup_logging(
        level=level.to_logging_level(),
        log_file=log_file,
        secrets=secrets,
    )  # Preventive creation of log for logging the loading of settings
