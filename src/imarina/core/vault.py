import os
import requests
import urllib3

from imarina.core.log_utils import get_logger

logger = get_logger(__name__)

_VAULT_BASE_PATH = "secret/data/imarina"

# Maps app-level secret names to (vault subpath, vault field key)
_SECRET_MAP = {
    # sharepoint (secret/imarina/runtime/sharepoint)
    "CLIENT_ID":         ("runtime/sharepoint", "client_id"),
    "CLIENT_NAME":       ("runtime/sharepoint", "client_name"),
    "CLIENT_SECRET":     ("runtime/sharepoint", "client_secret"),
    "DRIVE_ID":          ("runtime/sharepoint", "drive_id"),
    "SHAREPOINT_DOMAIN": ("runtime/sharepoint", "domain"),
    "SITE_NAME":         ("runtime/sharepoint", "site_name"),
    "TENANT_ID":         ("runtime/sharepoint", "tenant_id"),
    # ftp (secret/imarina/runtime/ftp)
    "FTP_HOST":            ("runtime/ftp", "host"),
    "FTP_PASSWORD":        ("runtime/ftp", "password"),
    "FTP_PORT":            ("runtime/ftp", "port"),
    "FTP_UPLOAD_FILENAME": ("runtime/ftp", "upload_filename"),
    "FTP_USER":            ("runtime/ftp", "user"),
    # ssh admin (secret/imarina/admin/ssh)
    "SSH_HOST":     ("admin/ssh", "host"),
    "SSH_PASSWORD": ("admin/ssh", "password"),
    "SSH_USERNAME": ("admin/ssh", "username"),
    # jenkins admin (secret/imarina/admin/jenkins)
    "JENKINS_PASSWORD": ("admin/jenkins", "password"),
    "JENKINS_USERNAME": ("admin/jenkins", "username"),
}


_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read_credential(name):
    """Read a Vault connection credential from (in order):
      1. /run/secrets/<name>
      2. <project_root>/secrets/<name>
      3. environment variable
    """
    for path in (f"/run/secrets/{name}", os.path.join(_PROJECT_ROOT, "secrets", name)):
        if os.path.isfile(path):
            with open(path) as f:
                value = f.read().strip()
            if value:
                return value
    value = os.environ.get(name, "").strip()
    if value:
        return value
    raise KeyError(f"Vault credential '{name}' not found in secrets or environment")


class _VaultClient:
    def __init__(self):
        self._token = None
        self._cache = {}  # subpath -> {field: value}

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

    def _authenticate(self):
        # 1. Try a pre-issued Vault token.
        try:
            self._token = _read_credential("VAULT_TOKEN")
            return
        except KeyError:
            pass

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

    def _fetch_subpath(self, subpath):
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
        data = resp.json()["data"]["data"]
        self._cache[subpath] = data
        return data

    def read_secret(self, secret_name):
        if secret_name not in _SECRET_MAP:
            raise KeyError(f"No vault mapping defined for secret '{secret_name}'")
        subpath, field = _SECRET_MAP[secret_name]
        data = self._fetch_subpath(subpath)
        if field not in data:
            raise KeyError(
                f"Field '{field}' not found at vault path '{_VAULT_BASE_PATH}/{subpath}'"
            )
        value = data[field]
        if value is None or str(value).strip() == "":
            raise ValueError(f"Vault secret '{secret_name}' (field '{field}') is empty")
        return str(value)


_client = None


def read_vault_secret(secret_name):
    """Return the value of *secret_name* fetched from Vault.

    Raises KeyError  if the secret has no vault mapping or the field is absent.
    Raises ValueError if the field exists but is empty.
    Raises requests.HTTPError / ConnectionError on network / auth failures.
    """
    logger.debug(f"Requesting secret from Vault: {secret_name}")
    global _client
    if _client is None:
        _client = _VaultClient()
    return _client.read_secret(secret_name)
