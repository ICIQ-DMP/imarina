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

from enum import StrEnum


class SecretName(StrEnum):
    """All secret names that can be resolved via read_secret()."""

    CLIENT_ID = "CLIENT_ID"
    CLIENT_NAME = "CLIENT_NAME"
    CLIENT_SECRET = "CLIENT_SECRET"
    DRIVE_ID = "DRIVE_ID"
    SHAREPOINT_DOMAIN = "SHAREPOINT_DOMAIN"
    SITE_NAME = "SITE_NAME"
    TENANT_ID = "TENANT_ID"
    LIST_NAME = "LIST_NAME"

    FTP_HOST = "FTP_HOST"
    FTP_PASSWORD = "FTP_PASSWORD"
    FTP_PORT = "FTP_PORT"
    FTP_UPLOAD_FILENAME = "FTP_UPLOAD_FILENAME"
    FTP_USER = "FTP_USER"

    SSH_HOST = "SSH_HOST"
    SSH_PASSWORD = "SSH_PASSWORD"
    SSH_USERNAME = "SSH_USERNAME"

    JENKINS_PASSWORD = "JENKINS_PASSWORD"
    JENKINS_USERNAME = "JENKINS_USERNAME"

    SMTP_USERNAME = "SMTP_USERNAME"
    SMTP_PASSWORD = "SMTP_PASSWORD"
    SMTP_HOST = "SMTP_HOST"
    SMTP_PORT = "SMTP_PORT"
