import os
from dotenv import load_dotenv
from hydra_email_manager import HydraEmailManager

class Email:
    def __init__(self, username=None, password=None):
        load_dotenv()
        self.username = username if username is not None else os.getenv("EMAIL_USER")
        self.password = password if password is not None else os.getenv("EMAIL_PASSWORD")
        self.manager = HydraEmailManager()
        self.fez_login = self.manager.verificar_senha(self.username, self.password)
        if self.fez_login:
            print("✅ Login bem-sucedido.")
        else:
            print("❌ Login incorreto!")

    def enviar_email(self, user_from, subject, body, attachment=None):
        if not self.fez_login:
            raise Exception("Login não realizado. Verifique suas credenciais.")
        self.manager.enviar_email(self.username, user_from, subject, body, attachment)

    def baixar_emails(self, folder_id, is_read=None, file_format="eml", subject_filter=None, from_filter=None, body_filter=None, order_by=None, limit=10, only_attachments=False, mark_as_read=False):
        if not self.fez_login:
            raise Exception("Login não realizado. Verifique suas credenciais.")
        return self.manager.baixar_emails(self.username, folder_id, is_read, file_format, subject_filter, from_filter, body_filter, order_by, limit, only_attachments, mark_as_read)

    def marcar_email_como_lido(self, email_id):
        if not self.fez_login:
            raise Exception("Login não realizado. Verifique suas credenciais.")        
        self.manager.marcar_email_como_lido(self.username, email_id)

    def obter_id_pastas(self, parent_id=None):
        if not self.fez_login:
            raise Exception("Login não realizado. Verifique suas credenciais.")
        self.manager.obter_id_pastas(self.username, parent_id)

    def login(self, username, password):
        self.manager.verificar_senha(username, password)
        if self.manager.verificar_senha(username, password):
            return True
        else:
            return False

if __name__ == "__main__":
    email = Email()
    # Example usage
    res = email.baixar_emails(folder_id='AQMkADdiMDVjODcyLTkyMGYtNDkzYy1iNDhlLWYwOWNiZmMwOWMyMgAALgAAA6UWk04pGmtGo6Qh8ekR_hEBAOlav09_btVNjQXvUil-euQAAAIBDAAAAA==', from_filter='noreply@pacey.com.br', limit=20)