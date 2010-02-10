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

RE_INPUT = re_compile( r"\input{([^}]+)}" )

get_bbl_file = lambda fname: splitext(fname)[0]+".bbl"


def read_file( fname ):
    result = []
    if not splitext( fname )[1] and not exists( fname ):
        fname += ".tex"

    for line in open( fname ):
        # skip results
        if line.startswith("%"):
            continue

        line = line.replace(r"\def\mode{0} %", r"\def\mode{1}")
        # expand input statements
        m = RE_INPUT.search(line)
        if m:
            line = read_file( m.group(1) )

        # expand literature
        if line.startswith(r"\bibliographystyle"):
            continue
        if line.startswith(r"\bibliography"):
            line = read_file( get_bbl_file(argv[1]) )

        result.append( line )


    return "".join(result)


print read_file( argv[1] )


