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
    ftp = None
    try:
        serv = paramiko.Transport((host, port))
        serv.connect(username=username, password=password)
        ftp = paramiko.SFTPClient.from_transport(serv)
    except Exception as e:
        logger.exception(e)
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
    except Exception as e:
        logger.exception(e)
    logger.info("File uploaded to FTP server.")

    logger.info("Closing connection.")
    try:
        ftp.close()
    except Exception as e:
        logger.exception(e)
    logger.info("Closed connection.")
