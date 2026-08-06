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

# import sys
import os
from collections.abc import Callable
from enum import StrEnum

import requests

from imarina.core.filesystem import read_env_var, read_file_content
from imarina.core.log_utils import get_logger
from imarina.core.vault import read_vault_secret

logger = get_logger(__name__)


class SecretName(StrEnum):
    """All secret names that can be resolved via read_secret()."""

    CLIENT_ID = "CLIENT_ID"
    CLIENT_NAME = "CLIENT_NAME"
    CLIENT_SECRET = "CLIENT_SECRET"
    DRIVE_ID = "DRIVE_ID"
    SHAREPOINT_DOMAIN = "SHAREPOINT_DOMAIN"
    SITE_NAME = "SITE_NAME"
    TENANT_ID = "TENANT_ID"
    LIST_NAME = "LIST_NAME"

    FTP_HOST = "FTP_HOST"
    FTP_PASSWORD = "FTP_PASSWORD"
    FTP_PORT = "FTP_PORT"
    FTP_UPLOAD_FILENAME = "FTP_UPLOAD_FILENAME"
    FTP_USER = "FTP_USER"

    SSH_HOST = "SSH_HOST"
    SSH_PASSWORD = "SSH_PASSWORD"
    SSH_USERNAME = "SSH_USERNAME"

    JENKINS_PASSWORD = "JENKINS_PASSWORD"
    JENKINS_USERNAME = "JENKINS_USERNAME"

    SMTP_USERNAME = "SMTP_USERNAME"
    SMTP_PASSWORD = "SMTP_PASSWORD"
    SMTP_HOST = "SMTP_HOST"
    SMTP_PORT = "SMTP_PORT"


def read_secret(secret_name: SecretName) -> str:
    """Retrieve a secret from predefined sources in order of priority."""
    sources: list[Callable[[], str]] = [
        lambda: read_file_content(f"/run/secrets/{secret_name}"),
        lambda: read_file_content(
            os.path.join(
                os.path.dirname(
                    os.path.dirname(
                        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                    )
                ),
                "secrets",
                secret_name,
            )
        ),
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
