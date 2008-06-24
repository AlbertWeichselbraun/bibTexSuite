#!/usr/bin/env python

""" handles bibtex objects based on the _bibtex library """

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


import _bibtex
from operator import and_
BIBTEX_TEST_FILE = "self.bib"


cleanup = lambda x: x.replace("{", "").replace("}", "").replace("\"", "")

class BibTexEntry(object):
    """ handles a single bibtex entry """

    def __init__(self, bibtex_entry):
        self.key, self.type, tmp, tmp, entries  = bibtex_entry
        self.orig_entry = dict( [ (key, cleanup(_bibtex.get_native(value))) for key, value in entries.iteritems() ] )
        self.entry = dict( [ (key, cleanup(value)) for key, value in self.orig_entry.iteritems() ] )


    def __contains__(self, search_terms):
        """ returns true if any of the BibTexEntry's fields contains the given string """
        textRep = " ".join( map(str.lower, self.entry.values()) )
        return reduce(and_, [ needle.lower() in textRep for needle in search_terms])
    

    def getAuthor(self):
        """ returns the author for the given entry """
        return self.entry.get('author', '')


    def getTitle(self):
        return self.entry['title']


    def getYear(self):
        return self.entry.get('year', '')

    def getOutlet(self):
        """ returns the entrie's outlet """
        outlet = []
        outlet.append( self.entry.get('journal', '') or self.entry.get('booktitle', '') or "" )
        if 'isbn' in self.entry:
            outlet.append("ISBN: %(isbn)s" % self.entry )
        outlet.append( self.entry.get('publisher', '') )
        if 'pages' in self.entry:
            outlet.append( "pages %(pages)s" %  self.entry )
        if 'volume' in self.entry and 'number' in self.entry:
            outlet.append("%(volume)s(%(number)s)" % self.entry )
        # cleanup entries
        outlet = filter(None, outlet)
        return ", ".join(outlet)


    def getCitation(self, filter_term = None):
        """ returns the citation of the given article """
        if not filter_term or filter_term in self:
            return """%s (%s). ''%s'', %s""" % \
                     (self.getAuthor(), self.getYear(), self.getTitle(), self.getOutlet() )
        else:
            return None

       
    def getWikipediaCitation(self, filter_term = None):
        """ returns the wikipedia citation for the given article """
        if not filter_term or filter_term in self:
            return """<cite id="%s">%s</cite>""" % (self.key, self.getCitation() )
        else:
            return None


    def getBibTexCitation(self, filter_term = None):
        """ returns the bibTexCitation for the given item """
        entries = [ "   %s=%s" % (key, value) for key, value in self.orig_entry.iteritems() ] 
        return "@%s{%s\n%s\n}" % ( self.type.upper(), self.key, "\n".join(entries) )


    def __str__(self):
        """ returns a string representation of the item """
        return "<BibTexEntry %s>" % self.key



class BibTex(object):
    """ handles bibtex objects based n the _bibtex library """

    def __init__(self, fname):
        self.fhandle = _bibtex.open_file(fname, 100)

    def __iter__(self):
        """ this class implements the iterator interface """
        return self
    
    def next(self):
        """ iterator interface: get next bibtex entry """
        try:
            return BibTexEntry( _bibtex.next(self.fhandle) )
        except TypeError:
            raise StopIteration


if __name__ == '__main__':
    from unittest import TestCase, main


    class BibTexTest(TestCase):
        
        def testGetEntries(self):
            """ read an input file """
            b=BibTex( BIBTEX_TEST_FILE )
            for bibtex_entry in b:
                print bibtex_entry.getCitation()


    class BibTexEntryTest(TestCase):
        
        def setUp(self):
            self.bibtex_entry = _bibtex.next( _bibtex.open_file( BIBTEX_TEST_FILE, 100 ) )
        
        def testContains(self):
            """ tests whether the contains functions works as advertised """
            b = BibTexEntry( self.bibtex_entry )
            self.assertTrue ( ('Albert',) in b )
            self.assertTrue ( ('albert',) in b )
            self.assertTrue ( ('albert','arno','astrid') in b )
            self.assertFalse( ('albert', 'Anna') in b )
            self.assertFalse( ('Julius',) in b )

            print b.getCitation()

    main()



            

