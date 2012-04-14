#!/usr/bin/env python

""" handles bibtex objects based on the _bibtex library """

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


import _bibtex
from operator import and_
from os.path import basename
from urllib import urlencode

BIBTEX_TEST_FILE = "self.bib"

cleanup = lambda x: x.replace("{", "").replace("}", "").replace("\"", "")
get_longest_word = lambda s: max( [ (len(w), w) for w in s.split() ] )[1]


class NameFormatter(object):
    """ handles different name formats """

    def __init__(self, names):
        self.names = map( self.getLastnameFirst,  names.strip().split(" and "))

    
    @staticmethod
    def getLastnameFirst(name):
        """ converts a name to the format 'lastname, firstname(s)' """
        if "," in name or not name: 
            return name

        firstnames, lastname = name.split()[:-1], name.split()[-1:][0]
        return "%s, %s" % (lastname, " ".join(firstnames) )


    @staticmethod
    def getFirstnameFirst(name):
        """ converts a name to the format 'firstname(s) lastname' """
        if not "," in name:
            return name

        lastname, firstnames = name.split(", ")
        return "%s %s" % (firstnames, lastname)


    def getFirstAuthorLastname(self):
        """ returns the lastname of the first author """
        return self.names[0].split(", ")[0]


    def getAuthors(self, format_function=None):
        """ returns the authors as used in a citation, formatted using an
            optional format_function """

        authors = map(format_function, self.names)
        if len(authors)==1:
            return authors[0]

        return "%s and %s" % (", ".join(authors[:-1]), authors[-1])


    def getBibTexAuthors(self):
        """ returns the author list in the BibTeX format 'a1 and a2 and a3...' """
        return " and ".join(self.names)
           
        

class BibTexEntry(object):
    """ handles a single bibtex entry """

    def __init__(self, bibtex_entry, path=""):
        """ @param[in] bibtex_entry 
            @param[in] path          (optional path to the bib file containing the entry)
        """
        self.key, self.type, tmp, tmp, entries  = bibtex_entry
        self.orig_entry = dict( [ (key, cleanup(_bibtex.get_native(value))) for key, value in entries.iteritems() ] )
        self.entry = dict( [ (key, cleanup(value)) for key, value in self.orig_entry.iteritems() ] )


        self.path  = path
        if 'author' in self.entry:
            self.entry['author'] = NameFormatter(self.entry['author']).getBibTexAuthors()



    def __cmp__(self, o):
        """ sorts bibtex entries based on the publishing year """
        sy, oy = self.entry.get('year',0), o.entry.get('year', 0)
        if sy == oy:
            return 0
        elif sy > oy:
            return 1
        else:
            return -1


    def __contains__(self, search_terms):
        """ returns true if any of the BibTexEntry's fields contains the given string """
        textRep = " ".join( map(str.lower, self.entry.values()) ) + self.key
        return reduce(and_, [ needle.lower() in textRep for needle in search_terms])
    
    def getNumAuthors(self):
        """ returns the number of authors """
        if not 'author' in self.entry:
            return 0
        else:
            return len(self.entry['author'].split(" and "))

    def getAuthor(self):
        """ returns the author for the given entry """
        return NameFormatter(self.entry.get('author', '')).getAuthors()


    def getFilename(self, extension=""):
        """ returns the filename for the given entry 
            (or the ieee-filename if possible) 
        """
        if 'file' in self.entry:
            return self.entry['file'].split(":")[1]
        else:
            return self.getIEEEFilename()+extension 

    def getIEEEFilename(self):
        """ composes the IEEE filename for the entry:
              surname-titleword200x.pdf 
        """
        s="%s-%s%s" % (NameFormatter(self.entry.get('author', '')).getFirstAuthorLastname(), get_longest_word(self.getTitle()), self.getYear())
        return s


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
            return  """[%s, %s] %s (%s). ''%s'', %s""" % \
                     (self.key, basename(self.path), self.getAuthor(), self.getYear(), self.getTitle(), self.getOutlet() ) 
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
        entries = [ "   %s={%s}" % (key, value) for key, value in self.orig_entry.iteritems() ] 
        return "@%s{%s,\n%s\n}" % ( self.type.upper(), self.key, ",\n".join(entries) )


    def getCoinsCitation(self, filter_term = None):
        """ returns the coins citation for the given item """
        if not filter_term or filter_term in self:
            return Coins().getCoin( self )
        else:
            return None


    def __str__(self):
        """ returns a string representation of the item """
        return "<BibTexEntry %s>" % self.key



class BibTex(object):
    """ handles bibtex objects based n the _bibtex library """

    def __init__(self, path):
        self.path    = path
        self.fhandle = _bibtex.open_file(path, 100)

    def __iter__(self):
        """ this class implements the iterator interface """
        return self
    
    def next(self):
        """ iterator interface: get next bibtex entry """
        try:
            return BibTexEntry( _bibtex.next(self.fhandle), self.path )
        except TypeError:
            raise StopIteration



      

class Coins(object):

    def __init__(self):
        self.COIN_TRANSLATION_DICT = {
            'title':   ('rtf.atitle', self._get, 'title'),
            'journal': ('rtf.jtitle', self._get, 'journal'),
            'year':    ('rft.date', self._get, 'year'),
            'volume':  ('rtf.volume', self._get, 'volume'),
            'issue':   ('rtf.issue', self._get, 'issue'),
            'pages':   ('rtf.pages', self._get, 'pages'),
            'eprint':  ('rtf.id', self._get, 'eprint'),
            'author':  ('rtf.au', self._getAuthors, '')
        }

    def getCoin(self, b):
        """ @returns the coin for the given bibtex object """
        entry_dict = b.entry
        url = self._getReferrer() + self._getGenre( b.type )
        for item, (field, translation_function, key) in self.COIN_TRANSLATION_DICT.items():
            if item in entry_dict:
                url.extend( translation_function(field, entry_dict, key ) )

        return self._getSkeleton() % (self._assembleUrl( url ).replace("&", "&amp;"))

    def _assembleUrl(self, items):
        """ creates the coins url from the given items """
        return urlencode( items )


    def _get(self, field, d, key):
        return [ (field, d.get(key)) ]


    def _getGenre(self, entry_type):
        if entry_type.lower() in ('inproceedings', 'conference'):
            return [ ('rtf.genre', 'proceeding') ]
        elif entry_type.lower() in ('article', ):
            return [ ('rtf.genre', 'article') ]
        else:
            return [ ('rtf.genre', 'unknown') ]

    def _getAuthors(self, field, d, key):
        result = []
        for author in str(d['author']).split("and"):
            result.append( ('rtf.au', author.strip() ) )
        return result


    def _getSkeleton(self):
        return """<span class="Z3988" title="ctx_ver=Z39.88-2004&amp;%s" /> """


    @staticmethod
    def _getReferrer():
        """ returns a reference to the creator of the coin """
        return [ ('rft_id', 'info:sid/semanticlab.net:bibTexSuite'), ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:journal') ]


class TestCoins(object):

    def setUp(self):
        from os.path import dirname, join as os_join
        import _bibtex
        self.bibtex_entry = BibTexEntry( _bibtex.next( _bibtex.open_file( os_join( dirname(__file__), "../test", BIBTEX_TEST_FILE ), 100 ) ) )

    def testBibtex(self):
        print Coins().getCoin( self.bibtex_entry )


class TextBibTex(object):
        
    def testGetEntries(self):
        """ read an input file """
        b=BibTex( BIBTEX_TEST_FILE )
        for bibtex_entry in b:
            pass
            #print bibtex_entry.getCitation()


class TestBibTexEntry(object):
    
    def setUp(self):
        from os.path import dirname, join as os_join
        self.bibtex_entry = _bibtex.next( _bibtex.open_file( os_join( dirname(__file__), "../test", BIBTEX_TEST_FILE ), 100 ) )
    
    def testContains(self):
        """ tests whether the contains functions works as advertised """
        b = BibTexEntry( self.bibtex_entry )
        assert  ('Albert',) in b 
        assert ('albert',) in b 
        assert ('albert', 'Anna') not in b 
        assert  ('Julius',) not in b 


class TestNameFormatter(object):
    """ tests the nameformatter class """

    NAMES = ( "Arno Scharl and Weichselbraun, Albert and Astrid Dickinger",
              "Wagner, Petra",
              "Christian Julius Toth and Caesar, Julius H.",
            )

    LAST_NAMES      = ('Scharl', 'Wagner', 'Toth')
    LASTNAME_FORMAT = ( "Scharl, Arno, Weichselbraun, Albert and Dickinger, Astrid",
                        "Wagner, Petra",
                        "Toth, Christian Julius and Caesar, Julius H.",
                      )
    FIRSTNAME_FORMAT= ( "Arno Scharl, Albert Weichselbraun and Astrid Dickinger",
                        "Petra Wagner",
                        "Christian Julius Toth and Julius H. Caesar",
                      )


    def setUp(self):
        self.name_obj = [ NameFormatter(name) for name in self.NAMES ]


    def testGetFirstAuthorLastnameTest(self):
        """ checks whether the class correctly determines the surname of the first author """
        for name_obj, solution in zip(self.name_obj, self.LAST_NAMES):
            assert name_obj.getFirstAuthorLastname() == solution 

    def testGetAuthors(self):
        """ tests whether the function corretly formats the authors """
        for name_obj, solution in zip(self.name_obj, self.LASTNAME_FORMAT):
            assert name_obj.getAuthors() == solution 

        for name_obj, solution in zip(self.name_obj, self.FIRSTNAME_FORMAT): 
            assert name_obj.getAuthors(NameFormatter.getFirstnameFirst) == solution 
 


