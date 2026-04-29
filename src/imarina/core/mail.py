import argparse
import requests
import smtplib
from email.message import EmailMessage
from email.mime.text import MIMEText
from secret import read_secret



def send_mail2(username, password, to, host, port, subject, content):
    SMTP_SERVER = host
    SMTP_PORT = port
    USERNAME = username
    PASSWORD = password

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = USERNAME
    msg["To"] = to
    msg.set_content(content)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()  # Use TLS
        smtp.login(USERNAME, PASSWORD)
        smtp.send_message(msg)

    print("Email sent successfully!")



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



def mail_process(sharepoint_path, args, item_id):

    smtp_password = read_secret("SMTP_PASSWORD")
    smtp_user = read_secret("SMTP_USERNAME")
    smtp_server = read_secret("SMTP_HOST")
    smtp_port = read_secret("SMTP_PORT")

    subject = f"Imarina  - Workflow  \"{args.title}\" amb ID {str(args.request)}  completat amb èxit"
    body = ("Hola!\n"
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

    send_mail(args.author_email,
              subject,
              body,
              smtp_user,
              smtp_user,
              smtp_password,
              smtp_server,
              smtp_port)

    print("Email sent. Process complete. ")




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Send iMarina workflow notification email")
    parser.add_argument("--id", required=True, help="MS List item ID")
    parser.add_argument("--email", required=True, help="Creator email")
    parser.add_argument("--name", required=True, help="Creator name")
    parser.add_argument("--status", required=True, choices=["success", "error"], help="Workflow status")
    parser.add_argument("--sharepoint-path", required=False, default="Institutional Strengthening/_Projects/iMarina_load_automation/output", help="SharePoint path of the generated file")
    args = parser.parse_args()


    print("Sending email with another func")
    print("To: " + args.author)
    print("username: " + read_secret("SMTP_USERNAME"))
    print("password: " + read_secret("SMTP_PASSWORD"))
    print("port: " + read_secret("SMTP_PORT"))
    print("Server: " + read_secret("SMTP_SERVER"))
    send_mail(
        to_email=args.author,
        subject="test email",
        body="a test of email",
        from_email=read_secret("SMTP_USERNAME"),
        username=read_secret("SMTP_USERNAME"),
        password=read_secret("SMTP_PASSWORD"),
        server=read_secret("SMTP_SERVER"),
        port=read_secret("SMTP_PORT")
    )

    mail_process(args)







