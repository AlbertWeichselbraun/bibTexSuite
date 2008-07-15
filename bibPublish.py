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
from shutil import copyfile

if os.path.islink(__file__):
    LIB_DIR       = os.path.join(os.path.dirname( os.readlink(__file__)), "lib")
else:
    LIB_DIR       = os.path.join(os.path.dirname(__file__), "lib")

USER_PREF_DIR = os.path.expanduser("~/.bibTexSuite")
CONFIG_FILE   = os.path.join( USER_PREF_DIR, "publishconfig.py" )
TEMPLATE_PATH = os.path.join( USER_PREF_DIR, "templates" )
USER_CACHE    = os.path.join( USER_PREF_DIR, "cache" )


def _create_config():
    """ creates the cache/configuration files """
    if not os.path.exists(USER_PREF_DIR): os.mkdir(USER_PREF_DIR)
    if not os.path.exists(USER_CACHE)    : os.mkdir(USER_CACHE)
    if not os.path.exists(CONFIG_FILE):
        f=open( CONFIG_FILE, "w")
        f.write("# bibPublish example config file\n\n" )
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
    parser.add_option("-o", "--output-dir", dest="output_dir", 
                      help="output directory.")
    parser.add_option("-t", "--template", dest="template", default=DEFAULT_TEMPLATE,
                      help="template to use (%s)." % DEFAULT_TEMPLATE)
    parser.add_option("--template-path", dest="template_path", default=TEMPLATE_PATH,
                      help="specify another template path (%s)." % (TEMPLATE_PATH))
    parser.add_option("-i", "--input", dest="input", default=BIB_PUBLISH_FILES,
                      help="add additional bibTeX files to publish (%s)" % ", ".join(BIB_PUBLISH_FILES) )


    (options, args) = parser.parse_args()
    return options


_get_bib = lambda fn:  [ b for b in BibTex(fn) ]

def get_matching_bibtex_entries( search_terms, bibtex_files ):
    """ returns a list of all bibtex entries matching the search terms """
    result = []
    for fname in bibtex_files:
        result += [ b for b in cacheRetrieve( USER_CACHE, fname, _get_bib) if search_terms is None or search_terms in b ]

    return result


def publish( publish_dir, template_path, pdf_path,  bibtex_entries):
    """ publishes the given bibtex_entries in publish_dir using the template specified in
        template_path
    """
    pdf_search = PdfSearch(pdf_path)
    ts = Template( template_path )
    ts.recreateTheme( publish_dir)

    # write per file abstract/bibtex/pdf (if available)
    for b in bibtex_entries:
        entry_discriptor = {'bibtex': os.path.join("bibtex", b.getIEEEFilename()+".bib") }
        open( os.path.join(publish_dir, entry_discriptor['bibtex']), "w").write( b.getBibTexCitation() )
        if b.entry.has_key("abstract"):
            entry_discriptor['abstract'] = os.path.join("abstract", b.getIEEEFilename()+".html")
            open( os.path.join(publish_dir, entry_discriptor['abstract']), "w").write( ts.getAbstract(b) )
        
        pdf = pdf_search.search(b)
        if pdf!='':
            entry_discriptor['pdf'] = os.path.join("pdf", os.path.basename(pdf) ) 
            copyfile(pdf, os.path.join(publish_dir, entry_discriptor['pdf']) )

        ts.setDescriptor( b, entry_discriptor )

    # write index.html
    open( os.path.join(publish_dir, "index.html"), "w").write( ts.getHtmlFile(entries) )



# ===============================================================================
# =
# = M A I N 
# =
# ===============================================================================

_read_config()
from publishconfig import BIB_PUBLISH_OUTPUT_DIR, DEFAULT_TEMPLATE, BIB_PUBLISH_FILES, PDF_SEARCH_PATH
from template import Template
from bibtex import BibTex
from cache import cacheRetrieve
from pdfsearch import PdfSearch

options = parse_options()
entries = get_matching_bibtex_entries( None, options.input )

publish( BIB_PUBLISH_OUTPUT_DIR, os.path.join(options.template_path, options.template), PDF_SEARCH_PATH, entries )

