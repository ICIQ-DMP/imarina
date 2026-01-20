import typer

from imarina.core.log_utils import configure_logging_from_settings, get_logger
from imarina.core.shared_options import DirectoryOpt
from imarina.core.sharepoint import download_input_from_sharepoint

logger = get_logger(__name__)



# aquesta funcion to sharepoint to InputDirectory
# comment this but no delete

# TODO downloads files from sharepoint, configure arg for download dir using the diretoryOpt shared options

def download_controller(ctx: typer.Context, input_dir: DirectoryOpt) -> None:
    configure_logging_from_settings()

    target_path = input_dir if input_dir is not None else Path("input")

    print(f" Starting download of input files from SharePoint into: {target_path}")

    try:
        download_input_from_sharepoint(target_path)
        print(f" DONE : Input files successfully downloaded to local directory: {target_path}")
    except Exception as e:
        print(f" Error download input files to SharePoint: {e}")
    return




#
# def download_controller(ctx: typer.Context, input_dir: DirectoryOpt) -> None:
#     configure_logging_from_settings()  # funció per configurar els logs
#
#     # Si l'usuari no passa cap directori (-d), DirectoryOpt podria ser None.
#     # Fem servir la carpeta "input" del projecte per defecte en aquest cas.
#     target_path = input_dir if input_dir is not None else Path("input")
#
#     print(f"🔄 Starting download of input files from SharePoint into: {target_path}")
#
#     try:
#         # ruta correcta per fer el download
#         download_input_from_sharepoint(target_path)
#         print(f"✅ Input files successfully downloaded to {target_path}.")
#     except Exception as e:
#         # excepció si no es poden descarregar els arxiu del SharePoint
#         print(f"❌ Error downloading input files from SharePoint: {e}")
#
#     return