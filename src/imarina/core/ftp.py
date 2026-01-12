import paramiko

from imarina.core.log_utils import get_logger
from imarina.core.secret import read_secret

logger = get_logger(__name__)

def upload_excel(excel_path):
    logger.info('Connecting to FTP server.')
    ftp = None
    try:
        serv = paramiko.Transport((read_secret("FTP_HOST"), int(read_secret("FTP_PORT"))))
        serv.connect(username=read_secret("FTP_USER"), password=read_secret("FTP_PASSWORD"))
        ftp = paramiko.SFTPClient.from_transport(serv)
    except Exception as e:
        logger.exception(e)
    logger.info('Connected to FTP server.')

    logger.info('Uploading file.')
    try:
        ftp.put(excel_path, 'icl_ag_personal_12539')
    except Exception as e:
        logger.exception(e)
    logger.info('Uploaded file.')

    logger.info('Closing connection.')
    try:
        ftp.close()
    except Exception as e:
        logger.exception(e)
    logger.info('Closed connection.')
