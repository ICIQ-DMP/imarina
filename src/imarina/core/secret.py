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

from collections.abc import Callable

import requests

from imarina.core.defines import PROJECT_DIR
from imarina.core.filesystem import read_env_var, read_file_content
from imarina.core.log_utils import get_logger
from imarina.core.secret_name import SecretName
from imarina.core.vault import read_vault_secret

# Re-exported (non-local) name needed here for mypy's strict-mode reexport
# check, since callers do `from imarina.core.secret import SecretName`.
__all__ = ["SecretName", "read_secret"]

logger = get_logger(__name__)


def read_secret(secret_name: SecretName) -> str:
    """Retrieve a secret from predefined sources in order of priority."""
    sources: list[Callable[[], str]] = [
        lambda: read_file_content(f"/run/secrets/{secret_name}"),
        lambda: read_file_content(PROJECT_DIR / "secrets" / secret_name),
        lambda: read_env_var(secret_name),
        lambda: read_vault_secret(secret_name),
    ]

    # Each source signals "not available here" via one of these; anything else
    # (e.g. a programming bug) is left to propagate instead of being swallowed.
    # - read_file_content/read_file: FileNotFoundError, PermissionError (OSError)
    # - read_env_var: KeyError, ValueError
    # - read_vault_secret: KeyError, ValueError, requests.exceptions.RequestException
    expected_errors = (
        OSError,
        KeyError,
        ValueError,
        requests.exceptions.RequestException,
    )
    for source in sources:
        try:
            value = source()
            if value:
                return value
        except expected_errors as e:
            logger.debug(f"Secret source unavailable for '{secret_name}': {e}")
            continue
    raise RuntimeError(f"Could not read {secret_name} from any source")
