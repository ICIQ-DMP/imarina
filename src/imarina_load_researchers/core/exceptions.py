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

from pathlib import Path

from imarina_load_researchers.core.secret_name import SecretName


class NoExcelFilesFoundError(FileNotFoundError):
    """Raised when no Excel files are found where at least one was expected."""

    def __init__(self) -> None:
        super().__init__("No Excel files found")


class OutputLinkMissingError(ValueError):
    """Raised when `publish` is asked to resolve a file from an MS List item
    that has no "iMarina Excel output link" field set."""

    def __init__(self, operation_id: str) -> None:
        super().__init__(
            f"MS List item {operation_id} has no 'iMarina Excel output link' "
            "set to publish from."
        )


class EnvVarMissingError(KeyError):
    """Raised when a required environment variable is not set at all."""

    def __init__(self, var_name: str) -> None:
        super().__init__(f"The environment variable '{var_name}' does not exist.")


class EnvVarEmptyError(ValueError):
    """Raised when a required environment variable is set but its value is empty."""

    def __init__(self, var_name: str) -> None:
        super().__init__(f"The environment variable '{var_name}' is empty.")


class FileContentEmptyError(ValueError):
    """Raised when a file exists and is readable but has no content."""

    def __init__(self, file_path: str | Path) -> None:
        super().__init__(f"The file '{file_path}' is empty.")


class FileMissingError(FileNotFoundError):
    """Raised when an expected file does not exist at the given path."""

    def __init__(self, file_path: str | Path) -> None:
        super().__init__(f"The file '{file_path}' does not exist.")


class FileUnreadableError(PermissionError):
    """Raised when a file exists but cannot be opened due to file permissions."""

    def __init__(self, file_path: str | Path) -> None:
        super().__init__(f"The file '{file_path}' cannot be read. Check permissions.")


class SftpSessionError(RuntimeError):
    """Raised when opening an SFTP session over an existing transport fails."""

    def __init__(self) -> None:
        super().__init__("Failed to open SFTP session: from_transport returned None.")


class UnknownLogLevelError(ValueError):
    """Raised when a configured log level string doesn't match any known level."""

    def __init__(self, value: str, valid: str) -> None:
        super().__init__(f"Unknown log level '{value}'. Valid: {valid}")


class SecretUnavailableError(RuntimeError):
    """Raised when a secret could not be resolved from any of `read_secret`'s
    fallback sources (Docker secret, local file, environment variable, Vault)."""

    def __init__(self, secret_name: SecretName) -> None:
        super().__init__(f"Could not read {secret_name} from any source")


class SharePointError(Exception):
    """Raised when a SharePoint Graph API call fails or returns unexpected data."""

    def __init__(self, status_code: int, response_text: str) -> None:
        super().__init__(f"Error listing SharePoint: {status_code} - {response_text}")


class TokenNotSetError(RuntimeError):
    """Raised when a token refresh completes without ever setting an access token."""

    def __init__(self) -> None:
        super().__init__("Token refresh did not set an access token.")


class TokenRequestError(RuntimeError):
    """Raised when requesting an access token from the identity provider fails."""

    def __init__(self, error: Exception, response_text: str) -> None:
        super().__init__(
            f"Error requesting access token: {error}\nResponse: {response_text}"
        )


class MissingCredentialsError(ValueError):
    """Raised when TENANT_ID, CLIENT_ID or CLIENT_SECRET cannot be resolved
    from secrets."""

    def __init__(self) -> None:
        super().__init__(
            "Missing values for TENANT_ID, CLIENT_ID or CLIENT_SECRET in secrets."
        )


class VaultCredentialMissingError(KeyError):
    """Raised when a Vault-connection credential (e.g. the Vault token) is
    missing from both secrets and the environment."""

    def __init__(self, name: str) -> None:
        super().__init__(
            f"Vault credential '{name}' not found in secrets or environment"
        )


class VaultMappingMissingError(KeyError):
    """Raised when a `SecretName` has no entry in `vault.py`'s `_SECRET_MAP`,
    so the Vault fallback has no subpath/field to look it up under."""

    def __init__(self, secret_name: SecretName) -> None:
        super().__init__(f"No vault mapping defined for secret '{secret_name}'")


class VaultFieldMissingError(KeyError):
    """Raised when a Vault secret was found at its path but doesn't contain
    the expected field."""

    def __init__(self, field: str, vault_path: str) -> None:
        super().__init__(f"Field '{field}' not found at vault path '{vault_path}'")


class VaultSecretEmptyError(ValueError):
    """Raised when a Vault secret's field was found but its value is empty."""

    def __init__(self, secret_name: SecretName, field: str) -> None:
        super().__init__(f"Vault secret '{secret_name}' (field '{field}') is empty")
