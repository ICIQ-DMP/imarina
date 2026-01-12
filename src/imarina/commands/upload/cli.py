from datetime import datetime
from pathlib import Path

import typer

from imarina.core.log_utils import get_logger
from imarina.core.sharepoint import upload_file_sharepoint_2

logger = get_logger(__name__)


def download_controller(
    ctx: typer.Context,
    file_path: Path = typer.Option(
        None, help="Path of the jobs dictionary file(.xlsx)"
    ),
    target_folder: Path = typer.Option(
        f"Institutional Strengthening/_Projects/iMarina_load_automation/uploads/{datetime.today().strftime('%d-%m-%Y')}",
        help="Path of the jobs dictionary file(.xlsx)",
    ),
) -> None:
    # Phase 4: Upload to SharePoint (Institutional Strengthening)
    print("Uploading the latest Excel file to SharePoint...")
    print(f"📁 Path del fitxer generat: {file_path}")
    try:
        upload_file_sharepoint_2(file_path, target_folder)
        logger.info("✅ Upload to SharePoint completed successfully.")

    except Exception as e:
        logger.error(f"❌ Error uploading to SharePoint: {e}")
        raise
