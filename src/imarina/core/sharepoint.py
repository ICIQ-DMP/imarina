import os
from pathlib import Path

import requests
from urllib.parse import quote

from imarina.core.TokenManager import get_token_manager, TokenManager
from datetime import datetime
from typing import Any
from imarina.core.log_utils import get_logger

logger = get_logger(__name__)
access_token = get_token_manager()


def list_drives() -> None:

    token_manager = get_token_manager()
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

    url = "https://graph.microsoft.com/v1.0/sites/iciq.sharepoint.com:/sites/digitalitzacio-InstitutionalStrengthening:/drives"
    response = requests.get(url, headers=headers)
    print(response.json())


def get_site_id(token_manager: TokenManager, domain: str, site_name: str) -> Any:
    url = f"https://graph.microsoft.com/v1.0/sites/{domain}:/sites/{site_name}"  # Obtain the ID of site from SharePoint.
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()["id"]


def get_drive_id(
    token_manager: TokenManager, site_id: str, drive_name: str = "Documents"
) -> Any:
    encoded_site_id = quote(site_id, safe="")

    url = f"https://graph.microsoft.com/v1.0/sites/{encoded_site_id}/drives"  # Obtain the ID from drive(library documents) from site
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    drives = response.json().get("value", [])
    for drive in drives:
        if drive["name"] == drive_name:
            return drive["id"]
    raise Exception(f"Drive '{drive_name}' no encontrado en el site.")


def upload_file(
    token_manager: TokenManager, drive_id: str, remote_path: str, local_file_path: str
) -> None:
    print(f"Uploading from local path {local_file_path} to {remote_path}")
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_path}:/content?@microsoft.graph.conflictBehavior=replace"  # replace if the file have exist
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "Content-Type": "application/octet-stream",
    }

    with open(local_file_path, "rb") as f:

        response = requests.put(url, headers=headers, data=f, timeout=300)
        response.raise_for_status()
    print("✅ Upload Done")


# in this function read the folder in path: SECRETS / new file added DRIVE_ID


def get_sharepoint_drive_id() -> str:

    current_path = Path(__file__).resolve()

    root = current_path
    while root.parent != root:
        if (root / "secrets").is_dir():
            break
        root = root.parent

    secret_path = root / "secrets" / "DRIVE_ID"

    if not secret_path.exists():

        if (root.parent / "secrets").is_dir():
            secret_path = root.parent / "secrets" / "DRIVE_ID"

    try:
        return secret_path.read_text().strip()
    except FileNotFoundError:
        raise RuntimeError(f"❌ No s'ha trobat el secret a {secret_path.absolute()}")




# Uploads a file to the SharePoint site 'Institutional Strengthening'.
def upload_file_sharepoint(
    file_path: Path, target_folder: str = "_Projects/iMarina_load_automation/uploads"
) -> (
    Any
):  # Args: file_path: Local file path to upload.  target_folder: Relative path inside drive(ex:'Uploads/2025-10').
    if isinstance(file_path, str):
        file_path = Path(file_path)

    token_manager = get_token_manager()

    drive_id = (
        get_sharepoint_drive_id()
    )  # drive_id is read in a method (get_sharepoint_drive_id)

    filename = file_path.name
    remote_path = f"{target_folder}/{filename}".strip("/")

    # 5.Return URL confirmation
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_path}:/content?%40microsoft.graph.conflictBehavior=replace"
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }
    try:
        with open(file_path, "rb") as f:
            response = requests.put(url, headers=headers, data=f, timeout=300)

        if response.status_code in (200, 201):
            print(f"✅ Archivo '{filename}' subido correctamente a {target_folder}.")
        else:

            response.raise_for_status()

    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print(
                f"❌ Error: La carpeta destino no existe ({target_folder}) en SharePoint."
            )
        else:
            print(f"❌ Error HTTP al subir '{filename}': {e}")
        raise
    except Exception as e:
        print(f"❌ Error inesperado al subir '{filename}': {e}")
        raise


def download_input_from_sharepoint(local_input_folder: str = "input") -> Any:
    print("--- Iniciando proceso de DESCARGA desde SharePoint ---")

    token_manager = get_token_manager()
    drive_id = get_sharepoint_drive_id()

    # sharepoint path
    sharepoint_path = "Institutional Strengthening/_Projects/iMarina_load_automation/input"

    # local folder exist
    local_path = Path(local_input_folder)
    local_path.mkdir(parents=True, exist_ok=True)

    # authorization with token_manager
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

    # in process
    operation_id = os.environ.get("OPERATION_ID")
    site_id = os.environ.get("MS_SITE_ID")
    list_id = os.environ.get("MS_LIST_ID")

    if not operation_id:
        raise Exception("OPERATION_ID not defined in venv")

    print(f"Check MS LIST for ID : {operation_id}")

    response = requests.get(
        f"https://graph.microsoft.com/v1.0/sites/iciq.sharepoint.com,{os.environ['MS_SITE_ID']}/lists/{os.environ['MS_LIST_ID']}/items/{os.environ['OPERATION_ID']}?expand=fields",
        headers=headers,
        timeout=30

    )

    if response.status_code != 200:
        raise Exception(f"Error to Check the List: {response.status_code} - {response.text}")

    fields = response.json()["fields"]
    print("DEBUG fields:", list(fields.keys()))
    files_to_download = {
        "A3.xlsx": fields.get("A3 Excel Link"),
        "iMarina.xlsx": fields.get("iMarina Excel Link"),
    }

    try:
        url_list = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{sharepoint_path}:/children"
        response = requests.get(url_list, headers=headers, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Error to list Sharepoint {response.status_code} - {response.text}")
        items = response.json().get('value', [])
        files_to_download_sp = [f for f in items if f.get('file') and f['name'] in files_to_download]
        if not files_to_download_sp:
            print(f" Not files .xlsx in the Sharepoint path")
            return

        print(f" Found {len(files_to_download_sp)} files to download...")

        for remote_file in files_to_download_sp:
            name = remote_file['name']
            url_download = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{remote_file['id']}/content"
            res_file = requests.get(url_download, headers=headers, timeout=300)

            if res_file.status_code == 200:
                with open(local_path / name, "wb") as f:
                    f.write(res_file.content)
                print(f" Save {name} successfully")
            else:
                print(f" Error downloading {name} : {res_file.status_code}")

    except Exception as e:
        print(f" Error downloading {name} : {e}")
        raise e
    ### IN PROCESS



    try:

        url_list = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{sharepoint_path}:/children"
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        response = requests.get(url_list, headers=headers, timeout=30)

        if response.status_code != 200:
            raise Exception(f"Error al listar SharePoint: {response.status_code} - {response.text}")

        items = response.json().get('value', [])
        # only files (.xlsx)
        files_to_download = [f for f in items if f.get('file') and f['name'].endswith('.xlsx')]

        if not files_to_download:
            print(f"⚠️ No hay archivos .xlsx para descargar en la ruta de SharePoint.")
            return

        print(f"📂 Encontrados {len(files_to_download)} archivos. Descargando...")

        for remote_file in files_to_download:
            name = remote_file['name']

            url_download = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/items/{remote_file['id']}/content"

            res_file = requests.get(url_download, headers=headers, timeout=300)

            if res_file.status_code == 200:
                with open(local_path / name, "wb") as f:
                    f.write(res_file.content)
                print(f"  ✅ {name} guardado con éxito.")
            else:
                print(f"  ❌ Error al bajar {name}: {res_file.status_code}")

    except Exception as e:
        print(f"❌ Fallo crítico en la descarga: {e}")
        raise e



def folder_exists(token_manager: TokenManager, drive_id: str, folder_path: str) -> bool:
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}"
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

    response = requests.get(url, headers=headers, timeout=60)
    return response.status_code == 200


def upload_latest_excel() -> Any:
    print("Entrando en upload_latest_excel()")
    uploads_dir = Path("/app/uploads")

    excel_files = list(uploads_dir.glob("iMarina_upload_*.xlsx"))
    if not excel_files:
        print("⚠️ No se encontró ningún archivo iMarina_upload_*.xlsx en /app/uploads")
        return

    latest_file = max(excel_files, key=os.path.getmtime)
    print(f"📂 Últim fitxer trobat: {latest_file.name}")

    today_folder = datetime.today().strftime("%d-%m-%Y")
    target_folder = f"Institutional Strengthening/_Projects/iMarina_load_automation/uploads/{today_folder}"

    try:
        print(f"⬆️ Subiendo {latest_file.name} a {target_folder}...")
        upload_file_sharepoint(latest_file, target_folder=target_folder)
        print(
            f"✅ Fitxer {latest_file.name} pujat correctament a SharePoint a la carpeta {target_folder}."
        )
    except Exception as e:
        print(f"❌ Error pujant '{latest_file.name}': {e}")


if __name__ == "__main__":
    token_manager = get_token_manager()

    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
    }

    site_name = "digitalitzacio-InstitutionalStrengthening"
    tenant_domain = "iciq.sharepoint.com"

    url = f"https://graph.microsoft.com/v1.0/sites/{tenant_domain}:/sites/{site_name}:/drives"

    print("Requesting drive info from:", url)
    r = requests.get(url, headers=headers)
    r.raise_for_status()
    print(r.json())

    upload_latest_excel()
