#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

import sys, os
from types import *
from optparse import OptionParser
from xml.dom.minidom import parse
import xml.etree.ElementTree as ET
import re

__version__ = '1.0'

class debug:
    """
    Simple objet to help show verbose level of text.
    """
    _verbose = None

    def __init__(self, verbose=False):
        if self._verbose == None:
            self._verbose = verbose

    def toggleVerbose(self):
        if self._verbose:
            self._verbose = False
        else:
            self._verbose = True

    def p(self, text):
        if self._verbose:
            print text

class Factions:
    factionData = None

    def __init__(self, factionXmlFile):
        """
        Load the faction.xml file in memory
        """
        if self.factionData == None:
            self.factionData = ET.parse( factionXmlFile )

    def findFaction(self, name):
        """
        return true fi the faction 'name' is found in the faction xml file
        """
        for faction in self.factionData.findall('faction'):
            if faction.attrib['name'] == name:
                return True
        return False

class Asset:
    assetData = None

    def __init__(self, assetXmlFile):
        """
        Load the asset.xml file in memory
        """
        if self.assetData == None:
            self.assetData = ET.parse( assetXmlFile )

    def findPlanet(self, name):
        """
        Return true if the planet 'name' is found in the asset xml file
        """
        for asset in self.assetData.findall('asset'):
            if asset.attrib['name'] == name:
                return True
        return False

class Mission:
    __currentNode__ = None
    Factions
    Asset

    def __init__(self, xmlfile, Factions, Asset):
        self.Factions = Factions
        self.Asset = Asset

        self.debug = debug()
        self.doc = parse(xmlfile)
        self.Attribs = {}
        self.Attribs["name"] = self.getRootElement().getAttribute('name')

        self.lua = self.getRootElement().getElementsByTagName('lua')[0].childNodes[0].wholeText

        self.flags = {'unique': None}
        try:
            self.getRootElement().getElementsByTagName('flags')[0].childNodes[1].tagName
        except:
            self.flags['unique'] = False
        else:
            self.flags['unique'] = True

        self.avail = { 'chance': None,
                       'cond': None,
                       'done': None,
                       'location': [],
                       'faction': [],
                       'planet': []}

        for availTag in self.getRootElement().getElementsByTagName('avail')[0].childNodes:
            if availTag.nodeType == availTag.TEXT_NODE:
                continue
            elif availTag.tagName == 'cond':
                self.avail['cond'] = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'chance':
                self.avail['chance'] = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'done':
                self.avail['done'] = availTag.childNodes[0].wholeText
            elif availTag.tagName == 'location':
                locations = [ 'None', 'Computer', 'Bar', 'Outfit', 'Shipyard', 'Land', 'Commodity' ]
                if availTag.childNodes[0].wholeText not in locations:
                    sys.stderr.write("Unknow value '%s' for 'location' child of avail tag for mission %s\n"
                            % (availTag.childNodes[0].wholeText, self.getName()))
                else:
                    self.avail['location'].append(availTag.childNodes[0].wholeText)
            elif availTag.tagName == 'faction':
                if self.Factions.findFaction(availTag.childNodes[0].wholeText):
                    self.avail['faction'].append(availTag.childNodes[0].wholeText)
                else:
                    print "Error: faction %s didn't exists" % availTag.childNodes[0].wholeText
            elif availTag.tagName == 'planet':
                if self.Asset.findPlanet(availTag.childNodes[0].wholeText):
                    self.avail['planet'].append(availTag.childNodes[0].wholeText)
                else:
                    print "Error: planet %s didn't exists" % availTag.childNodes[0].wholeText
            else:
                sys.stderr.write("Unknow child %s of avail tag for mission %s" % (availTag.tagName, self.getName()))

    def getRootElement(self):
        if self.__currentNode__ == None:
            self.__currentNode__ = self.doc.documentElement
        return self.__currentNode__


    def getName(self):
        return self.Attribs["name"]

    def isUnique(self):
        return self.flags['unique']

    def getAvail(self,Node=None):
        if Node != None:
            if None in self.avail:
                return self.avail[Node]
            else:
                return None
        else:
            return {'chance': self.avail['chance'],
                    'cond': self.avail['cond'],
                    'done': self.avail['done'],
                    'location': self.avail['location'],
                    'planet': self.avail['planet'],
                    'faction': self.avail['faction']
                   }

class TransformXmlToMissions:
    __missionList__ = []

    def __init__(self, localpath, debug, ignore):
        self.debug = debug
        self.ignore = ignore
        self.readXml(localpath)

    def readXml(self, localpath):
        datpath = os.path.abspath(os.path.normpath(localpath + "/../"))
        localpath = os.path.abspath(os.path.normpath(localpath))
        assets = Asset(os.path.join(datpath, 'asset.xml'))
        factions = Factions(os.path.join(datpath, 'faction.xml'))
        for root, dirs, files in os.walk(localpath):
            for f in files:
                filename = os.path.join(root, f)
                if self.ignore_filename(filename):
                    continue
                if re.match(".*(\.xml)$", f):
                    self.debug.p("Processing %s" % (filename))
                    self.__missionList__.append(Mission(filename,
                                                    factions,
                                                    assets
                                                ))
                    m = None
        self.debug.p("Done")

    def writeMissionsXml(self, output=None):
        rootxml = ET.Element('Missions')
        for mission in self.__missionList__:
            child = ET.SubElement(rootxml, 'mission', name=mission.getName())
            lua = ET.SubElement(child, 'lua')
            lua.text=mission.lua
            if (mission.isUnique()):
                flags = ET.SubElement(child, 'flags')
                ET.SubElement(flags, 'unique')
            avail = ET.SubElement(child, 'avail')
            for key, val in mission.getAvail().items():
                if val:
                    if type(val) is ListType:
                        for item in val:
                            etkey = ET.SubElement(avail, key)
                            etkey.text = item
                    else:
                        etkey = ET.SubElement(avail, key)
                        etkey.text = val
        tree = ET.ElementTree(rootxml)
        if output:
            tree.write(output,'utf-8')
        else:
            ET.dump(rootxml)

    def tostring(self):
        for mission in self.__missionList__:
            print "Name: %s" % mission.getName()
            print "Lua: %s" % mission.lua()
            if mission.isUnique() == True:
                print "+Is unique"
            print "Avail:"
            for key, val in mission.getAvail().items():
                print "   %s: %s" % (key, val)
            print

    def ignore_filename(self,filename):
        root, ext = os.path.splitext(filename)
        basename = os.path.basename(filename)
        if ext in ['.pyc', '.pyo', '.backup'] \
                or ext.endswith('~') or ext.endswith('#') \
                or basename.startswith('.') or filename in self.ignore:
            return True
        return False

if __name__ == "__main__":

    parser = OptionParser(usage="Usage %prog [-h] [-v] [-o] <path to naev/dat/missions/>",
                          version="%prog "+__version__,
                          description='''\

TODO: write a description.

Gather informational tags about missions, do a sanity check and write them in
a big xml.
'''
                         )
    parser.add_option("-o", "--output",
                      metavar="FILE", help="write output to FILE" )
    parser.add_option("-i", "--ignore",
                      action="append", default=[], metavar="FILE",
                      help="ignore FILE. To ignore more than one file, repeat \
                      this argument")
    parser.add_option("-v", "--verbose",
                      action="store_true", default=False)

    (cfg, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("incorrect number of arguments")

    local_path = args[0]
    local_files = TransformXmlToMissions(local_path, debug(cfg.verbose),
            cfg.ignore)

    local_files.writeMissionsXml(cfg.output)




