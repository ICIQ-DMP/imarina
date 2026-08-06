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

from pathlib import Path

import paramiko

from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


def upload_file_ftp(
    path: Path,
    host: str,
    port: int,
    username: str,
    password: str,
    dry_run: bool,
    upload_filename: str,
) -> None:
    logger.info("Connecting to FTP server.")
    ftp: paramiko.SFTPClient | None = None
    try:
        serv = paramiko.Transport((host, port))
        serv.connect(username=username, password=password)
        ftp = paramiko.SFTPClient.from_transport(serv)
    except Exception:
        logger.exception("Failed to connect to FTP server.")
        return
    assert ftp is not None  # if ftp
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
    logger.info("File uploaded to FTP server.")

    logger.info("Closing connection.")
    try:
        ftp.close()
    except Exception:
        logger.exception("Failed to close FTP connection.")
    logger.info("Closed connection.")
