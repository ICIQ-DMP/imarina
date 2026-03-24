from pathlib import Path

import requests
import typer

from imarina.core.log_utils import get_logger
from imarina.core.shared_options import DirectoryOpt
from imarina.core.sharepoint import download_input_from_sharepoint

from imarina.core.sharepoint import get_parameters_list, get_token_manager

logger = get_logger(__name__)


# aquesta funcion to sharepoint to InputDirectory
# comment this but no delete

#  downloads files from sharepoint, configure arg for download dir using the diretoryOpt shared options



def download_controller(ctx: typer.Context, input_dir: DirectoryOpt = None) -> None:
    #  path or input default
    target_path = input_dir if input_dir is not None else Path("input")

    print(f" Starting download of input files from SharePoint into: {target_path}")

    try:
        # function download_input_from_sharepoint
        download_input_from_sharepoint(str(target_path))

        print(
            f" DONE : Input files successfully downloaded to local directory: {target_path}"
        )
    except Exception as e:

        print(f" Error downloading input files from SharePoint: {e}")


    try:
        # Function get_parameters_list and download the links(url) of Excels (A3 Excel and iMarina Excel)
        A3_link, imarina_link = get_parameters_list()
        token_manager = get_token_manager() # get token
        headers = {"Authorization": f"Bearer {token_manager.get_token()}"}

        for url, filename in [(A3_link, "A3.xlsx"), (imarina_link, "iMarina.xlsx")]:
            if not url:
                print(f"URL no found {filename}")
                continue

            import base64
            encoded = base64.b64encode(url.encode()).decode()
            encoded = encoded.rstrip("=").replace("/", "_").replace("+", "-")
            download_url = f"https://graph.microsoft.com/v1.0/shares/u!{encoded}/driveItem/content"

            response = requests.get(download_url, headers=headers, allow_redirects=True)
            response.raise_for_status()
            with open(target_path / filename, "wb") as f:
                f.write(response.content)
            print(f"✅ {filename} download successful")


    except Exception as e:
        print(f" Error getting parameters for MS List: {e}")


    return
