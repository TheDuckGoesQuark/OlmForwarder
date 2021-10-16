import smtplib


class EmailClientConfig:
    config_dict: dict[str]

    def __init__(self, config_dict: dict[str]):
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


class SMTPEmailClient:
    _email_server: smtplib.SMTP
    _config: EmailClientConfig

    def __init__(self, email_sender_config: EmailClientConfig):
        self._config = email_sender_config

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._disconnect()

    def _connect(self):
        self._email_server = smtplib.SMTP(self._config.get_email_server_address(), self._config.get_smtp_port())
        self._email_server.ehlo()
        self._email_server.starttls()
        self._email_server.ehlo()
        self._email_server.login(self._config.get_email_username(), self._config.get_email_password())

    def send(self, to_address, email_message):
        self._email_server.sendmail(self._config.get_email_username(), list(to_address), email_message)

    def _disconnect(self):
        if self._email_server is not None:
            self._email_server.quit()
