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

import base64
import datetime
from dataclasses import dataclass
from http import HTTPStatus
from pathlib import Path
from typing import Any, cast
from urllib.parse import quote

import requests

from imarina_load_researchers.core.exceptions import (
    NoExcelFilesFoundError,
    SharePointError,
)
from imarina_load_researchers.core.file_select import parse_datetime_from_filename
from imarina_load_researchers.core.log_utils import get_logger
from imarina_load_researchers.core.secret import SecretName, read_secret
from imarina_load_researchers.core.sharepoint_fields import (
    FIELD_A3_EXCEL_INPUT_LINK,
    FIELD_IMARINA_EXCEL_INPUT_LINK,
)
from imarina_load_researchers.core.token_manager import TokenManager, get_token_manager

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
) -> str:
    """Upload a local file to SharePoint, returning the uploaded item's id
    (needed by callers that go on to generate a sharing link for it)."""

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
    return cast(str, response.json()["id"])


def download_item_content(
    token_manager: TokenManager, drive_id: str, item_id: str, destination: Path
) -> None:
    """Download a driveItem's content by id, writing it to `destination`."""
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/content"
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers, timeout=300)
    response.raise_for_status()
    with open(destination, "wb") as f:
        f.write(response.content)


def download_shared_link_content(
    token_manager: TokenManager, url: str, destination: Path
) -> None:
    """Download the file behind an MS List "sharing link" field value (the
    encoding Graph expects for its `/shares/u!{...}` endpoint), writing it to
    `destination`. Used for the two user-supplied input links (`download`)
    and for sourcing `publish`'s file from a request's output link.
    """
    encoded = base64.b64encode(url.encode()).decode()
    encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
    download_url = (
        f"https://graph.microsoft.com/v1.0/shares/u!{encoded}/driveItem/content"
    )
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(
        download_url, headers=headers, allow_redirects=True, timeout=300
    )
    response.raise_for_status()
    with open(destination, "wb") as f:
        f.write(response.content)


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
        try:
            download_item_content(
                token_manager, drive_id, remote_file["id"], local_destiny_folder / name
            )
            logger.debug(f"{name} saved successfully.")
        except requests.exceptions.HTTPError:
            logger.exception(f"Error downloading {name}")


def _resolve_site_and_list() -> tuple[str, str]:
    """Return (site_id, list_name), resolved from secrets. Shared by every
    function that reads or writes an MS List item."""
    token_manager = get_token_manager()
    sharepoint_domain = read_secret(SecretName.SHAREPOINT_DOMAIN)
    site_name = read_secret(SecretName.SITE_NAME)
    list_name = read_secret(SecretName.LIST_NAME)
    site_id = get_site_id(token_manager, sharepoint_domain, site_name)
    return site_id, list_name


def _get_list_item_fields(operation_id: str) -> dict[str, Any]:
    """GET the `fields` object of an MS List item by its id."""
    token_manager = get_token_manager()
    site_id, list_name = _resolve_site_and_list()

    list_url = (
        f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{quote(list_name, safe='')}/items/"
        f"{operation_id}?$expand=fields&$select=fields"
    )
    list_resp = requests.get(
        list_url,
        headers={"Authorization": f"Bearer {token_manager.get_token()}"},
        timeout=60,
    )
    list_resp.raise_for_status()

    return cast(dict[str, Any], list_resp.json().get("fields", {}))


def get_parameters_list(operation_id: str) -> tuple[str | None, str | None]:
    fields = _get_list_item_fields(operation_id)

    return fields.get(FIELD_A3_EXCEL_INPUT_LINK), fields.get(
        FIELD_IMARINA_EXCEL_INPUT_LINK
    )


def get_list_item_link_field(operation_id: str, field_name: str) -> str | None:
    """Read a single Text-type link field off an MS List item, or None if
    that field isn't set. Used by `publish` to source its file from the
    request's output-link field when given an ID (STEPS.md)."""
    return cast(str | None, _get_list_item_fields(operation_id).get(field_name))


def update_list_item_fields(operation_id: str, fields: dict[str, str]) -> None:
    """PATCH one or more fields on an MS List item.

    Graph's `/fields` sub-resource takes the field dict directly as the PATCH
    body (unlike `_get_list_item_fields`'s GET, which reads the whole item and
    pulls a `fields` object back out of the response).
    """
    token_manager = get_token_manager()
    site_id, list_name = _resolve_site_and_list()

    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_name}/items/{operation_id}/fields"
    response = requests.patch(
        url,
        headers={
            "Authorization": f"Bearer {token_manager.get_token()}",
            "Content-Type": "application/json",
        },
        json=fields,
        timeout=60,
    )
    response.raise_for_status()


def create_sharing_link(
    token_manager: TokenManager, drive_id: str, item_id: str
) -> str:
    """Create an organization-scoped, view-only sharing link for a SharePoint
    driveItem. Scope is deliberately "organization", not "anonymous" -- these
    links point at personnel data (STEPS.md's GDPR section)."""
    url = (
        f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{item_id}/createLink"
    )
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.post(
        url,
        headers=headers,
        json={"type": "view", "scope": "organization"},
        timeout=60,
    )
    response.raise_for_status()
    return cast(str, response.json()["link"]["webUrl"])


@dataclass(frozen=True)
class RemoteFile:
    id: str
    name: str


def select_latest_remote_file(
    token_manager: TokenManager, drive_id: str, remote_folder: Path, suffix: str
) -> RemoteFile:
    """List `remote_folder`'s children and pick the latest .xlsx by the
    filename-encoded datetime (STEPS.md: "the last of a group of files will
    always be deduced from the name of the file"). Remote counterpart of
    `select_file_to_upload` (core/file_select.py), which does the same thing
    against local files -- unlike that function, there is no modification-time
    fallback here: STEPS.md's rule for remote folders is filename-datetime
    only, and a SharePoint item's `lastModifiedDateTime` doesn't carry the
    same "file was produced at" meaning local mtime does for the local
    fallback.
    """
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_folder}:/children"
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers, timeout=30)
    if response.status_code != HTTPStatus.OK:
        raise SharePointError(response.status_code, response.text)

    items = response.json().get("value", [])
    excel_files = [f for f in items if f.get("file") and f["name"].endswith(".xlsx")]
    if not excel_files:
        raise NoExcelFilesFoundError

    dated_files: list[tuple[datetime.datetime, dict[str, Any]]] = []
    for item in excel_files:
        parsed_dt = parse_datetime_from_filename(item["name"], suffix)
        if parsed_dt is not None:
            dated_files.append((parsed_dt, item))

    if not dated_files:
        raise NoExcelFilesFoundError

    dated_files.sort(key=lambda x: x[0], reverse=True)
    chosen = dated_files[0][1]
    return RemoteFile(id=chosen["id"], name=chosen["name"])
