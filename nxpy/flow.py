import re
from lxml import etree
from nxpy import tag_pattern, whitespace_pattern


class Flow(object):

    def __init__(self):
        self.routes = []

    def export(self):
        flow = etree.Element('flow')
        if len(self.routes):
            for route in self.routes:
                flow.append(route.export())
            return flow
        else:
            return False

    def build(self, node):
        for child in node:
            nodeName_ = tag_pattern.match(child.tag).groups()[-1]
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
            ro = etree.Element('route', {'operation': self.operation})
        else:
            ro = etree.Element('route')
        if self.name:
            etree.SubElement(ro, "name").text = self.name
        match = etree.Element("match")
        for key in self.match:
            if self.match[key]:
                for value in self.match[key]:
                    etree.SubElement(match, key).text = value
        if match.getchildren():
            ro.append(match)
        then = etree.Element("then")
        for key in self.then:
            if self.then[key]:
                if self.then[key] is not True and self.then[key] is not False:
                    etree.SubElement(then, key).text = self.then[key]
                else:
                    etree.SubElement(then, key)
        if then.getchildren():
            ro.append(then)
        if ro.getchildren():
            return ro
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
        elif nodeName_ == 'match':
            for grandChild_ in child_:
                grandChildName_ = tag_pattern.match(
                    grandChild_.tag).groups()[-1]
                grandChildText = grandChild_.text
                grandChildText = re.sub(
                    whitespace_pattern, " ", grandChildText).strip()
                self.match[grandChildName_].append(grandChildText)
        elif nodeName_ == 'then':
            for grandChild_ in child_:
                grandChildName_ = tag_pattern.match(
                    grandChild_.tag).groups()[-1]
                self.then[grandChildName_] = True
