import argparse
import requests


def read_secret(name: str) -> str:
    with open(f"secrets/{name}", "r") as f:
        return f.read().strip()


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
    return response.json()["access_token"]


def get_creator_email(token: str, site_id: str, list_id: str, item_id: str) -> tuple[str, str]:
    url = f"https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{list_id}/items/{item_id}?expand=fields"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()

    fields = response.json().get("createdBy", {}).get("user", {})
    email = fields.get("email", "")
    name = fields.get("displayName", "")
    return email, name


def send_email(token: str, sender: str, to_email: str, subject: str, body: str):
    url = f"https://graph.microsoft.com/v1.0/users/{sender}/sendMail"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body,
            },
            "toRecipients": [
                {"emailAddress": {"address": to_email}}
            ],
        }
    }
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    print("Email sent successfully!")


# function SEND EMAIL CORRECT
def build_success_body(name: str, item_id: str, sharepoint_path: str) -> str:
    return (
        f"Hola {name},\n"
        f"\n"
        f"T'informem que el workflow d'iMarina amb ID {item_id} s'ha completat correctament.\n"
        f"\n"
        f"El fitxer generat està disponible al  SharePoint a la següent ruta:\n"
        f"{sharepoint_path}\n"
        f"\n"
        f"Per a qualsevol dubte, contacta amb l'equip de Digitalització.\n"
        f"\n"
        f"Salutacions,\n"
        f"\n"
        f"(Aquest missatge ha estat auto-generat.)"
    )


# function SEND EMAIL ERROR
def build_error_body(name: str, item_id: str) -> str:
    return (
        f"Hola {name},\n"
        f"\n"
        f"T'informem que el teu workflow d'iMarina amb ID {item_id} ha fallat.\n"
        f"\n"
        f"Si us plau, contacta amb l'equip de Digital Transformation per a més informació.\n"
        f"\n"
        f"Salutacions,\n"
        f"\n"
        f"(Aquest missatge ha estat auto-generat)"
    )


def mail_process(args):
    # Read secrets
    tenant_id = read_secret("TENANT_ID")
    client_id = read_secret("CLIENT_ID")
    client_secret = read_secret("CLIENT_SECRET")
    site_id = read_secret("MS_SITE_ID")
    list_id = read_secret("MS_LIST_ID")
    sender = read_secret("SENDER_EMAIL")

    # Get access token
    print("Getting access token...")
    token = get_access_token(tenant_id, client_id, client_secret)

    # Get creator email and name
    print(f"Getting creator info for item ID {args.id}...")
    to_email, name = get_creator_email(token, site_id, list_id, args.id)
    print(f"Sending email to: {to_email} ({name})")

    # Build email content based on status
    if args.status == "success":
        subject = f"iMarina - Workflow ID {args.id} completat correctament"
        body = build_success_body(name, args.id, args.sharepoint_path)
    else:
        subject = f"iMarina - Workflow ID {args.id} ha fallat"
        body = build_error_body(name, args.id)

    # Send email
    send_email(token, sender, to_email, subject, body)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send iMarina workflow notification email")
    parser.add_argument("--id", required=True, help="MS List item ID")
    parser.add_argument("--status", required=True, choices=["success", "error"], help="Workflow status")
    parser.add_argument("--sharepoint-path", required=False, default="Institutional Strengthening/_Projects/iMarina_load_automation/output", help="SharePoint path of the generated file")
    args = parser.parse_args()

    mail_process(args)

