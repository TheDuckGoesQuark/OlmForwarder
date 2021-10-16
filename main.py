import sys
from pprint import pprint

import yaml

from email_forwarder.email_client import SMTPEmailClient, EmailClientConfig
from olmparser.config import OlmParserConfig
from olmparser.olm import OlmParser, OlmEmailIterator


def __main__():
    if len(sys.argv) < 3:
        print(f'Usage: ./{sys.argv[0]} config_file_path olm_archive_path')
        return 1

    config_file_path = sys.argv[1]
    olm_file_path = sys.argv[2]
    config = yaml.safe_load(open(config_file_path))

    olm_parser = OlmParserConfig(config['parser'])
    parser = OlmParser(olm_file_path)
    print(f'Found {parser.count()} items in archive')

    categories = parser.parse_categories()
    local_parser = parser.get_local_parser()
    account_parser = parser.get_account_parser(olm_parser.get_accounts_to_include()[0])

    # with SMTPEmailClient(EmailClientConfig(config['email'])) as email_client:
    #     for thing in email_iterator:
    #         try:
    #             pprint(thing[0].category)
    #         except AttributeError as e:
    #             continue
    #     # email_client.send()


__main__()
