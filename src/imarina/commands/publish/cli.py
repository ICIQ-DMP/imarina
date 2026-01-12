from pathlib import Path

import typer

from imarina.core.ftp import upload_excel
from imarina.core.log_utils import configure_logging_from_settings, get_logger

logger = get_logger(__name__)


def download_controller(
    ctx: typer.Context,
    file_path: Path = typer.Option(
        None, help="Path of the jobs dictionary file(.xlsx)"
    ),
) -> None:
    configure_logging_from_settings()

    upload_excel(file_path)
