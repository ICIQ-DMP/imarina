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

import argparse
import smtplib

# from email.message import EmailMessage
from email.mime.text import MIMEText

import requests

from imarina.core.secret import SecretName, read_secret
from imarina.core.sharepoint import get_list_id, get_site_id
from imarina.core.token_manager import get_token_manager


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

    print("Email sent!")


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


def mail_process(args: argparse.Namespace) -> None:

    smtp_password = read_secret(SecretName.SMTP_PASSWORD)
    smtp_user = read_secret(SecretName.SMTP_USERNAME)
    smtp_server = read_secret(SecretName.SMTP_HOST)
    smtp_port = int(read_secret(SecretName.SMTP_PORT))

    # credentials MS GRAPH
    tenant_id = read_secret(SecretName.TENANT_ID)
    client_id = read_secret(SecretName.CLIENT_ID)
    client_secret = read_secret(SecretName.CLIENT_SECRET)
    site_id = get_site_id(
        get_token_manager(),
        read_secret(SecretName.SHAREPOINT_DOMAIN),
        read_secret(SecretName.SITE_NAME),
    )
    list_id = get_list_id(
        get_token_manager(), site_id, read_secret(SecretName.LIST_NAME)
    )

    print("Getting access token...")
    token = get_access_token(tenant_id, client_id, client_secret)

    print(f"Getting creator info for item ID {args.id}...")
    to_email, name = get_creator_email(token, site_id, list_id, args.id)
    print(f"Sending email to: {to_email} ({name})")

    if args.status == "success":
        subject = f"iMarina - Workflow ID {args.id} completed successfully"
        body = build_success_body(name, args.id, args.sharepoint_path)
    else:
        subject = f"iMarina - Workflow ID {args.id} failed"
        body = build_error_body(name, args.id)

    send_email(
        to_email,
        subject,
        body,
        smtp_user,
        smtp_user,
        smtp_password,
        smtp_server,
        smtp_port,
    )
    print("Email sent. Process complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Send iMarina workflow notification email"
    )
    parser.add_argument("--id", required=True, help="MS List item ID")
    parser.add_argument(
        "--status", required=True, choices=["success", "error"], help="Workflow status"
    )
    parser.add_argument(
        "--sharepoint-path",
        required=False,
        default="Institutional Strengthening/_Projects/iMarina_load_automation/output",
        help="SharePoint path of the generated file",
    )
    args = parser.parse_args()

    mail_process(args)
