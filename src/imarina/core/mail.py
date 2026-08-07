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

import smtplib
from email.mime.text import MIMEText
from enum import StrEnum

import requests

from imarina.core.log_utils import get_logger

logger = get_logger(__name__)


class WorkflowStatus(StrEnum):
    """Outcome of the iMarina build pipeline, reported by the `notify` command."""

    SUCCESS = "success"
    ERROR = "error"


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return str(response.json()["access_token"])


def get_creator_email(
    token: str, site_id: str, list_id: str, item_id: str
) -> tuple[str, str]:
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items/{item_id}?expand=fields"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    fields = response.json().get("createdBy", {}).get("user", {})
    return fields.get("email", ""), fields.get("displayName", "")


def send_email(
    to_email: str,
    subject: str,
    body: str,
    from_email: str,
    username: str,
    password: str,
    server: str,
    port: int,
) -> None:
    # Create message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    # Connect to Microsoft 365 SMTP
    with smtplib.SMTP(server, port) as smtp_conn:
        smtp_conn.ehlo()
        smtp_conn.starttls()  # Upgrade connection to TLS
        smtp_conn.login(username, password)
        smtp_conn.sendmail(from_email, [to_email], msg.as_string())

    logger.info("Email sent!")


def build_success_body(name: str, item_id: str, sharepoint_path: str) -> str:
    return (
        f"Hello {name},\n\n"
        f"We inform you that the iMarina workflow with ID {item_id} has completed successfully.\n\n"
        f"The generated file is available on SharePoint at the following path:\n"
        f"{sharepoint_path}\n\n"
        f"For any questions, contact the Digitalization team.\n\n"
        f"Regards,\n\n"
        f"(This message was auto-generated.)"
    )


def build_error_body(name: str, item_id: str) -> str:
    return (
        f"Hello {name},\n\n"
        f"We inform you that your iMarina workflow with ID {item_id} has failed.\n\n"
        f"Please contact the Digitalization team for more information.\n\n"
        f"Regards,\n\n"
        f"(This message was auto-generated.)"
    )
