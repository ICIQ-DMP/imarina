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

from http import HTTPStatus
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote

import requests

from imarina.core.exceptions import SharePointError
from imarina.core.log_utils import get_logger
from imarina.core.secret import SecretName, read_secret
from imarina.core.token_manager import TokenManager, get_token_manager

# Only re-exported (non-local) name needs listing here for mypy's strict-mode
# reexport check; functions defined in this module don't need it.
__all__ = [
    "download_files_in_folder_from_sharepoint",
    "get_parameters_list",
    "get_token_manager",
]

logger = get_logger(__name__)


def get_list_id(token_manager: TokenManager, site_id: str, list_name: str) -> str:
    """Return the GUID of the named SharePoint list.

    Args:
        token_manager: Authenticated token manager.
        site_id: SharePoint site identifier.
        list_name: Display name of the target list.

    Returns:
        The list's Graph API GUID string.
    """
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_name}"
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return cast(str, response.json()["id"])


def get_site_id(token_manager: TokenManager, domain: str, site_name: str) -> Any:
    url = f"https://graph.microsoft.com/v1.0/sites/{domain}:/sites/{site_name}"  # Obtain the ID of site from SharePoint
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()["id"]


def upload_file(
    token_manager: TokenManager,
    drive_id: str,
    target_folder: Path,
    local_file_path: Path,
) -> None:

    remote_path = target_folder / local_file_path.name
    logger.info(f"Uploading from local path {local_file_path} to {remote_path}")
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_path}:/content?%40microsoft.graph.conflictBehavior=replace"
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "Content-Type": "application/octet-stream",
    }
    try:
        with open(local_file_path, "rb") as f:

            response = requests.put(url, headers=headers, data=f, timeout=300)

        if response.status_code in (200, 201):
            logger.info(
                f"File '{local_file_path.name}' uploaded successfully to {remote_path}."
            )
        else:
            response.raise_for_status()
    except requests.exceptions.HTTPError:
        if response.status_code == HTTPStatus.NOT_FOUND:
            logger.exception(
                f"Destination folder does not exist ({remote_path}) in SharePoint."
            )
        else:
            logger.exception(f"HTTP error uploading '{local_file_path.name}'")
        raise
    except Exception:
        logger.exception(f"Unexpected error uploading '{local_file_path.name}'")
        raise

    logger.info("Upload done")


def download_files_in_folder_from_sharepoint(
    drive_id: str, local_destiny_folder: Path, remote_origin_folder: Path
) -> Any:
    token_manager = get_token_manager()

    local_destiny_folder.mkdir(parents=True, exist_ok=True)

    url_list = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_origin_folder}:/children"
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

    response = requests.get(url_list, headers=headers, timeout=30)

    if response.status_code != HTTPStatus.OK:
        raise SharePointError(response.status_code, response.text)

    items = response.json().get("value", [])
    files_to_download = [f for f in items if f.get("file")]

    if not files_to_download:
        logger.warning("No files to download in the SharePoint path.")
        return

    logger.info(f"Found {len(files_to_download)} files. Downloading...")

    for remote_file in files_to_download:
        name = remote_file["name"]

        url_download = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{remote_file['id']}/content"

        res_file = requests.get(url_download, headers=headers, timeout=300)

        if res_file.status_code == HTTPStatus.OK:
            with open(local_destiny_folder / name, "wb") as f:
                f.write(res_file.content)
            logger.debug(f"{name} saved successfully.")
        else:
            logger.error(f"Error downloading {name}: {res_file.status_code}")


def get_parameters_list(operation_id: str) -> tuple[str | None, str | None]:
    token_manager = get_token_manager()
    access_token = token_manager.get_token()

    sharepoint_domain = read_secret(SecretName.SHAREPOINT_DOMAIN)
    site_name = read_secret(SecretName.SITE_NAME)
    list_name = read_secret(SecretName.LIST_NAME)

    site_id = get_site_id(token_manager, sharepoint_domain, site_name)

    list_url = (
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{quote(list_name, safe='')}/items/"
        f"{operation_id}?$expand=fields&$select=fields"
    )
    list_resp = requests.get(
        list_url, headers={"Authorization": f"Bearer {access_token}"}, timeout=60
    )
    list_resp.raise_for_status()

    fields = list_resp.json().get("fields", {})

    a3_field = fields.get("A3_x0020_Excel_x0020_Link", {})
    imarina_field = fields.get("iMarina_x0020_Excel_x0020_Link", {})

    return a3_field.get("Url"), imarina_field.get("Url")
