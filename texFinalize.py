#!/usr/bin/env python

""" finalizes latex documents for publication
    (merges input files and bibiography)
"""
# (C)opyrights 2008-2010 by Albert Weichselbraun <albert@weichselbraun.net>
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

from re import compile as re_compile
from sys import argv
from os.path import splitext, exists

RE_INPUT  = re_compile( r"\input{([^}]+)}" )
RE_FIGURE = re_compile( r"newlabel{fig:(\S+)}{{(\d+)}" )
RE_HREF   = re_compile( ".href{[^}]+?}{([^}]+?)}" )

FIG_NUM_TABLE = {}

latexComand = lambda x: "\n"+x if x.startswith("\\") else x

def get_bbl_file( fname ):
    """ reads the bbl file and removes links from the file """
    fname = splitext( fname )[0]+".bbl"
    result = "".join( [ latexComand( line.strip()+" " if not line.strip().endswith("%") else line.strip()[:-1] ) for line in open(fname) ] )
    getLinkText = lambda x: x.group(1)
    return "\n".join( [ RE_HREF.sub(getLinkText, line) for line in result.split("\n") ] )


def read_aux_file( fname ):
    """ reads the aux file required to replace labels with figure numbers """
    fname = splitext( fname )[0]+".aux"
    if not exists( fname ):
        return

    for line in open( fname ):
        m = RE_FIGURE.search(line)
        if m:
            key = r"\ref{fig:%s}" % m.group(1)
            FIG_NUM_TABLE[ key ] = m.group(2)


def replace_items( line ):
    """ replaces mode and figure references """
    line = line.replace(r"\def\mode{0} %", r"\def\mode{1} %")
    for key, reference in FIG_NUM_TABLE.items():
        line = line.replace(key, reference)
    return line


def read_file( fname ):
    result = []
    if not splitext( fname )[1] and not exists( fname ):
        fname += ".tex"

    read_aux_file( fname )

    for line in open( fname ):
        # skip results
        if line.startswith("%"):
            continue

        line = replace_items( line )
        # expand input statements
        m = RE_INPUT.search(line)
        if m:
            line = read_file( m.group(1) )

        # expand literature
        if line.startswith(r"\bibliographystyle"):
            continue
        if line.startswith(r"\bibliography"):
            line = get_bbl_file(argv[1])

        result.append( line )


    return "".join(result)


print read_file( argv[1] )


