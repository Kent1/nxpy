from lxml import etree
from nxpy.interface import Interface
from nxpy.vlan import Vlan
from nxpy.flow import Flow
from util import tag_pattern


class Device(object):

    # Singleton
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(
                Device, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.name = ''
        self.domain_name = ''
        self.interfaces = []
        self.vlans = []
        self.routing_options = []

    def export(self, netconf_config=False):
        config = etree.Element("configuration")
        device = etree.Element('system')
        if self.name:
            etree.SubElement(device, "host-name").text = self.name
        if self.domain_name:
            etree.SubElement(device, "domain-name").text = self.domain_name
        if len(device.getchildren()):
            config.append(device)
        interfaces = etree.Element('interfaces')
        if len(self.interfaces):
            for interface in self.interfaces:
                if (interface):
                    interfaces.append(interface.export())
            config.append(interfaces)
        vlans = etree.Element('vlans')
        if len(self.vlans):
            for vlan in self.vlans:
                if (vlan):
                    vlans.append(vlan.export())
            config.append(vlans)
        routing_options = etree.Element('routing-options')
        if len(self.routing_options):
            for ro in self.routing_options:
                if (ro):
                    routing_options.append(ro.export())
            config.append(routing_options)
        if netconf_config:
            conf = etree.Element("config")
            conf.append(config)
            config = conf
        if len(config.getchildren()):
            return config
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = tag_pattern.match(child.tag).groups()[-1]
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
                childName_ = tag_pattern.match(node.tag).groups()[-1]
                # *************** FLOW ****************
                if childName_ == 'flow':
                    obj_ = Flow()
                    obj_.build(node)
                    self.routing_options.append(obj_)
