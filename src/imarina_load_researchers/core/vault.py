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

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

import requests
import urllib3

from imarina_load_researchers.core.defines import PROJECT_DIR
from imarina_load_researchers.core.exceptions import (
    VaultCredentialMissingError,
    VaultFieldMissingError,
    VaultMappingMissingError,
    VaultSecretEmptyError,
)
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.secret_name import SecretName

logger = get_logger(__name__)

_VAULT_BASE_PATH = "secret/data/imarina"

# Maps app-level secret names to (vault subpath, vault field key)
_SECRET_MAP: dict[SecretName, tuple[str, str]] = {
    # sharepoint (secret/imarina/runtime/sharepoint)
    SecretName.CLIENT_ID: ("runtime/sharepoint", "client_id"),
    SecretName.CLIENT_NAME: ("runtime/sharepoint", "client_name"),
    SecretName.CLIENT_SECRET: ("runtime/sharepoint", "client_secret"),
    SecretName.DRIVE_ID: ("runtime/sharepoint", "drive_id"),
    SecretName.SHAREPOINT_DOMAIN: ("runtime/sharepoint", "domain"),
    SecretName.SITE_NAME: ("runtime/sharepoint", "site_name"),
    SecretName.TENANT_ID: ("runtime/sharepoint", "tenant_id"),
    SecretName.LIST_NAME: ("runtime/sharepoint", "list_name"),
    # ftp (secret/imarina/runtime/ftp)
    SecretName.FTP_HOST: ("runtime/ftp", "host"),
    SecretName.FTP_PASSWORD: ("runtime/ftp", "password"),
    SecretName.FTP_PORT: ("runtime/ftp", "port"),
    SecretName.FTP_USER: ("runtime/ftp", "user"),
    # smtp credentials (secret/imarina/runtime/smtp)
    SecretName.SMTP_USERNAME: ("runtime/smtp", "username"),
    SecretName.SMTP_PASSWORD: ("runtime/smtp", "password"),
    SecretName.SMTP_HOST: ("runtime/smtp", "host"),
    SecretName.SMTP_PORT: ("runtime/smtp", "port"),
}


def _read_credential(name: str) -> str:
    """Read a Vault connection credential from (in order):
    1. /run/secrets/<name>
    2. <project_root>/secrets/<name>
    3. environment variable
    """
    for path in (Path(f"/run/secrets/{name}"), PROJECT_DIR / "secrets" / name):
        if path.is_file():
            value = path.read_text().strip()
            if value:
                return value
    value = os.environ.get(name, "").strip()
    if value:
        return value
    raise VaultCredentialMissingError(name)


class _VaultClient:
    """A minimal HashiCorp Vault client for this app's KV v2 secrets,
    handling authentication and per-subpath response caching."""

    def __init__(self) -> None:
        """Sets up the HTTP session, configuring TLS verification from
        `VAULT_CACERT`/`VAULT_SKIP_VERIFY` if either credential is available."""
        self._token: str | None = None
        self._cache: dict[str, dict[str, Any]] = {}  # subpath -> {field: value}

        self._session = requests.Session()
        try:
            ca_cert = _read_credential("VAULT_CACERT")
            self._session.verify = ca_cert
        except KeyError:
            try:
                skip = _read_credential("VAULT_SKIP_VERIFY")
                if skip.lower() in ("1", "true", "yes"):
                    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
                    self._session.verify = False
            except KeyError:
                pass  # Use the default CA bundle

    def _authenticate(self) -> None:
        """
        Obtains a Vault token, preferring a pre-issued `VAULT_TOKEN` and
        falling back to AppRole login (`VAULT_ROLE_ID` + `VAULT_SECRET_ID`).

        Raises:
            KeyError: If neither `VAULT_TOKEN` nor the AppRole credentials
                (including `VAULT_ADDR`) can be resolved.
            requests.HTTPError: If the AppRole login request fails.
        """
        # 1. Try a pre-issued Vault token.
        try:
            self._token = _read_credential("VAULT_TOKEN")
        except KeyError:
            pass
        else:
            return

        # 2. Try AppRole (VAULT_ROLE_ID + VAULT_SECRET_ID).
        role_id = _read_credential("VAULT_ROLE_ID")
        secret_id = _read_credential("VAULT_SECRET_ID")
        vault_addr = _read_credential("VAULT_ADDR")
        resp = self._session.post(
            f"{vault_addr}/v1/auth/approle/login",
            json={"role_id": role_id, "secret_id": secret_id},
            timeout=10,
        )
        resp.raise_for_status()
        self._token = resp.json()["auth"]["client_token"]

    def _fetch_subpath(self, subpath: str) -> dict[str, Any]:
        """
        Reads a KV v2 secret's data at `subpath`, authenticating if needed.

        Results are cached per subpath for the lifetime of this client, so a
        secret with multiple fields is only ever fetched from Vault once.

        Args:
            subpath (str): Path under `_VAULT_BASE_PATH` to read.

        Returns:
            dict[str, Any]: The secret's `{field: value}` data.

        Raises:
            requests.HTTPError: If the Vault request fails.
        """
        if subpath in self._cache:
            return self._cache[subpath]

        if self._token is None:
            self._authenticate()

        vault_addr = _read_credential("VAULT_ADDR")
        url = f"{vault_addr}/v1/{_VAULT_BASE_PATH}/{subpath}"
        resp = self._session.get(
            url,
            headers={"X-Vault-Token": self._token},
            timeout=10,
        )
        resp.raise_for_status()
        data: dict[str, Any] = resp.json()["data"]["data"]
        self._cache[subpath] = data
        return data

    def read_secret(self, secret_name: SecretName) -> str:
        """
        Resolves an app-level `SecretName` to its value in Vault.

        Args:
            secret_name (SecretName): The secret to resolve.

        Returns:
            str: The secret's value.

        Raises:
            KeyError: If `secret_name` has no `_SECRET_MAP` entry, or the
                mapped field is absent from the Vault secret's data.
            ValueError: If the field exists but is empty.
        """
        if secret_name not in _SECRET_MAP:
            raise VaultMappingMissingError(secret_name)
        subpath, field = _SECRET_MAP[secret_name]
        data = self._fetch_subpath(subpath)
        if field not in data:
            raise VaultFieldMissingError(field, f"{_VAULT_BASE_PATH}/{subpath}")
        value = data[field]
        if value is None or str(value).strip() == "":
            raise VaultSecretEmptyError(secret_name, field)
        return str(value)


@lru_cache(maxsize=1)
def _get_client() -> _VaultClient:
    """
    Returns the process-wide `_VaultClient` singleton, creating it on first call.

    Returns:
        _VaultClient: The cached client instance.
    """
    return _VaultClient()


def read_vault_secret(secret_name: SecretName) -> str:
    """Return the value of *secret_name* fetched from Vault.

    Raises KeyError  if the secret has no vault mapping or the field is absent.
    Raises ValueError if the field exists but is empty.
    Raises requests.HTTPError / ConnectionError on network / auth failures.
    """
    logger.debug(f"Requesting secret from Vault: {secret_name}")
    return _get_client().read_secret(secret_name)
