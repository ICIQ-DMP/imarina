from pathlib import Path
import typer
from datetime import datetime  # timestamp
from imarina.core.shared_options import DirectoryOpt
from imarina.core.sharepoint import upload_file_sharepoint
from imarina.core.log_utils import configure_logging_from_settings


def backup_controller(ctx: typer.Context, directory: DirectoryOpt = None) -> None:

    configure_logging_from_settings()

    local_uploads_dir = directory if directory is not None else Path.cwd() / "uploads"

    if not local_uploads_dir.exists():
        print(f"❌ Error: No s'ha trobat la carpeta local: {local_uploads_dir}")
        return

    local_files = list(local_uploads_dir.glob("*.xlsx"))
    if not local_files:
        print(f"⚠️ No hi ha cap fitxer Excel local a: {local_uploads_dir}")
        return

    latest_local_file = max(local_files, key=lambda f: f.stat().st_mtime)

    now = datetime.now()
    today_folder = now.strftime("%Y-%m-%d")
    timestamp_name = f"iMarina_upload_{now.strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"

    target_sharepoint_folder = f"Institutional Strengthening/_Projects/iMarina_load_automation/output/{today_folder}"

    print(f"📂 Fitxer local detectat: {latest_local_file.name}")
    print(f"☁️ Upload to SharePoint: {timestamp_name}")

    try:
        # copy temp with timestamp name
        temp_file = latest_local_file.with_name(timestamp_name)

        # copy original file
        import shutil

        shutil.copy2(latest_local_file, temp_file)

        try:

            upload_file_sharepoint(temp_file, target_folder=target_sharepoint_folder)
            print(f"✅ Backup fet al SharePoint : output/{today_folder}/")
        finally:

            if temp_file.exists():
                temp_file.unlink()

    except Exception as e:
        print(f"❌ Error fent el backup: {e}")
