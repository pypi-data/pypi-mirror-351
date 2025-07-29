import os
import base64
import requests
import urllib.parse
from dotenv import load_dotenv
from email import policy
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.encoders import encode_base64
from email.mime.multipart import MIMEMultipart
from msal import ConfidentialClientApplication

class HydraEmailManager:
    def __init__(self):
        load_dotenv()
        
        self.TENANT_ID = os.getenv("TENANT_ID")
        self.CLIENT_ID = os.getenv("CLIENT_ID")
        self.CLIENT_SECRET = os.getenv("CLIENT_SECRET")
        self.AUTHORITY = f"https://login.microsoftonline.com/{self.TENANT_ID}"
        self.SCOPE = ["https://graph.microsoft.com/.default"]
        self.app = ConfidentialClientApplication(self.CLIENT_ID, self.CLIENT_SECRET, self.AUTHORITY)
        self.token = self.app.acquire_token_for_client(self.SCOPE)
        self.headers = {"Authorization": f"Bearer {self.token['access_token']}", "Content-Type": "application/json"} if "access_token" in self.token else None

    def verificar_senha(self, username, password):
        token = self.app.acquire_token_by_username_password(username, password, scopes=self.SCOPE)
        if "access_token" in token:
            return True
        else:
            return False

    def enviar_email(self, user_email, user_from, subject, body, attachment=None):
        if self.headers:
            # Separa os destinatários por ';' e remove espaços extras
            if ";" in user_from:
                destinatarios = [addr.strip() for addr in user_from.split(";") if addr.strip()]
            else:
                destinatarios = [user_from.strip()]
    
            email_data = {
                "message": {
                    "subject": subject,
                    "body": {
                        "contentType": "HTML",
                        "content": f"{body}<br>"
                    },
                    "toRecipients": [
                        {"emailAddress": {"address": addr}} for addr in destinatarios
                    ]
                }
            }
    
            if attachment:
                with open(attachment, "rb") as f:
                    attachment_content = f.read()
                attachment_data = {
                    "@odata.type": "#microsoft.graph.fileAttachment",
                    "name": os.path.basename(attachment),
                    "contentBytes": base64.b64encode(attachment_content).decode('utf-8')
                }
                email_data["message"]["attachments"] = [attachment_data]
    
            url_send = f"https://graph.microsoft.com/v1.0/users/{user_email}/sendMail"
            response_send = requests.post(url_send, headers=self.headers, json=email_data)
    
            if response_send.status_code == 202:
                print("Email enviado com sucesso!")
            else:
                print("Erro ao enviar email:", response_send.json())
        else:
            print("Erro ao obter token:", self.token.get("error_description")) 
    
    def baixar_emails(self, user_email, folder_id, is_read=None, file_format="eml", subject_filter=None, from_filter=None, body_filter=None, order_by=None, limit=10, only_attachments=False, mark_as_read=False):
        if self.headers:
            url = f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/{folder_id}/messages?"
            filters = []
    
            if is_read is not None:
                filters.append(f"isRead eq {str(is_read).lower()}")
            if subject_filter:
                filters.append(f"contains(subject, '{subject_filter}')")
            if from_filter:
                from_filter = from_filter.replace('\'', '\'\'')
                filters.append(f"from/emailAddress/address eq '{urllib.parse.quote(from_filter)}'")
            if body_filter:
                filters.append(f"contains(body/content, '{body_filter}')")
            if filters:
                url += f"$filter={' and '.join(filters)}"
            if order_by:
                url += f"&$orderby={order_by}"
            if limit:
                url += f"&$top={limit}"
    
            response = requests.get(url, headers=self.headers)
    
            if response.status_code == 200:
                emails = response.json().get("value", [])
                os.makedirs("emails", exist_ok=True)
                email_data = []
                for email in emails:
                    subject = email['subject']
                    from_address = email['from']['emailAddress']['address']
                    body = email['body']['content']
                    print(f"De: {from_address}")
                    print(f"Assunto: {subject}")
                    print(f"Mensagem: {body}")
                    print("="*50)
    
                    msg = MIMEMultipart("related")
                    msg['From'] = from_address
                    msg['To'] = user_email
                    msg['Subject'] = subject
    
                    msg_alternative = MIMEMultipart("alternative")
                    msg.attach(msg_alternative)
                    msg_alternative.attach(MIMEText(body, 'html'))
    
                    attachments_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{email['id']}/attachments"
                    attachments_response = requests.get(attachments_url, headers=self.headers)
                    if attachments_response.status_code == 200:
                        attachments = attachments_response.json().get("value", [])
                        for attachment in attachments:
                            if attachment["@odata.type"] == "#microsoft.graph.fileAttachment" and attachment["contentType"] == "application/pdf":
                                attachment_content = base64.b64decode(attachment["contentBytes"])
                                part = MIMEBase('application', 'octet-stream')
                                part.set_payload(attachment_content)
                                encode_base64(part)
                                part.add_header('Content-Disposition', f'attachment; filename="{attachment["name"]}"')
                                msg.attach(part)
                                pdf_filename = os.path.join("emails", attachment["name"])
                                with open(pdf_filename, "wb") as pdf_file:
                                    pdf_file.write(attachment_content)
    
                    if not only_attachments:
                        filename = "".join([c if c.isalnum() or c in " ._-()" else "_" for c in subject]) + f".{file_format}"
                        filepath = os.path.join("emails", filename)
    
                        if file_format == "eml":
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(msg.as_string(policy=policy.default))
                        elif file_format == "html":
                            with open(filepath, "w", encoding="utf-8") as file:
                                file.write(body)
                    
                    email_data.append({
                        "id": email['id'],
                        "from": from_address,
                        "subject": subject,
                        "body": body,
                        "attachments": [attachment["name"] for attachment in attachments if attachment["@odata.type"] == "#microsoft.graph.fileAttachment" and attachment["contentType"] == "application/pdf"]
                    })
    
                    # Marcar como lido se solicitado
                    if mark_as_read and not email.get("isRead", False):
                        patch_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{email['id']}"
                        patch_data = {"isRead": True}
                        patch_response = requests.patch(patch_url, headers=self.headers, json=patch_data)
                        if patch_response.status_code == 200:
                            print(f"Email {email['id']} marcado como lido.")
                        else:
                            print(f"Falha ao marcar como lido: {email['id']}")
    
                return email_data
            else:
                print("Erro:", response.json())
        else:
            print("Erro ao obter token:", self.token.get("error_description"))

    def marcar_email_como_lido(self, user_email, email_id):
        """
        Marca um email específico como lido.
        """
        if self.headers:
            patch_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{email_id}"
            patch_data = {"isRead": True}
            patch_response = requests.patch(patch_url, headers=self.headers, json=patch_data)
            if patch_response.status_code == 200:
                print(f"Email {email_id} marcado como lido.")
                return True
            else:
                print(f"Falha ao marcar como lido: {email_id} - {patch_response.json()}")
                return False
        else:
            print("Erro ao obter token:", self.token.get("error_description"))
            return False

    def obter_id_pastas(self, user_email, parent_folder_id=None):
        if self.headers:
            if parent_folder_id:
                url = f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/{parent_folder_id}/childFolders"
            else:
                url = f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders"
            
            while url:
                response = requests.get(url, headers=self.headers)
                if response.status_code == 200:
                    folders = response.json().get("value", [])
                    for folder in folders:
                        print(f"Nome da Pasta: {folder['displayName']}")
                        print(f"ID da Pasta: {folder['id']}")
                        print("="*50)
                    # Verifica se há uma próxima página de resultados
                    url = response.json().get("@odata.nextLink")
                else:
                    print("Erro:", response.json())
                    break
        else:
            print("Erro ao obter token:", self.token.get("error_description"))

    def limpar_pasta(self, user_email, folder_id):
        confirm = input(f"Tem certeza de que deseja limpar a pasta com ID {folder_id} para o usuário {user_email}? (s/n): ")
        if confirm.lower() != 's':
            print("Operação cancelada.")
            return

        if self.headers:
            url = f"https://graph.microsoft.com/v1.0/users/{user_email}/mailFolders/{folder_id}/messages"
            response = requests.get(url, headers=self.headers)

            if response.status_code == 200:
                emails = response.json().get("value", [])
                for email in emails:
                    email_id = email['id']
                    delete_url = f"https://graph.microsoft.com/v1.0/users/{user_email}/messages/{email_id}"
                    delete_response = requests.delete(delete_url, headers=self.headers)
                    if delete_response.status_code == 204:
                        print(f"Email com ID {email_id} deletado com sucesso.")
                    else:
                        print(f"Erro ao deletar email com ID {email_id}: {delete_response.json()}")
            else:
                print("Erro ao obter emails:", response.json())
        else:
            print("Erro ao obter token:", self.token.get("error_description"))

    def obter_grupos_usuario(self, user_email):
        if self.headers:
            url = f"https://graph.microsoft.com/v1.0/users/{user_email}/memberOf"
            response = requests.get(url, headers=self.headers)
    
            if response.status_code == 200:
                grupos = response.json().get("value", [])
                for grupo in grupos:
                    print(grupo)
                    print(f"Nome do Grupo: {grupo.get('displayName', 'N/A')}")
                    print(f"ID do Grupo: {grupo.get('id', 'N/A')}")
                    print("=" * 50)
                return grupos
            else:
                print("Erro ao obter grupos:", response.json())
        else:
            print("Erro ao obter token:", self.token.get("error_description"))