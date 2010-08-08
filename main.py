#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

import sys, os
from optparse import OptionParser
from xml.dom.minidom import parse
import xml.etree.ElementTree as ET
import re

__version__ = '1.0'

class flags:
    unique: None

    def __init__(self):
        pass

class avail:
    chance: None
    cond: None
    done: None
    location: None
    faction: {}
    
    def __init__(self):
        pass

class Mission:
    __currentNode__: None
    __missionAttribs__: {'name': None}
    
    lua: None
    flags: flags()
    avail: avail()

    def __init__(self, xmlfile):
        self.doc = parse(xmlfile)
        self.__missionAttribs__["name"] = self.doc.getRootElement().getAttribute('name')
   
        self.lua = self.doc.getRootElement().getElementsByTagName('lua')[0].childNodes[0].wholeText
        
        try:
            self.doc.getRootElement().getElementsByTagName('flags')[0].childNodes[1].tagName
        except:
            self.flags.unique = False
        else:
            self.flags.unique = True
        
        for availTag in self.doc.getRootElement().getElementsByTagName('avail').childNodes:
            if availTag.nodeType == availTag.TEXT_NODE:
                continue
            elif availTag.tagName == 'cond':
                self.avail.cond = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'chance':
                self.avail.chance = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'done':
                self.avail.done = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'location':
                locations = [ 'None', 'Computer', 'Bar', 'Outfit', 'Shipyard', 'Land', 'Commodity' ]
                if availTag.childNodes[0].wholeText not in locations:
                    sys.stderr.write("Unknow value '%s' for 'location' child of avail tag for mission %s" % (availTag.childNodes[0].wholeText, self.getName()))
                else:
                    self.avail.location[] = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'action':
                self.avail.faction = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'planet':
                self.avail.planet = availTag.childNodes[0].wholeText
            else:
                sys.stderr.write("Unknow child %s of avail tag for mission %s" % (availTag.tagName, self.getName()))

    def getName(self):
        return self.__missionAttribs__["name"]

class TransformXmlToMissions:
    __missionList__ = None
    __verbose__     = True
    
    def __init__(self):
        self.readXml()

    def readXml(self, localpath):
        localpath = os.path.abspath(os.path.normpath(localpath))
        for root, dirs, files in os.walk(localpath):
            for f in files:
                filename = os.path.join(root, f)
                if re.match(".*(\.xml)$", f) and !self.ignore_filename(filename):
                    sys.stdout.write("Processing %s" % (filename))
                    sys.stdout.flush()
                    self.__missionList__[] = Mission(filename)
        sys.stdout.write("Done")
        sys.stdout.flush()
    
    def writeMissionsXml(self, output=None):
        rootxml = ET.Element('Missions')
        for mission in self.__missionList__:
            child = ET.Element('mission', name=mission.getName())
            
    
    def ignore_filename(self,filename):
        root, ext = os.path.splitext(filename)
        basename = os.path.basename(filename)
        if ext in ['.pyc', '.pyo', '.backup'] \
               or ext.endswith('~') or ext.endswith('#') or basename.startswith('.'):
            return True
        return False

if __name__ == "__main__":

    parser = OptionParser(usage="Usage %prog [-h] [-v] [-o] <path to naev/dat/missions/>",
                          version="%prog "+__version__,
                          description='''\
TODO: write a description
Gather informational tags about missions, do a sanity check and write them in
a big xml.
'''
                         )
    parser.add_option("-o", "--output",
                      metavar="FILE", help="write output to FILE" )
    parser.add_option("-v", "--verbose",
                      action="store_true", default=False)

    (cfg, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("incorrect number of arguments")

    local_path = args[0]
    local_files = TransformXmlToMissions(local_path)
    
