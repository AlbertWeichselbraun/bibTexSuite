#!/usr/bin/env python

""" searches and lists labels within a latex file
"""
# (C)opyrights 2008-2009 by Albert Weichselbraun <albert@weichselbraun.net>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from re import compile
from sys import argv
from collections import defaultdict

RE_LABEL = compile("\\label\{([^\}]+)\}")
LABEL_GROUPS = { 'sec': 'Sections', 'eq': 'Equations', 'fig': 'Figures', 'tab': 'Tables' }

def extract_labels( fname ):
    """ extract all labels from the text """
    labels=[]
    for line in open( fname ):
        labels.extend( RE_LABEL.findall(line) )

    return labels

def group_labels( labels ):
    """ groups labels based on their qualifiers """
    res = defaultdict( list )
    for label in labels:
        if ":" in label:
            grp, lbl = label.split(":", 1) 
        else:
            grp, lbl = '', label

        if grp in LABEL_GROUPS:
            res[ LABEL_GROUPS[grp] ].append(label)
        else:
            res['Unknown'].append(label)

    return res


labels = extract_labels( argv[1] )

for group, label in group_labels( labels ).iteritems():
    print group.upper()+":"
    print "  "+"\n  ".join( sorted(label) )

