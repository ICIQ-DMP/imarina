from pathlib import Path

import typer

from imarina.core.log_utils import get_logger
from imarina.core.sharepoint import upload_file_sharepoint

logger = get_logger(__name__)


def upload_controller(
    ctx: typer.Context,
    file_path: Path = typer.Option(
        None,
        help="Excel file path (.xlsx). If left empty, it will look for the last one in 'output'.",
    ),
    target_folder: Path = typer.Option(
        "Institutional Strengthening/_Projects/iMarina_load_automation/output",
        help="Folder to the destination Sharepoint",
    ),
) -> None:
    print(" Uploading the latest Excel file to SharePoint...")

    if file_path is None:
        uploads_dir = Path.cwd() / "output"
        if uploads_dir.exists():
            # recent file in uploads folder
            files = list(uploads_dir.glob("*.xlsx"))
            if files:
                file_path = max(files, key=lambda f: f.stat().st_mtime)
            else:
                print(f"❌ Error: Not files Excel in  {uploads_dir}")
                raise typer.Exit(code=1)
        else:
            print(
                "❌ Error: No file specified and the 'output' folder does not exist.."
            )
            raise typer.Exit(code=1)

    # the file not exist in the path
    if not file_path.exists():
        print(f"❌ Error: The file no exist in the path: {file_path}")
        raise typer.Exit(code=1)

    print(f"📁 Local file detected: {file_path.name}")
    print(f"☁️ Destination SharePoint: {target_folder}")

    try:

        upload_file_sharepoint(file_path, target_folder=str(target_folder))
        print("✅ Upload to SharePoint completed successfully.")
        # logger.info(f"Successfully uploaded {file_path.name}")

    except Exception as e:
        print(f"❌ Error uploading to SharePoint: {e}")
        # logger.error(f"Error: {e}")
        raise typer.Exit(code=1)
