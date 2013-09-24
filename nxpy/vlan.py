import re
from lxml import etree
from nxpy.util import tag_pattern, whitespace_pattern


class Vlan:

    def __repr__(self):
        return "Name %s, Vlan-Id: %s" % (self.name, self.vlan_id)

    def __init__(self):
        self.name = ''
        self.vlan_id = ''
        self.operation = None

    def export(self):
        if self.operation:
            vlan = etree.Element('vlan', {'operation': self.operation})
        else:
            vlan = etree.Element('vlan')
        if self.name:
            etree.SubElement(vlan, "name").text = self.name
        if self.vlan_id:
            etree.SubElement(vlan, "vlan-id").text = self.vlan_id
        if self.name and self.vlan_id:
            return vlan
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
        elif nodeName_ == 'vlan-id':
            vlanid_ = child_.text
            vlanid_ = re.sub(whitespace_pattern, " ", vlanid_).strip()
            self.vlan_id = vlanid_
