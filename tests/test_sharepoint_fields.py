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
from unittest.mock import MagicMock, patch

import pytest

from imarina_load_researchers.core.exceptions import NoExcelFilesFoundError
from imarina_load_researchers.core.sharepoint import (
    create_sharing_link,
    download_item_content,
    get_list_item_link_field,
    select_latest_remote_file,
    update_list_item_fields,
)


class DummyTokenManager:
    def get_token(self):
        return "fake_token_123"


# --- create_sharing_link ----------------------------------------------------


@patch("imarina_load_researchers.core.sharepoint.requests.post")
def test_create_sharing_link_success(mock_post):
    mock_response = MagicMock()
    mock_response.json.return_value = {
        "link": {"webUrl": "https://sharepoint.example/link"}
    }
    mock_response.raise_for_status.return_value = None
    mock_post.return_value = mock_response

    result = create_sharing_link(DummyTokenManager(), "DRIVE1", "ITEM1")

    mock_post.assert_called_once()
    called_url = mock_post.call_args[0][0]
    assert "drives/DRIVE1/items/ITEM1/createLink" in called_url
    assert mock_post.call_args[1]["json"] == {"type": "view", "scope": "organization"}
    assert result == "https://sharepoint.example/link"


# --- download_item_content ---------------------------------------------------


@patch("imarina_load_researchers.core.sharepoint.requests.get")
def test_download_item_content_success(mock_get, tmp_path):
    mock_response = MagicMock()
    mock_response.content = b"file-bytes"
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    destination = tmp_path / "out.xlsx"

    download_item_content(DummyTokenManager(), "DRIVE1", "ITEM1", destination)

    assert destination.read_bytes() == b"file-bytes"
    called_url = mock_get.call_args[0][0]
    assert "drives/DRIVE1/items/ITEM1/content" in called_url


# --- select_latest_remote_file ------------------------------------------------


@patch("imarina_load_researchers.core.sharepoint.requests.get")
def test_select_latest_remote_file_picks_newest_by_filename(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "value": [
            {
                "id": "OLD",
                "name": "2025-01-01_12-00-00__icl_ag_personal_12539.xlsx",
                "file": {"mimeType": "application/vnd.ms-excel"},
            },
            {
                "id": "NEW",
                "name": "2026-01-01_12-00-00__icl_ag_personal_12539.xlsx",
                "file": {"mimeType": "application/vnd.ms-excel"},
            },
            {"id": "NOTAFILE", "name": "somefolder", "folder": {}},
        ]
    }
    mock_get.return_value = mock_response

    result = select_latest_remote_file(DummyTokenManager(), "DRIVE1", Path("some/dir"))

    assert result.id == "NEW"
    assert result.name == "2026-01-01_12-00-00__icl_ag_personal_12539.xlsx"


@patch("imarina_load_researchers.core.sharepoint.requests.get")
def test_select_latest_remote_file_raises_when_empty(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"value": []}
    mock_get.return_value = mock_response

    with pytest.raises(NoExcelFilesFoundError):
        select_latest_remote_file(DummyTokenManager(), "DRIVE1", Path("some/dir"))


# --- update_list_item_fields / get_list_item_link_field ----------------------
#
# These resolve site/list from secrets internally (unlike the functions
# above, which take token_manager/drive_id directly), so read_secret and
# get_token_manager need mocking too, plus get_site_id's own requests.get
# call.


@patch("imarina_load_researchers.core.sharepoint.requests.patch")
@patch("imarina_load_researchers.core.sharepoint.requests.get")
@patch("imarina_load_researchers.core.sharepoint.read_secret")
@patch("imarina_load_researchers.core.sharepoint.get_token_manager")
def test_update_list_item_fields_success(
    mock_get_token_manager, mock_read_secret, mock_get, mock_patch
):
    mock_get_token_manager.return_value = DummyTokenManager()
    mock_read_secret.return_value = "dummy"

    site_response = MagicMock()
    site_response.json.return_value = {"id": "SITE12345"}
    site_response.raise_for_status.return_value = None
    mock_get.return_value = site_response

    patch_response = MagicMock()
    patch_response.raise_for_status.return_value = None
    mock_patch.return_value = patch_response

    update_list_item_fields("42", {"Workflow_x0020_State": "Preparing"})

    mock_patch.assert_called_once()
    called_url = mock_patch.call_args[0][0]
    assert "items/42/fields" in called_url
    assert mock_patch.call_args[1]["json"] == {"Workflow_x0020_State": "Preparing"}


@patch("imarina_load_researchers.core.sharepoint.requests.get")
@patch("imarina_load_researchers.core.sharepoint.read_secret")
@patch("imarina_load_researchers.core.sharepoint.get_token_manager")
def test_get_list_item_link_field_success(
    mock_get_token_manager, mock_read_secret, mock_get
):
    mock_get_token_manager.return_value = DummyTokenManager()
    mock_read_secret.return_value = "dummy"

    site_response = MagicMock()
    site_response.json.return_value = {"id": "SITE12345"}
    site_response.raise_for_status.return_value = None

    item_response = MagicMock()
    item_response.json.return_value = {
        "fields": {"SomeField": "https://sharepoint.example/output.xlsx"}
    }
    item_response.raise_for_status.return_value = None

    mock_get.side_effect = [site_response, item_response]

    result = get_list_item_link_field("42", "SomeField")

    assert result == "https://sharepoint.example/output.xlsx"


@patch("imarina_load_researchers.core.sharepoint.requests.get")
@patch("imarina_load_researchers.core.sharepoint.read_secret")
@patch("imarina_load_researchers.core.sharepoint.get_token_manager")
def test_get_list_item_link_field_missing_returns_none(
    mock_get_token_manager, mock_read_secret, mock_get
):
    mock_get_token_manager.return_value = DummyTokenManager()
    mock_read_secret.return_value = "dummy"

    site_response = MagicMock()
    site_response.json.return_value = {"id": "SITE12345"}
    site_response.raise_for_status.return_value = None

    item_response = MagicMock()
    item_response.json.return_value = {"fields": {}}
    item_response.raise_for_status.return_value = None

    mock_get.side_effect = [site_response, item_response]

    result = get_list_item_link_field("42", "SomeField")

    assert result is None
