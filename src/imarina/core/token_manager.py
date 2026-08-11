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

import functools
import time

import requests

from imarina.core.exceptions import (
    MissingCredentialsError,
    SecretUnavailableError,
    TokenNotSetError,
    TokenRequestError,
)
from imarina.core.log_utils import get_logger
from imarina.core.secret import SecretName, read_secret

logger = get_logger(__name__)


class TokenManager:
    def __init__(
        self,
        tenant_id: str,
        client_id: str,
        client_secret: str,
        scope: str = "https://graph.microsoft.com/.default",
    ) -> None:
        self.token_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        )
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.access_token: str | None = None
        self.expires_at: float = 0

    def get_token(self) -> str:
        # return a valid token and if the token has expired or is about to expire , request a new token.
        if (
            self.access_token is None or time.time() >= self.expires_at - 300
        ):  # Refresh if less than 5 minutes remain
            self._refresh_token()
        if self.access_token is None:
            raise TokenNotSetError
        return self.access_token

    def _refresh_token(self) -> None:
        # request a new token for AZURE AD
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }
        response = requests.post(self.token_url, data=token_data, timeout=10)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise TokenRequestError(e, response.text) from e

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.expires_at = time.time() + token_data.get("expires_in", 3600)


def _create_token_manager() -> TokenManager:
    # read the secrets and create a unique instance of TokenManager.
    try:
        tenant_id = read_secret(SecretName.TENANT_ID)
        client_id = read_secret(SecretName.CLIENT_ID)
        client_secret = read_secret(SecretName.CLIENT_SECRET)
    except SecretUnavailableError as e:
        raise MissingCredentialsError from e
    return TokenManager(
        tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
    )


@functools.cache
def get_token_manager() -> TokenManager:
    manager = _create_token_manager()
    return manager
