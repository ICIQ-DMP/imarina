import typer

from imarina.core.log_utils import process_log_flags, configure_logging_from_settings

from imarina.core.log_utils import get_logger
from imarina.core.shared_options import (
    VerboseOpt,
    VeryVerboseOpt,
    QuietOpt,
    VeryQuietOpt,
    LogFileOpt,
)


def cli_global_callback(
    ctx: typer.Context,
    verbose: VerboseOpt = False,
    very_verbose: VeryVerboseOpt = False,
    quiet: QuietOpt = False,
    very_quiet: VeryQuietOpt = False,
    log_file: LogFileOpt = None,
) -> None:
    """
    Global option callback. Executed if no command is provided.
    """
    configure_logging_from_settings()
    logger = get_logger(__name__)

    cli_log_level, more_than_one_flag = process_log_flags(
        very_verbose=very_verbose, verbose=verbose, quiet=quiet, very_quiet=very_quiet
    )

    if more_than_one_flag:
        logger.warning(
            "More than one log level arguments was provided, the log level with more verbosity will be used."
        )

    configure_logging_from_settings(level=cli_log_level, log_file=log_file)
    logger = get_logger(__name__)

    logger.debug("Ended global callback")
