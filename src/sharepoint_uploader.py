import os
from email import errors
from pathlib import Path

import requests
from requests.exceptions import HTTPError
from urllib.parse import quote

from TokenManager import get_token_manager
from datetime import datetime

access_token = get_token_manager()
from secret import read_secret


def list_drives():

    token_manager = get_token_manager()
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

    url = "https://graph.microsoft.com/v1.0/sites/iciq.sharepoint.com:/sites/digitalitzacio-InstitutionalStrengthening:/drives"
    response = requests.get(url, headers=headers)
    print(response.json())


def get_site_id(token_manager, domain, site_name):
    url = f"https://graph.microsoft.com/v1.0/sites/{domain}:/sites/{site_name}"   #Obtain the ID of site from SharePoint.
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    return response.json()["id"]



def get_drive_id(token_manager, site_id, drive_name="Documents"):
    encoded_site_id = quote(site_id, safe='')

    url = f"https://graph.microsoft.com/v1.0/sites/{encoded_site_id}/drives"  #Obtain the ID from drive(library documents) from site
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    drives = response.json().get("value", [])
    for drive in drives:
        if drive["name"] == drive_name:
            return drive["id"]
    raise Exception(f"Drive '{drive_name}' no encontrado en el site.")


def upload_file(token_manager, drive_id, remote_path, local_file_path):
    print(f"Uploading from local path {local_file_path} to {remote_path}")
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_path}:/content?@microsoft.graph.conflictBehavior=replace"  #replace if the file have exist
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "Content-Type": "application/octet-stream"
    }

    with open(local_file_path, "rb") as f:

        response = requests.put(url, headers=headers, data=f, timeout=300)
        response.raise_for_status()
    print("✅ Upload Done")


# Uploads a file to the SharePoint site 'Institutional Strengthening'. TODO: two functions, one for uploading files generically and other that sets the config that you need
def upload_file_sharepoint(file_path: Path, target_folder: str = ""):   #Args: file_path: Local file path to upload.  target_folder: Relative path inside drive(ex:'Uploads/2025-10').
    if isinstance(file_path, str):
        file_path = Path(file_path)

    token_manager = get_token_manager()

    drive_id = "b!KJ1B2DCzSkuCoY3RpzAwFygN2jp0uu1LuLHdfD8wx_3n_8Rkg41LSY25TQTmrzYb"

    filename = file_path.name
    remote_path = f"{target_folder}/{filename}".strip("/")


    # 5.Return URL confirmation
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_path}:/content?%40microsoft.graph.conflictBehavior=replace"
    headers = {
        "Authorization": f"Bearer {token_manager.get_token()}",
        "Content-Type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    }


    with open(file_path, "rb") as f:
        response = requests.put(url, headers=headers, data=f, timeout=300)
    if response.status_code not in (200, 201):
        print(f"✅ Archivo '{file_path.name}' subido correctamente.")
    elif response.status_code == 404:
        print(f"❌ Error: La carpeta destino no existe ({target_folder}) en SharePoint.")

    response.raise_for_status()


def download_input_to_sharepoint(local_input_folder: str = "/app/input"):
    print("Iniciando subida de archivos input al SharePoint.")

    token_manager = get_token_manager()

    drive_id = "b!KJ1B2DCzSkuCoY3RpzAwFygN2jp0uu1LuLHdfD8wx_3n_8Rkg41LSY25TQTmrzYb"
    sharepoint_input_folder = "Institutional Strengthening/_Projects/iMarina_load_automation/input"

    local_path = Path(local_input_folder)

    if not local_path.exists():
        print(f"❌ Error: La carpeta local '{local_input_folder}' no existe")
        return

    files = list(local_path.glob("*.xlsx"))
    if not files:
        print(f"⚠️ No se encontraron archivos .xlsx en {local_input_folder}")
        return

    print(f"📂 Encontrados {len(files)} archivos para subir desde {local_input_folder}")
    uploaded_count = 0
    errors = []


    for file_path in files:
        try:
            # TODO from this point extract this function and create a new
            print(f"  ⬆️ Subiendo: {file_path.name}")
            remote_path = f"{sharepoint_input_folder}/{file_path.name}".strip("/")

            url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{remote_path}:/content"
            headers = {
                "Authorization": f"Bearer {token_manager.get_token()}",
                "Content-Type": "application/octet-stream"

            }
            with open(file_path, "rb") as f:
                 response = requests.put(url, headers=headers, data=f, timeout=300)

            code = response.status_code

            # correct ✅ if code is 200 or 201 & body content data context
            if code in (200, 201):
                 print(f"  ✅ {file_path.name} subido/reemplazado correctamente en SharePoint ({code})")
                 uploaded_count += 1

            elif code >= 400:
                error_msg = f"{file_path.name}: {code} - {response.reason}"
                print(f"\n Error subiendo {file_path.name}: {error_msg}")
                errors.append(error_msg)
            else:
                print(f"  ⚠️ Respuesta inesperada ({code}), pero archivo {file_path.name} parece subido correctamente.")
                uploaded_count += 1

        except Exception as e:
            error_msg = f"{file_path.name}: {str(e)}"
            print(f"  ❌ Error: {error_msg}")
            errors.append(error_msg)


    print("\n" + "=" * 60)
    print(f"✅ Subida completada: {uploaded_count}/{len(files)} archivos subidos correctamente")
    if errors:
        print(f"❌ {len(errors)} errores durante la subida:")
        for error in errors:
            print(f"  - {error}")
    print("=" * 60)


def folder_exists(token_manager, drive_id, folder_path):
    url = f"https://graph.microsoft.com/v1.0/drives/{drive_id}/root:/{folder_path}"
    headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

    try:
        response = requests.get(url, headers=headers, timeout=60)
        return response.status_code == 200
    except:
        return False


def upload_latest_excel():
    print("Entrando en upload_latest_excel()")
    uploads_dir =  Path("/app/uploads")

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
        print(f"✅ Fitxer {latest_file.name} pujat correctament a SharePoint a la carpeta {target_folder}.")
    except Exception as e:
        print(f"❌ Error pujant '{latest_file.name}': {e}")



if __name__ == "__main__":
    list_drives()
    upload_latest_excel()


