import os
from nxpy.device import Device
from nxpy.util import tag_pattern
from lxml import etree


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
        rootNodeTag = tag_pattern.match(rootNode.tag).groups()[-1]
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
        rootNodeTag = tag_pattern.match(rootNode.tag).groups()[-1]
        if rootNodeTag == 'rpc-reply':
            rootNode = rootNode.xpath("//*[local-name()='configuration']")[0]
        if rootNodeTag == 'data':
            rootNode = rootNode.xpath("//*[local-name()='configuration']")[0]
        rootObj = Device()
        rootObj.build(rootNode)
        return rootObj
