# imarina-load - Automated imarina data loads
# Copyright (C) 2026  Aleix Mariné Tena (AleixMT) and Sonia Sayalero
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import typer

from imarina.core.defines import (
    DEFAULT_DRY_RUN,
    DEFAULT_PUBLISH_FILE_PATH,
    FTP_UPLOAD_PATH,
    OUTPUT_DIR,
)
from imarina.core.file_select import select_file_to_upload
from imarina.core.ftp import FtpCredentials, upload_file_ftp
from imarina.core.log_utils import get_logger
from imarina.core.secret import SecretName, read_secret
from imarina.core.shared_options import DryRunOpt, PublishFilePathOpt

logger = get_logger(__name__)


def publish_controller(
    file_path: PublishFilePathOpt = DEFAULT_PUBLISH_FILE_PATH,
    dry_run: DryRunOpt = DEFAULT_DRY_RUN,
) -> None:
    """
    Publishes an Excel file into the SFTP server of iMarina service.
    If the Excel is not provided it will be deduced from the output folder using the date in the filename or the last
    modification date.
    By default, only connects to the SFTP server but does not do the upload. To upload the file the parameter --dry-run
    false must be provided.
    """

    if file_path is None:
        file_path = select_file_to_upload(OUTPUT_DIR)

    credentials = FtpCredentials(
        host=read_secret(SecretName.FTP_HOST),
        port=int(read_secret(SecretName.FTP_PORT)),
        username=read_secret(SecretName.FTP_USER),
        password=read_secret(SecretName.FTP_PASSWORD),
    )

    try:
        upload_file_ftp(
            path=file_path,
            credentials=credentials,
            dry_run=dry_run,
            upload_filename=FTP_UPLOAD_PATH,
        )
    # Broad on purpose: CLI boundary turns any failure into a clean exit(1).
    except Exception as e:
        logger.exception("Error publishing file to iMarina FTP server")
        raise typer.Exit(code=1) from e
