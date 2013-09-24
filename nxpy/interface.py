import re
from lxml import etree
from nxpy.unit import Unit
from nxpy.util import tag_pattern, whitespace_pattern


class Interface(object):

    def __repr__(self):
        return "Name %s, Description: %s" % (self.name, self.description)

    def __init__(self, name=None, description=None):
        self.name = name
        self.bundle = ''
        self.description = description
        self.vlantagging = ''
        self.tunneldict = []
        # Unit dict is a list of dictionaries containing units to
        # interfaces, should be index like
        # {
        # 'unit': 'name',
        # 'description': 'foo',
        # 'vlanid': 'bar',
        # 'addresses': ['IPv4addresses', 'IPv6addresses']
        # }
        self.unitdict = []

    def export(self):
        ifce = etree.Element('interface')
        if self.name:
            etree.SubElement(ifce, "name").text = self.name
        if self.description:
            etree.SubElement(ifce, "description").text = self.description
        if len(self.unitdict):
            for unit in self.unitdict:
                if unit:
                    ifce.append(unit.export())
        if len(ifce.getchildren()):
            return ifce
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = tag_pattern.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):
        if nodeName_ == 'name':
            name_ = child_.text
            name_ = re.sub(whitespace_pattern, " ", name_).strip()
            self.name = name_
        elif nodeName_ == 'description':
            description_ = child_.text
            description_ = re.sub(whitespace_pattern, " ", description_).strip()
            self.description = description_
        elif nodeName_ == 'unit':
            obj_ = Unit()
            obj_.build(child_)
            self.unitdict.append(obj_)
