#!/usr/bin/env python
# Copyright 2011 Leonidas Poulopoulos (GRNET S.A - NOC)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import re
import os
from lxml import etree


def new_ele(tag, attrs={}, **extra):
    etree.Element(tag, attrs, **extra)


def sub_ele(parent, tag, attrs={}, **extra):
    etree.SubElement(parent, tag, attrs, **extra)

# Globals
Tag_pattern_ = re.compile(r'({.*})?(.*)')
STRING_CLEANUP_PAT = re.compile(r"[\n\r\s]+")


class Device(object):

    def __init__(self):
        self.name = ''
        self.domain_name = ''
        self.interfaces = []
        self.vlans = []
        self.routing_options = []

    def export(self, netconf_config=False):
        config = new_ele("configuration")
        device = new_ele('system')
        if self.name:
            sub_ele(device, "host-name").text = self.name
        if self.domain_name:
            sub_ele(device, "domain-name").text = self.domain_name
        if len(device.getchildren()):
            config.append(device)
        interfaces = new_ele('interfaces')
        if len(self.interfaces):
            for interface in self.interfaces:
                if (interface):
                    interfaces.append(interface.export())
            config.append(interfaces)
        vlans = new_ele('vlans')
        if len(self.vlans):
            for vlan in self.vlans:
                if (vlan):
                    vlans.append(vlan.export())
            config.append(vlans)
        routing_options = new_ele('routing-options')
        if len(self.routing_options):
            for ro in self.routing_options:
                if (ro):
                    routing_options.append(ro.export())
            config.append(routing_options)
        if netconf_config:
            conf = new_ele("config")
            conf.append(config)
            config = conf
        if len(config.getchildren()):
            return config
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):
        if nodeName_ == 'interfaces':
            for node in child_:
                obj_ = Interface()
                obj_.build(node)
                self.interfaces.append(obj_)
        if nodeName_ == 'vlans':
            for node in child_:
                obj_ = Vlan()
                obj_.build(node)
                self.vlans.append(obj_)
        if nodeName_ == 'routing-options':
            for node in child_:
                childName_ = Tag_pattern_.match(node.tag).groups()[-1]
                # *************** FLOW ****************
                if childName_ == 'flow':
                    obj_ = Flow()
                    obj_.build(node)
                    self.routing_options.append(obj_)


class DeviceDiff(Device):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                DeviceDiff, cls).__new__(cls, *args, **kwargs)
        return cls._instance

devdiff = DeviceDiff()


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

    def get_descr(self):
        return self.description

    def set_descr(self, x):
        global devdiff
        self.description = x
        intdiff = Interface(name=self.name, description=self.description)
        if len(devdiff.interfaces) > 0:
            deviffIntNames = [i.name for i in devdiff.interfaces]
            if self.name in deviffIntNames:
                for interface in devdiff.interfaces:
                    if interface.name == self.name:
                        devdiff.interfaces.remove(interface)
        devdiff.interfaces.append(intdiff)
    # The new_description attribute initiates the DeviceDiff class
    new_description = property(get_descr, set_descr)

    def export(self):
        ifce = new_ele('interface')
        if self.name:
            sub_ele(ifce, "name").text = self.name
        if self.description:
            sub_ele(ifce, "description").text = self.description
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
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):
        if nodeName_ == 'name':
            name_ = child_.text
            name_ = re.sub(STRING_CLEANUP_PAT, " ", name_).strip()
            self.name = name_
        elif nodeName_ == 'description':
            description_ = child_.text
            description_ = re.sub(
                STRING_CLEANUP_PAT, " ", description_).strip()
            self.description = description_
        elif nodeName_ == 'unit':
            obj_ = Unit()
            obj_.build(child_)
            self.unitdict.append(obj_)


class Vlan:

    def __repr__(self):
        return "Name %s, Vlan-Id: %s" % (self.name, self.vlan_id)

    def __init__(self):
        self.name = ''
        self.vlan_id = ''
        self.operation = None

    def export(self):
        if self.operation:
            vlan = new_ele('vlan', {'operation': self.operation})
        else:
            vlan = new_ele('vlan')
        if self.name:
            sub_ele(vlan, "name").text = self.name
        if self.vlan_id:
            sub_ele(vlan, "vlan-id").text = self.vlan_id
        if self.name and self.vlan_id:
            return vlan
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):
        if nodeName_ == 'name':
            name_ = child_.text
            name_ = re.sub(STRING_CLEANUP_PAT, " ", name_).strip()
            self.name = name_
        elif nodeName_ == 'vlan-id':
            vlanid_ = child_.text
            vlanid_ = re.sub(STRING_CLEANUP_PAT, " ", vlanid_).strip()
            self.vlan_id = vlanid_


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
        unit = new_ele('unit')
        if self.name:
            sub_ele(unit, "name").text = self.name
        if self.description:
            sub_ele(unit, "description").text = self.description
        if self.vlan_id:
            sub_ele(unit, "vlan-id").text = self.vlan_id
        if len(self.family):
            family = new_ele("family")
            for member in self.family:
                try:
                    if member['name']:
                        mem_name = new_ele(member['name'])
                except:
                    pass
                try:
                    if len(member['addresses']):
                        for address in member['addresses']:
                            addr = new_ele('address')
                            sub_ele(addr, "name").text = address
                            mem_name.append(addr)
                except:
                    pass
                try:
                    if member['mtu']:
                        sub_ele(mem_name, "mtu").text = member['mtu']
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
                        ethernet_switching = sub_ele(
                            family, 'ethernet-switching')
                        vlan = sub_ele(ethernet_switching, 'vlan')
                        for vlan_item in member['vlan_members']:
                            if operation:
                                vmem = sub_ele(
                                    vlan, 'members', {'operation': operation})
                            else:
                                vmem = sub_ele(vlan, 'members')
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
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):

        if nodeName_ == 'name':
            name_ = child_.text
            name_ = re.sub(STRING_CLEANUP_PAT, " ", name_).strip()
            self.name = name_
        elif nodeName_ == 'vlan-id':
            vlanid_ = child_.text
            vlanid_ = re.sub(STRING_CLEANUP_PAT, " ", vlanid_).strip()
            self.vlan_id = vlanid_
        elif nodeName_ == 'description':
            description_ = child_.text
            description_ = re.sub(
                STRING_CLEANUP_PAT, " ", description_).strip()
            self.description = description_
        elif nodeName_ == 'family':
            vlan_unit_list = []
            family_dict = {}
            for node in child_:
                childName_ = Tag_pattern_.match(node.tag).groups()[-1]
                # *************** ETHERNET-SWITCHING ****************
                if childName_ == 'ethernet-switching':
                    for grandChild_ in node:
                        grandchildName_ = Tag_pattern_.match(
                            grandChild_.tag).groups()[-1]
                        if grandchildName_ == 'port-mode':
                            pmode = grandChild_.text
                            pmode = re.sub(
                                STRING_CLEANUP_PAT, " ", pmode).strip()
                            family_dict['port-mode'] = pmode
                        elif grandchildName_ == 'vlan':
                            for vlan_member in grandChild_:
                                vlanmem = vlan_member.text
                                vlanmem = re.sub(
                                    STRING_CLEANUP_PAT, " ", vlanmem).strip()
                                vlan_unit_list.append(vlanmem)
                            family_dict['vlan_members'] = vlan_unit_list
                    self.family.append(family_dict)


class Flow(object):

    def __init__(self):
        self.routes = []

    def export(self):
        flow = new_ele('flow')
        if len(self.routes):
            for route in self.routes:
                flow.append(route.export())
            return flow
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):
        if nodeName_ == 'route':
            obj_ = Route()
            obj_.build(child_)
            self.routes.append(obj_)


class Route(object):

    def __init__(self):
        self.name = ''
        self.operation = None
        self.match = {
            "destination": [],
            "source": [],
            "protocol": [],
            "port": [],
            "destination-port": [],
            "source-port": [],
            "icmp-code": [],
            "icmp-type": [],
            "tcp-flags": [],
            "packet-length": [],
            "dscp": [],
            "fragment": []
        }
        ''' Match is a dict with list values
        example: self. match = {
            "destination": [<ip-prefix(es)>],
            "source": [<ip-prefix(es)>],
            "protocol": [<numeric-expression(s)>],
            "port": [<numeric-expression(s)>],
            "destination-port": [<numeric-expression(s)>]
            "source-port": [<numeric-expression(s)>],
            "icmp-code": [<numeric-expression(s)>],
            "icmp-type": [<numeric-expression(s)>],
            "tcp-flags": [<bitwise-expression(s)>],
            "packet-length": [<numeric-expression(s)>],
            "dscp": [<numeric-expression(s)>],
            "fragment": [
                "dont-fragment"
                "not-a-fragment"
                "is-fragment"
                "first-fragment"
                "last-fragment"
            ]
        '''
        self.then = {
            "accept": False,
            "discard": False,
            "community": False,
            "next-term": False,
            "rate-limit": False,
            "sample": False,
            "routing-instance": False
        }
        '''Then is a dict (have to see about this in the future:
        self.then = {
        "accept": True/False,
        "discard": True/False,
        "community": "<name>"/False,
        "next-term": True/False,
        "rate-limit": <rate>/False,
        "sample": True/False,
        "routing-instance": "<RouteTarget extended community>"
        }
        '''

    def export(self):
        if self.operation:
            ro = new_ele('route', {'operation': self.operation})
        else:
            ro = new_ele('route')
        if self.name:
            sub_ele(ro, "name").text = self.name
        match = new_ele("match")
        for key in self.match:
            if self.match[key]:
                for value in self.match[key]:
                    sub_ele(match, key).text = value
        if match.getchildren():
            ro.append(match)
        then = new_ele("then")
        for key in self.then:
            if self.then[key]:
                if self.then[key] is not True and self.then[key] is not False:
                    sub_ele(then, key).text = self.then[key]
                else:
                    sub_ele(then, key)
        if then.getchildren():
            ro.append(then)
        if ro.getchildren():
            return ro
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = Tag_pattern_.match(child.tag).groups()[-1]
            self.buildChildren(child, nodeName_)

    def buildChildren(self, child_, nodeName_, from_subclass=False):
        if nodeName_ == 'name':
            name_ = child_.text
            name_ = re.sub(STRING_CLEANUP_PAT, " ", name_).strip()
            self.name = name_
        elif nodeName_ == 'match':
            for grandChild_ in child_:
                grandChildName_ = Tag_pattern_.match(
                    grandChild_.tag).groups()[-1]
                grandChildText = grandChild_.text
                grandChildText = re.sub(
                    STRING_CLEANUP_PAT, " ", grandChildText).strip()
                self.match[grandChildName_].append(grandChildText)
        elif nodeName_ == 'then':
            for grandChild_ in child_:
                grandChildName_ = Tag_pattern_.match(
                    grandChild_.tag).groups()[-1]
                self.then[grandChildName_] = True


class Parser(object):

    def __init__(self, confile=None):
        self.confile = confile

    def export(self):
        if self.confile:
            confile = self.confile
            if os.path.isfile(confile):
                # probably it's a file...
                configuration = self.parse()
            else:
                configuration = self.parseString()
            return configuration
        else:
            return None

    def parsexml_(self, *args, **kwargs):
        if 'parser' not in kwargs:
            kwargs['parser'] = etree.ETCompatXMLParser()
        doc = etree.parse(*args, **kwargs)
        return doc

    def parse(self):
        '''Normally this would be an rpc_reply in case of netconf invoking or
        a configuration element in case of normal parsing'''
        doc = self.parsexml_(self.confile)
        rootNode = doc.getroot()
        # NetCONF invoked
        rootNodeTag = Tag_pattern_.match(rootNode.tag).groups()[-1]
        if rootNodeTag == 'rpc-reply':
            rootNode = rootNode.xpath("//*[local-name()='configuration']")[0]
        if rootNodeTag == 'data':
            rootNode = rootNode.xpath("//*[local-name()='configuration']")[0]
        rootObj = Device()
        rootObj.build(rootNode)
        return rootObj

    def parseString(self):
        '''Normally this would be an rpc_reply in case of netconf invoking or
        a configuration element in case of normal parsing'''
        from StringIO import StringIO
        doc = self.parsexml_(StringIO(self.confile))
        rootNode = doc.getroot()
        rootNodeTag = Tag_pattern_.match(rootNode.tag).groups()[-1]
        if rootNodeTag == 'rpc-reply':
            rootNode = rootNode.xpath("//*[local-name()='configuration']")[0]
        if rootNodeTag == 'data':
            rootNode = rootNode.xpath("//*[local-name()='configuration']")[0]
        rootObj = Device()
        rootObj.build(rootNode)
        return rootObj
