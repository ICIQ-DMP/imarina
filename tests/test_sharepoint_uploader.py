import pytest
from unittest.mock import patch, MagicMock

from imarina.core.sharepoint import get_site_id


class DummyTokenManager:
    def get_token(self):
        return "fake_token_123"


@patch("imarina.core.sharepoint.requests.get")
def test_get_site_id_success(mock_get):
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": "SITE12345"}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    token_manager = DummyTokenManager()  # execute function
    result = get_site_id(token_manager, "iciq.sharepoint.com", "my_site")

    mock_get.assert_called_once()  # verificacions
    called_url = mock_get.call_args[0][0]
    headers = mock_get.call_args[1]["headers"]

    assert (
        "https://graph.microsoft.com/v1.0/sites/iciq.sharepoint.com:/sites/my_site"
        in called_url
    )
    assert headers["Authorization"] == "Bearer fake_token_123"
    assert result == "SITE12345"


@patch("imarina.core.sharepoint.requests.get")
def test_get_site_id_http_error(mock_get):
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = Exception("Bad Request")
    mock_get.return_value = mock_response

    token_manager = DummyTokenManager()

    with pytest.raises(Exception, match="Bad Request"):
        get_site_id(token_manager, "iciq.sharepoint.com", "my_site")


def test_get_site_id():
    assert True
