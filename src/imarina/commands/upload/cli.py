from datetime import datetime
from pathlib import Path

import typer

from imarina.core.log_utils import get_logger
from imarina.core.sharepoint import upload_file_sharepoint

logger = get_logger(__name__)



def upload_controller(
    ctx: typer.Context,
    file_path: Path = typer.Option(
        None, help="Path del fitxer Excel (.xlsx). Si es deixa buit, busca l'últim a 'uploads'."
    ),
    target_folder: Path = typer.Option(
        f"Institutional Strengthening/_Projects/iMarina_load_automation/uploads/{datetime.today().strftime('%d-%m-%Y')}",
        help="Carpeta de destí a SharePoint",
    ),
) -> None:
    print(" Uploading the latest Excel file to SharePoint...")


    if file_path is None:
        uploads_dir = Path.cwd() / "uploads"
        if uploads_dir.exists():
            # recent file in uploads folder
            files = list(uploads_dir.glob("*.xlsx"))
            if files:
                file_path = max(files, key=lambda f: f.stat().st_mtime)
            else:
                print(f"❌ Error: No hi ha fitxers Excel a {uploads_dir}")
                raise typer.Exit(code=1)
        else:
            print(f"❌ Error: No s'ha especificat fitxer i la carpeta 'uploads' no existeix.")
            raise typer.Exit(code=1)

    # the file not exist in the path
    if not file_path.exists():
        print(f"❌ Error: El fitxer no existeix a la ruta: {file_path}")
        raise typer.Exit(code=1)

    print(f"📁 Fitxer local detectat: {file_path.name}")
    print(f"☁️ Destí SharePoint: {target_folder}")

    try:

        upload_file_sharepoint(file_path, target_folder=str(target_folder))
        print("✅ Upload to SharePoint completed successfully.")
        # logger.info(f"Successfully uploaded {file_path.name}")

    except Exception as e:
        print(f"❌ Error uploading to SharePoint: {e}")
        # logger.error(f"Error: {e}")
        raise typer.Exit(code=1)











# def upload_controller(
#     ctx: typer.Context,
#     file_path: Path = typer.Option(
#         None, help="Path of the jobs dictionary file(.xlsx)"
#     ),
#     target_folder: Path = typer.Option(
#         f"Institutional Strengthening/_Projects/iMarina_load_automation/uploads/{datetime.today().strftime('%d-%m-%Y')}",
#         help="Path of the jobs dictionary file(.xlsx)",
#     ),
# ) -> None:
#     # Phase 4: Upload to SharePoint (Institutional Strengthening)
#     print("Uploading the latest Excel file to SharePoint...")
#     if file_path is None or not file_path.exists():
#         print(f"❌ Error: No s'ha trobat el fitxer a la ruta: {file_path}")
#         return
#
#     print(f"📁 Fitxer local: {file_path.name}")
#     print(f" Destí: {target_folder}")
#
#    # print(f"📁 Path del fitxer generat: {file_path}")
#     try:
#         upload_file_sharepoint(file_path, target_folder=str(target_folder))
#         logger.info("✅ Upload to SharePoint completed successfully.")
#
#     except Exception as e:
#         logger.error(f"❌ Error uploading to SharePoint: {e}")
#         raise typer.Exit(code=1)
