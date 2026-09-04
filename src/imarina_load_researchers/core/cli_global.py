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

import typer

from imarina_load_researchers.core.defines import DEFAULT_LOG_PATH
from imarina_load_researchers.core.exceptions import SecretUnavailableError
from imarina_load_researchers.core.log_utils import (
    configure_logging_from_settings,
    get_logger,
    process_log_flags,
)
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.shared_options import (
    LogFileOpt,
    QuietOpt,
    VerboseOpt,
    VeryQuietOpt,
    VeryVerboseOpt,
)


def _available_secrets_for_redaction() -> list[str]:
    """Best-effort collection of configured secrets, for log redaction only.

    A secret that isn't configured on this machine can't leak into logs, so
    it's simply omitted from the redaction list rather than treated as fatal
    — most commands (e.g. `build`) don't touch most secrets at all.
    """
    logger = get_logger(__name__)
    secrets = []
    for key in SecretName:
        try:
            secrets.append(read_secret(key))
        except SecretUnavailableError:
            logger.debug(f"Secret '{key}' unavailable; skipping it for log redaction.")
    return secrets


def cli_global_callback(  # noqa: PLR0913, PLR0917
    ctx: typer.Context,
    verbose: VerboseOpt = False,
    very_verbose: VeryVerboseOpt = False,
    quiet: QuietOpt = False,
    very_quiet: VeryQuietOpt = False,
    log_file: LogFileOpt = DEFAULT_LOG_PATH,
) -> None:
    """
    Global option callback. Executed if no command is provided.
    """
    # configure_logging_from_settings()
    logger = get_logger(__name__)

    cli_log_level, more_than_one_flag = process_log_flags(
        very_verbose=very_verbose, verbose=verbose, quiet=quiet, very_quiet=very_quiet
    )

    if more_than_one_flag:
        logger.warning(
            "More than one log level arguments was provided, the log level with more verbosity will be used."
        )

    configure_logging_from_settings(
        level=cli_log_level,
        log_file=log_file,
        secrets=_available_secrets_for_redaction(),
    )
    logger = get_logger(__name__)

    logger.debug("Ended global callback")
