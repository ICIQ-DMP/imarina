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

from pathlib import Path

from imarina.core.secret_name import SecretName


class NoExcelFilesFoundError(FileNotFoundError):
    def __init__(self) -> None:
        super().__init__("No Excel files found")


class EnvVarMissingError(KeyError):
    def __init__(self, var_name: str) -> None:
        super().__init__(f"The environment variable '{var_name}' does not exist.")


class EnvVarEmptyError(ValueError):
    def __init__(self, var_name: str) -> None:
        super().__init__(f"The environment variable '{var_name}' is empty.")


class FileContentEmptyError(ValueError):
    def __init__(self, file_path: str | Path) -> None:
        super().__init__(f"The file '{file_path}' is empty.")


class FileMissingError(FileNotFoundError):
    def __init__(self, file_path: str | Path) -> None:
        super().__init__(f"The file '{file_path}' does not exist.")


class FileUnreadableError(PermissionError):
    def __init__(self, file_path: str | Path) -> None:
        super().__init__(f"The file '{file_path}' cannot be read. Check permissions.")


class SftpSessionError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Failed to open SFTP session: from_transport returned None.")


class UnknownLogLevelError(ValueError):
    def __init__(self, value: str, valid: str) -> None:
        super().__init__(f"Unknown log level '{value}'. Valid: {valid}")


class SecretUnavailableError(RuntimeError):
    def __init__(self, secret_name: SecretName) -> None:
        super().__init__(f"Could not read {secret_name} from any source")


class SharePointError(Exception):
    """Raised when a SharePoint Graph API call fails or returns unexpected data."""

    def __init__(self, status_code: int, response_text: str) -> None:
        super().__init__(f"Error listing SharePoint: {status_code} - {response_text}")


class TokenNotSetError(RuntimeError):
    def __init__(self) -> None:
        super().__init__("Token refresh did not set an access token.")


class TokenRequestError(RuntimeError):
    def __init__(self, error: Exception, response_text: str) -> None:
        super().__init__(
            f"Error requesting access token: {error}\nResponse: {response_text}"
        )


class MissingCredentialsError(ValueError):
    def __init__(self) -> None:
        super().__init__(
            "Missing values for TENANT_ID, CLIENT_ID or CLIENT_SECRET in secrets."
        )


class TokenManagerUnavailableError(RuntimeError):
    def __init__(self) -> None:
        super().__init__(
            "No TokenManager available (running under GITHUB_ACTIONS with no "
            "credentials configured)."
        )


class VaultCredentialMissingError(KeyError):
    def __init__(self, name: str) -> None:
        super().__init__(
            f"Vault credential '{name}' not found in secrets or environment"
        )


class VaultMappingMissingError(KeyError):
    def __init__(self, secret_name: SecretName) -> None:
        super().__init__(f"No vault mapping defined for secret '{secret_name}'")


class VaultFieldMissingError(KeyError):
    def __init__(self, field: str, vault_path: str) -> None:
        super().__init__(f"Field '{field}' not found at vault path '{vault_path}'")


class VaultSecretEmptyError(ValueError):
    def __init__(self, secret_name: SecretName, field: str) -> None:
        super().__init__(f"Vault secret '{secret_name}' (field '{field}') is empty")
