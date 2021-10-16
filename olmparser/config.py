from enum import Enum


class ImportableType(Enum):
    EMAIL = "email"
    CALENDAR_EVENT = "calendar_event"
    CONTACT = "contact"


class OlmParserConfig:
    config_dict: dict[str]

    def __init__(self, config_dict: dict[str]):
        self.config_dict = config_dict

    def get_types_to_import(self) -> list[ImportableType]:
        return self.config_dict["types_to_import"]

    def include_attachments(self) -> bool:
        return self.config_dict["include_attachments"]

    def include_local(self) -> bool:
        return self.config_dict["include_local"]

    def get_accounts_to_include(self) -> list[str]:
        return self.config_dict["accounts_to_include"]
