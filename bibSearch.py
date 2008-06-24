#!/usr/bin/env python

# (C)opyrights 2008 by Albert Weichselbraun <albert@weichselbraun.net>
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

import os.path
from sys import path
from operator import attrgetter
from optparse import OptionParser
from glob import glob
from os import stat

if os.path.islink(__file__):
    LIB_DIR       = os.path.join(os.path.dirname( os.readlink(__file__)), "lib")
else:
    LIB_DIR       = os.path.join(os.path.dirname(__file__), "lib")

USER_PREF_DIR = os.path.expanduser("~/.bibTexSuite")
CONFIG_FILE   = os.path.join( USER_PREF_DIR, "searchconfig.py" )
USER_CACHE    = os.path.join( USER_PREF_DIR, "cache" )

OUTPUT_FORMAT = { 'citation' : 'getCitation',
                  'wikipedia': 'getWikipediaCitation',
                  'bibtex'   : 'getBibTexCitation' }

def _create_config():
    """ creates the cache/configuration files """
    if not os.path.exists(USER_PREF_DIR): os.mkdir(USER_PREF_DIR)
    if not os.path.exists(USER_CACHE)    : os.mkdir(USER_CACHE)
    if not os.path.exists(CONFIG_FILE):
        f=open( CONFIG_FILE, "w")
        f.write("# bibSearch example config file\n\n# default output format (citation, bibtex, wikipedia)\nDEFAULT_OUTPUT_FORMAT = 'citation'\n\nDEFAULT_BIB_SEARCH_PATH = ['%s', ]\n" % (os.path.expanduser("~")) )
        f.close()

def _read_config():
    """ reads the configuration file """
    if not os.path.exists(CONFIG_FILE) or not os.path.exists(USER_CACHE):
        _create_config()
    path.append(USER_PREF_DIR)
    path.append(LIB_DIR)
    


def parse_options():
    """ parses the options specified by the user """
    parser = OptionParser()
    parser.add_option("-b", "--bibtex", dest="bibtex", action="store_true",
                      help="output search results as bibtex snippets.")
    parser.add_option("-c", "--citation", dest="citation", action="store_true",
                      help="output search results as wikipedia citations.")
    parser.add_option("-w", "--wikipedia", dest="wikipedia", action="store_true",
                      help="output search results as wikipedia citations.")
    parser.add_option("-p", "--path", dest="path", action="append", default=[],
                      help="add additional paths to the default search path.")


    (options, args) = parser.parse_args()

    # output format 
    try:
        output = [ opt for opt in OUTPUT_FORMAT.iterkeys() if attrgetter(opt)(options) ][0]
    except IndexError:
        output = DEFAULT_OUTPUT_FORMAT or 'citation'

    return {'output_format': OUTPUT_FORMAT[output], 'search_terms': args, 'search_path': DEFAULT_BIB_SEARCH_PATH + options.path }


_get_bib = lambda fn:  [ b for b in BibTex(fn) ]

def get_matching_bibtex_entries( search_terms, search_path ):
    """ returns a list of all bibtex entries matching the search terms """
    result = []
    for bibdir in search_path:
        for fname in glob(bibdir+"/*.bib"):
            result += [ b for b in cacheRetrieve( USER_CACHE, fname, _get_bib) if search_terms in b ]

    return result


# ===============================================================================
# =
# = M A I N 
# =
# ===============================================================================

_read_config()
from searchconfig import DEFAULT_BIB_SEARCH_PATH, DEFAULT_OUTPUT_FORMAT
from bibtex import BibTex
from cache import cacheRetrieve

opt = parse_options()
entries = get_matching_bibtex_entries( opt['search_terms'], opt['search_path'] )

output = attrgetter( opt['output_format'] )

for entry in entries:
    print output(entry)() 

print "(%d entries found)" % len(entries)

