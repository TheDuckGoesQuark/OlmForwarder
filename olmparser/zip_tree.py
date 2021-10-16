import zipfile
from pprint import pprint

from lxml import etree


def get_doc_tree(zip_file: zipfile.ZipFile, entry_name: str):
    def parse_huge_tree():
        p = etree.XMLParser(huge_tree=True)
        try:
            return etree.parse(fh, p)
        except etree.XMLSyntaxError:
            # probably corrupt
            return None

    with zip_file.open(entry_name) as fh:
        try:
            return etree.parse(fh)
        except etree.XMLSyntaxError:
            return parse_huge_tree()


def print_doc_tree(zip_file: zipfile.ZipFile, root: str):
    paths = zip_file.namelist()
    entries = [path for path in paths if path.startswith(f'{root}/')]
    pprint(entries)
