import sys

import yaml

from olmforwarder.email_sender import EmailSender
from olmforwarder.olm import OlmParser, OlmEmailIterator


def __main__():
    config_file_path = sys.argv[1]
    olm_file_path = sys.argv[2]
    config = yaml.safe_load(open(config_file_path))

    email_sender = EmailSender(config.email)

    olm_parser = OlmParser(olm_file_path)
    email_iterator = OlmEmailIterator(olm_parser)


__main__()
