import typer

from imarina.core.log_utils import configure_logging_from_settings, get_logger
from imarina.core.sharepoint import download_input_from_sharepoint

logger = get_logger(__name__)


def download_controller(ctx: typer.Context) -> None:
    configure_logging_from_settings()

    # TODO downloads files from sharepoint, configure arg for download dir using the diretoryOpt shared options

    print("🔄 Starting download of input files to from SharePoint into input...")
    try:
        download_input_from_sharepoint(input_dir)
        print("✅ Input files successfully uploaded to SharePoint/input.")
    except Exception as e:
        print(f"❌ Error uploading input files to SharePoint: {e}")
    return
