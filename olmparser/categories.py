import re
import zipfile
from typing import Optional

from olmparser.zip_tree import get_doc_tree

float_regex = r"(\d*)(\.)*(\d+)"
color_regex = f'r:({float_regex}) g:({float_regex}) b:({float_regex})'
color_matcher = re.compile(color_regex)


class Category:
    color_r: float
    color_g: float
    color_b: float
    category_name: str

    def __init__(self, color_r, color_g, color_b, category_name):
        self.color_r = color_r
        self.color_g = color_g
        self.color_b = color_b
        self.category_name = category_name


def parse_categories(zip_file: zipfile.ZipFile) -> list[Category]:
    categories_root_name = "Categories.xml"
    if categories_root_name not in zip_file.namelist():
        return []

    categories_tree = get_doc_tree(zip_file, categories_root_name)
    if categories_tree is None:
        return []

    category_nodes = categories_tree.getroot().iterchildren("*")
    return [parse_category_entry(c) for c in category_nodes]


def parse_category_entry(category_node) -> Optional[Category]:
    category_attributes_tuples = category_node.items()
    if not category_attributes_tuples or len(category_attributes_tuples) is 0:
        return None

    tuple_key_color_tuple_name = "OPFCategoryCopyBackgroundColor"
    tuple_key_category_name = "OPFCategoryCopyName"

    color_tuple = (0, 0, 0)
    category_name = "category_name"
    for category_attribute_tuple in category_attributes_tuples:
        if len(category_attribute_tuple) is not 2:
            continue

        tuple_key = category_attribute_tuple[0]
        tuple_value = category_attribute_tuple[1]

        if tuple_key is tuple_key_color_tuple_name:
            color_tuple = parse_category_color(tuple_value)
        elif tuple_key is tuple_key_category_name:
            category_name = tuple_value

    return Category(color_tuple[0], color_tuple[1], color_tuple[2], category_name)


def parse_category_color(colour_string):
    result = re.search(color_matcher, colour_string)
    if result is None:
        return 0, 0, 0
    else:
        return result.groups()
