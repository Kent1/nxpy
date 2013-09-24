import re
from lxml import etree
from nxpy import tag_pattern, whitespace_pattern


class Unit:

    def __repr__(self):
        return "Name %s, Description: %s" % (self.name, self.description)

    def __init__(self):
        self.name = ''
        self.description = ''
        self.vlan_id = ''
        # family: {'name':(one of inet, inet6, mpls, iso...), 'addresses':[],
        # 'mtu':'', 'accounting': {}, 'vlan_members':['',''],
        # 'vlan_members_operation':'delete' or 'replace' or 'merge'(this is the
        # default so omit)}
        self.family = []

    def export(self):
        unit = etree.Element('unit')
        if self.name:
            etree.SubElement(unit, "name").text = self.name
        if self.description:
            etree.SubElement(unit, "description").text = self.description
        if self.vlan_id:
            etree.SubElement(unit, "vlan-id").text = self.vlan_id
        if len(self.family):
            family = etree.Element("family")
            for member in self.family:
                try:
                    if member['name']:
                        mem_name = etree.Element(member['name'])
                except:
                    pass
                try:
                    if len(member['addresses']):
                        for address in member['addresses']:
                            addr = etree.Element('address')
                            etree.SubElement(addr, "name").text = address
                            mem_name.append(addr)
                except:
                    pass
                try:
                    if member['mtu']:
                        etree.SubElement(mem_name, "mtu").text = member['mtu']
                    family.append(mem_name)
                except:
                    pass
                try:
                    if member['vlan_members']:
                        try:
                            if member['vlan_members_operation']:
                                operation = member['vlan_members_operation']
                        except:
                            operation = None
                        ethernet_switching = etree.SubElement(
                            family, 'ethernet-switching')
                        vlan = etree.SubElement(ethernet_switching, 'vlan')
                        for vlan_item in member['vlan_members']:
                            if operation:
                                vmem = etree.SubElement(
                                    vlan, 'members', {'operation': operation})
                            else:
                                vmem = etree.SubElement(vlan, 'members')
                            vmem.text = vlan_item
                except:
                    pass
            unit.append(family)
        if len(unit.getchildren()):
            return unit
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
        elif nodeName_ == 'description':
            description_ = child_.text
            description_ = re.sub(
                whitespace_pattern, " ", description_).strip()
            self.description = description_
        elif nodeName_ == 'family':
            vlan_unit_list = []
            family_dict = {}
            for node in child_:
                childName_ = tag_pattern.match(node.tag).groups()[-1]
                # *************** ETHERNET-SWITCHING ****************
                if childName_ == 'ethernet-switching':
                    for grandChild_ in node:
                        grandchildName_ = tag_pattern.match(
                            grandChild_.tag).groups()[-1]
                        if grandchildName_ == 'port-mode':
                            pmode = grandChild_.text
                            pmode = re.sub(
                                whitespace_pattern, " ", pmode).strip()
                            family_dict['port-mode'] = pmode
                        elif grandchildName_ == 'vlan':
                            for vlan_member in grandChild_:
                                vlanmem = vlan_member.text
                                vlanmem = re.sub(
                                    whitespace_pattern, " ", vlanmem).strip()
                                vlan_unit_list.append(vlanmem)
                            family_dict['vlan_members'] = vlan_unit_list
                    self.family.append(family_dict)
