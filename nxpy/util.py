import re
from lxml import etree


def new_ele(tag, attrs={}, **extra):
    etree.Element(tag, attrs, **extra)


def sub_ele(parent, tag, attrs={}, **extra):
    etree.SubElement(parent, tag, attrs, **extra)

# Globals
tag_pattern = re.compile(r'({.*})?(.*)')
whitespace_pattern = re.compile(r'[\n\r\s]+')
