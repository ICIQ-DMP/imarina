from pathlib import Path
import typer

from imarina.core.log_utils import get_logger
from imarina.core.shared_options import DirectoryOpt
from imarina.core.sharepoint import download_input_from_sharepoint

logger = get_logger(__name__)


# aquesta funcion to sharepoint to InputDirectory
# comment this but no delete

#  downloads files from sharepoint, configure arg for download dir using the diretoryOpt shared options


def download_controller(ctx: typer.Context, input_dir: DirectoryOpt = None) -> None:
    target_path = input_dir if input_dir is not None else Path("input")

    print(f" Starting download of input files from SharePoint into: {target_path}")

    try:
        download_input_from_sharepoint(str(target_path))
        print(
            f" DONE : Input files successfully downloaded to local directory: {target_path}"
        )
    except Exception as e:
        print(f" Error download input files to SharePoint: {e}")
    return
