#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim:set shiftwidth=4 tabstop=4 expandtab textwidth=79:

import sys, os
import xml.etree.ElementTree as ET
from optparse import OptionParser
import re

__version__ = '1.0'

def get_local_files(localpath,Verbose=True):
    localpath = os.path.abspath(os.path.normpath(localpath))
    localfiles = {}
    for root, dirs, files in os.walk(localpath):
        for f in files:
            print os.path.join(root, f)
            if re.match("(\.xml)$", f):
                localfiles.append(os.path.join(root,f))

def parse_local_files(localfiles, Verbose=True):
    root = ET.Element("Missions")
    for xmlfile in localfiles:
        ET.SubElement(root, ET.parse(xmlfile))
    tree = ET.ElementTree(root)


if __name__ == "__main__":

    parser = OptionParser(usage="Usage %prog [-h] [-v] [-o] <path to parse>",
                          version="%prog "+__version__,
                          description='''\
Output a xml file.
'''
                         )
    parser.add_option("-o", "--output",
                      metavar="FILE", help="write output to FILE" )
    parser.add_option("-c", "--verbose",
                      action="store_true", default=False)

    (cfg, args) = parser.parse_args()
    if len(args)!=1:
        parser.error("incorrect number of arguments")

    local_path = args[0]
    local_files = get_local_files(local_path)
