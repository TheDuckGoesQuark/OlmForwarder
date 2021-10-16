import smtplib


class EmailSenderConfig:
    config_dict: dict[str]

    def __init__(self, config_dict):
        self.config_dict = config_dict

    def get_email_server_address(self):
        return self.config_dict["server_address"]

    def get_email_username(self):
        return self.config_dict["username"]

    def get_email_password(self):
        return self.config_dict["password"]

    def get_smtp_port(self):
        return self.config_dict["smtp_port"]

    def is_smtp_encryption_required(self):
        return self.config_dict["smtp_encryption_required"]


class EmailSender:
    config: EmailSenderConfig

    def __init__(self, email_sender_config: EmailSenderConfig):
        self.config = email_sender_config

    def send(self, to_address, email_message):
        email_server = smtplib.SMTP(self.config.get_email_server_address())
        email_server.sendmail(self.config.get_email_username(), list(to_address), email_message)
        email_server.quit()
