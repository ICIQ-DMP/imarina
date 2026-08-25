# imarina-load-researchers - Automated iMarina data loads
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

from dataclasses import dataclass
from pathlib import Path

import paramiko

from imarina_load_researchers.core.exceptions import SftpSessionError
from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


@dataclass
class FtpCredentials:
    host: str
    port: int
    username: str
    password: str


def upload_file_ftp(
    path: Path,
    credentials: FtpCredentials,
    dry_run: bool,
    upload_filename: str,
) -> None:
    """Upload *path* to the iMarina SFTP server.

    Raises on connection or upload failure instead of swallowing the error,
    so the caller can tell a failed publish from a successful one. A failure
    to close the connection afterwards is logged but not raised, since the
    file has already been delivered by that point.
    """
    logger.info("Connecting to FTP server.")
    try:
        serv = paramiko.Transport((credentials.host, credentials.port))
        serv.connect(username=credentials.username, password=credentials.password)
        ftp = paramiko.SFTPClient.from_transport(serv)
    except Exception:
        logger.exception("Failed to connect to FTP server.")
        raise
    if ftp is None:
        raise SftpSessionError
    logger.info("Connected to FTP server.")

    root_files = ftp.listdir()
    logger.trace(f"Files in entry directory of FTP server are: {root_files}")
    if "carga_icolet" in root_files:
        logger.trace(
            f"Files in carga_icolet folder of remote server: {ftp.listdir('carga_icolet')}"
        )

    if dry_run:
        logger.info("Dry run active: Skipping file upload.")
        return

    logger.info("Uploading file.")
    try:
        ftp.put(path, upload_filename)
    except Exception:
        logger.exception("Failed to upload file to FTP server.")
        raise
    logger.info("File uploaded to FTP server.")

    logger.info("Closing connection.")
    try:
        ftp.close()
    except Exception:
        logger.exception("Failed to close FTP connection.")
    else:
        logger.info("Closed connection.")
