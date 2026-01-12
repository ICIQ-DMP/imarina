import time

import requests

from imarina.core.secret import read_secret
import os
from src.imarina.core.log_utils import get_logger

logger = get_logger(__name__)


class TokenManager:
    def __init__(
        self,
        tenant_id,
        client_id,
        client_secret,
        scope="https://graph.microsoft.com/.default",
    ):
        self.token_url = (
            f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
        )
        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.access_token = None
        self.expires_at = 0

    def get_token(self):
        # return a valid token and if the token has expired or is about to expire , request a new token.
        if (
            self.access_token is None or time.time() >= self.expires_at - 300
        ):  # Refresca si falten <5 minuts
            self._refresh_token()
        return self.access_token

    def _refresh_token(self):
        # request a new token for AZURE AD
        token_data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "scope": self.scope,
        }
        response = requests.post(self.token_url, data=token_data)
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            raise RuntimeError(
                f"Error demanant el token d'accés: {e}\nResposta: {response.text}"
            )

        token_data = response.json()
        self.access_token = token_data["access_token"]
        self.expires_at = time.time() + token_data.get("expires_in", 3600)


def _create_token_manager():
    # read the secrets and create a unique instance of TokenManager.
    if os.getenv("GITHUB_ACTIONS") == "true":
        print("⚠️ Running in GitHub Actions — skipping TokenManager initialization")
        return None
    tenant_id = read_secret("TENANT_ID")
    client_id = read_secret("CLIENT_ID")
    client_secret = read_secret("CLIENT_SECRET")
    if not tenant_id or not client_id or not client_secret:
        raise ValueError(
            "Falten valors de TENANT_ID, CLIENT_ID o CLIENT_SECRET als secrets."
        )
    return TokenManager(
        tenant_id=tenant_id, client_id=client_id, client_secret=client_secret
    )


def get_token_manager():
    if not hasattr(get_token_manager, "_instance"):
        get_token_manager._instance = _create_token_manager()
    return get_token_manager._instance
