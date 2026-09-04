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

import smtplib
from dataclasses import dataclass
from email.mime.text import MIMEText
from enum import StrEnum

import requests

from imarina_load_researchers.core.log_utils import get_logger

logger = get_logger(__name__)


class WorkflowStatus(StrEnum):
    """Outcome reported by the `notify` command, from either the main
    download/build/upload pipeline or the separate, approval-gated publish
    pipeline (publish.Jenkinsfile)."""

    SUCCESS = "success"
    PUBLISHED = "published"
    ERROR = "error"


def get_access_token(tenant_id: str, client_id: str, client_secret: str) -> str:
    """
    Requests a Graph API app-only access token via the client-credentials flow.

    Args:
        tenant_id (str): Azure AD tenant ID.
        client_id (str): App registration's client ID.
        client_secret (str): App registration's client secret.

    Returns:
        str: The bearer access token.

    Raises:
        requests.HTTPError: If the token request fails.
    """
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(url, data=data, timeout=10)
    response.raise_for_status()
    return str(response.json()["access_token"])


def get_creator_email(
    token: str, site_id: str, list_id: str, item_id: str
) -> tuple[str, str]:
    """
    Looks up the email and display name of whoever created an MS List item.

    Used by `notify` to find who to email: the request's original submitter.

    Args:
        token (str): Graph API bearer access token.
        site_id (str): SharePoint site ID hosting the list.
        list_id (str): MS List ID.
        item_id (str): The list item's ID (the workflow's Operation ID).

    Returns:
        tuple[str, str]: `(email, display_name)`, either of which may be
            `""` if Graph didn't return it.

    Raises:
        requests.HTTPError: If the Graph API request fails.
    """
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items/{item_id}?expand=fields"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers, timeout=60)
    response.raise_for_status()
    fields = response.json().get("createdBy", {}).get("user", {})
    return fields.get("email", ""), fields.get("displayName", "")


@dataclass
class EmailContent:
    """A fully-composed email, ready to hand to `send_email`."""

    to_email: str
    subject: str
    body: str
    from_email: str


def send_email(
    message: EmailContent,
    username: str,
    password: str,
    server: str,
    port: int,
) -> None:
    """
    Sends an email over SMTP with STARTTLS (Microsoft 365 SMTP).

    Args:
        message (EmailContent): The email to send.
        username (str): SMTP auth username.
        password (str): SMTP auth password.
        server (str): SMTP server hostname.
        port (int): SMTP server port.

    Raises:
        smtplib.SMTPException: If the connection, login or send fails.
    """
    # Create message
    msg = MIMEText(message.body)
    msg["Subject"] = message.subject
    msg["From"] = message.from_email
    msg["To"] = message.to_email

    # Connect to Microsoft 365 SMTP
    with smtplib.SMTP(server, port) as smtp_conn:
        smtp_conn.ehlo()
        smtp_conn.starttls()  # Upgrade connection to TLS
        smtp_conn.login(username, password)
        smtp_conn.sendmail(message.from_email, [message.to_email], msg.as_string())

    logger.info("Email sent!")


def build_success_body(name: str, item_id: str, sharepoint_path: str) -> str:
    """
    Builds the email body for a successful `download`/`build`/`upload` run.

    Tells the requester their generated file is on SharePoint for review -
    see `build_published_body` for the wording used once it's been
    published instead.

    Args:
        name (str): Requester's display name.
        item_id (str): The workflow's Operation ID.
        sharepoint_path (str): SharePoint path where the file was uploaded.

    Returns:
        str: The plain-text email body.
    """
    return (
        f"Hello {name},\n\n"
        f"We inform you that the iMarina workflow with ID {item_id} has completed successfully.\n\n"
        f"The generated file is available on SharePoint at the following path:\n"
        f"{sharepoint_path}\n\n"
        f"For any questions, contact the Digitalization team.\n\n"
        f"Regards,\n\n"
        f"(This message was auto-generated.)"
    )


def build_published_body(name: str, item_id: str) -> str:
    """
    Builds the email body for a successful `publish` run.

    Distinct from `build_success_body` because a requester whose file has
    already been published shouldn't be told to go review it.

    Args:
        name (str): Requester's display name.
        item_id (str): The workflow's Operation ID.

    Returns:
        str: The plain-text email body.
    """
    return (
        f"Hello {name},\n\n"
        f"We inform you that the iMarina workflow with ID {item_id} has been "
        f"approved and published to the iMarina server.\n\n"
        f"For any questions, contact the Digitalization team.\n\n"
        f"Regards,\n\n"
        f"(This message was auto-generated.)"
    )


def build_error_body(name: str, item_id: str) -> str:
    """
    Builds the email body for a failed pipeline run (`--status error`).

    Args:
        name (str): Requester's display name.
        item_id (str): The workflow's Operation ID.

    Returns:
        str: The plain-text email body.
    """
    return (
        f"Hello {name},\n\n"
        f"We inform you that your iMarina workflow with ID {item_id} has failed.\n\n"
        f"Please contact the Digitalization team for more information.\n\n"
        f"Regards,\n\n"
        f"(This message was auto-generated.)"
    )
