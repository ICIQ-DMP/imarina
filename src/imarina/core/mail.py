import argparse
import requests
import smtplib
#from email.message import EmailMessage
from email.mime.text import MIMEText
from secret import read_secret



def get_access_token(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    response = requests.post(url, data=data)
    response.raise_for_status()
    return response.json()["access_token"]


def get_creator_email(token, site_id, list_id, item_id):
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items/{item_id}?expand=fields"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    fields = response.json().get("createdBy", {}).get("user", {})
    return fields.get("email", ""), fields.get("displayName", "")



# def send_mail2(username, password, to, host, port, subject, content):
#     SMTP_SERVER = host
#     SMTP_PORT = port
#     USERNAME = username
#     PASSWORD = password
#
#     msg = EmailMessage()
#     msg["Subject"] = subject
#     msg["From"] = USERNAME
#     msg["To"] = to
#     msg.set_content(content)
#
#     with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
#         smtp.starttls()  # Use TLS
#         smtp.login(USERNAME, PASSWORD)
#         smtp.send_message(msg)
#
#     print("Email sent successfully!")



def send_email(to_email, subject, body, from_email, username, password, server: str, port: int):
    # Create message
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = from_email
    msg['To'] = to_email

    # Connect to Microsoft 365 SMTP
    with smtplib.SMTP(server, port) as server:
        server.ehlo()
        server.starttls()  # Upgrade connection to TLS
        server.login(username, password)
        server.sendmail(from_email, [to_email], msg.as_string())

    print("Email sent!")



def build_success_body(name, item_id, sharepoint_path):
    return (
        f"Hola {name},\n\n"
        f"T'informem que el workflow d'iMarina amb ID {item_id} s'ha completat correctament.\n\n"
        f"El fitxer generat està disponible al SharePoint a la següent ruta:\n"
        f"{sharepoint_path}\n\n"
        f"Per a qualsevol dubte, contacta amb l'equip de Digitalització.\n\n"
        f"Salutacions,\n\n"
        f"(Aquest missatge ha estat auto-generat.)"
    )


def build_error_body(name, item_id):
    return (
        f"Hola {name},\n\n"
        f"T'informem que el teu workflow d'iMarina amb ID {item_id} ha fallat.\n\n"
        f"Si us plau, contacta amb l'equip de Digitalització per a més informació.\n\n"
        f"Salutacions,\n\n"
        f"(Aquest missatge ha estat auto-generat.)"
    )



def mail_process(args):

    smtp_password = read_secret("SMTP_PASSWORD")
    smtp_user = read_secret("SMTP_USERNAME")
    smtp_server = read_secret("SMTP_HOST")
    smtp_port = read_secret("SMTP_PORT")

    # credentials MS GRAPH
    tenant_id = read_secret("TENANT_ID")
    client_id = read_secret("CLIENT_ID")
    client_secret = read_secret("CLIENT_SECRET")
    site_id = read_secret("MS_SITE_ID")
    list_id = read_secret("MS_LIST_ID")

    print("Getting access token...")
    token = get_access_token(tenant_id, client_id, client_secret)

    print(f"Getting creator info for item ID {args.id}...")
    to_email, name = get_creator_email(token, site_id, list_id, args.id)
    print(f"Sending email to: {to_email} ({name})")

    if args.status == "success":
        subject = f"iMarina - Workflow ID {args.id} completat correctament"
        body = build_success_body(name, args.id, args.sharepoint_path)
    else:
        subject = f"iMarina - Workflow ID {args.id} ha fallat"
        body = build_error_body(name, args.id)

    send_email(to_email, subject, body, smtp_user, smtp_user, smtp_password, smtp_server, smtp_port)
    print("Email sent. Process complete.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send iMarina workflow notification email")
    parser.add_argument("--id", required=True, help="MS List item ID")
    parser.add_argument("--status", required=True, choices=["success", "error"], help="Workflow status")
    parser.add_argument("--sharepoint-path", required=False, default="Institutional Strengthening/_Projects/iMarina_load_automation/output", help="SharePoint path of the generated file")
    args = parser.parse_args()


    # print("Sending email with another func")
    # print("To: " + args.author)
    # print("username: " + read_secret("SMTP_USERNAME"))
    # print("password: " + read_secret("SMTP_PASSWORD"))
    # print("port: " + read_secret("SMTP_PORT"))
    # print("Server: " + read_secret("SMTP_SERVER"))
    # send_mail(
    #     to_email=args.author,
    #     subject="test email",
    #     body="a test of email",
    #     from_email=read_secret("SMTP_USERNAME"),
    #     username=read_secret("SMTP_USERNAME"),
    #     password=read_secret("SMTP_PASSWORD"),
    #     server=read_secret("SMTP_SERVER"),
    #     port=read_secret("SMTP_PORT")
    # )

    mail_process(args)







