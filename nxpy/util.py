import re

# Globals
tag_pattern = re.compile(r'({.*})?(.*)')
whitespace_pattern = re.compile(r'[\n\r\s]+')
