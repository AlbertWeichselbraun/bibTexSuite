#!/usr/bin/env python

""" handles bibtex objects based on the bibtexparser library """

# (C)opyrights 2008-2020 by Albert Weichselbraun <albert@weichselbraun.net>
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


import bibtexparser
from operator import and_
from os.path import basename
from urllib import urlencode

BIBTEX_TEST_FILE = "self.bib"


def cleanup(s):
    return s.replace("{", "").replace("}", "").replace("\"", "")


def get_longest_word(s):
    return max([(len(w), w) for w in s.split()])[1]


class NameFormatter(object):
    """ handles different name formats """

    def __init__(self, names):
        self.names = map(self.getLastnameFirst, names.strip().split(" and "))

    def __len__(self):
        '''
        Returns:
            the number of names in the entry.
        '''
        return len(self.names)

    @staticmethod
    def getLastnameFirst(name):
        """ converts a name to the format 'lastname, firstname(s)' """
        if "," in name or not name:
            return name

        firstnames, lastname = name.split()[:-1], name.split()[-1:][0]
        return "{}, {}".format(lastname, " ".join(firstnames))

    @staticmethod
    def getFirstnameFirst(name):
        """ converts a name to the format 'firstname(s) lastname' """
        if "," not in name:
            return name

        lastname, firstnames = name.split(", ")
        return "{} {}".format(firstnames, lastname)

    def getFirstAuthorLastname(self):
        """ returns the lastname of the first author """
        return self.names[0].split(", ")[0]

    def getAuthors(self, format_function=None):
        """
        Returns:
            the authors as used in a citation, formatted using an optional
            format_function.
        """
        authors = map(format_function, self.names)
        if len(authors) == 1:
            return authors[0]

        return "{} and {}".format(", ".join(authors[:-1]), authors[-1])

    def getBibTexAuthors(self):
        '''
        Returns:
            the author list in the BibTeX format 'a1 and a2 and a3...'
        '''
        return " and ".join(self.names)


class BibTexEntry(object):
    """ handles a single bibtex entry """

    def __init__(self, bibtex_entry, path=""):
        """
        Args:
            bibtex_entry: the dictionary of the bibtex entry
            path: optional path of the bib file containing the entry
        """
        self.orig_entry = bibtex_entry
        self.entry = {key: cleanup(value)
                      for key, value in bibtex_entry.items()}

        self.path = path
        # standardize author entries
        self.entry['author'] = NameFormatter(self.entry.get('author', 0))

    def __cmp__(self, o):
        """ sorts bibtex entries based on the publishing year """
        sy, oy = self.entry.get('year', 0), o.entry.get('year', 0)
        if sy == oy:
            return 0
        elif sy > oy:
            return 1
        else:
            return -1

    def __contains__(self, search_terms):
        '''
        Returns:
            True if any of the BibTexEntry's fields contains the given string
        '''
        entry_text = ' '.join([v.lower() for v in self.entry.values()])
        for term in search_terms:
            if term in entry_text:
                return True

        return False

    def getNumAuthors(self):
        """ returns the number of authors """
        return len(self.entry['author'])

    def getAuthor(self):
        """ returns the author for the given entry """
        return self.entry['author'].getAuthors()

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
        s = "%s-%s%s" % (self.entry['author'].getFirstAuthorLastname(),
                         get_longest_word(self.getTitle()),
                         self.getYear())
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
        self.path = path
        with open(path) as bib_file:
            self.bibtex_entries = bibtexparser.load(bib_file).entries

    def __iter__(self):
        """ this class implements the iterator interface """
        return self.bibtex_entries.__iter__

    def next(self):
        """ iterator interface: get next bibtex entry """
        try:
            return self.bibtex_entries.next()
        except TypeError:
            raise StopIteration


class Coins(object):

    def __init__(self):
        self.COIN_TRANSLATION_DICT = {
            'title':   ('rft.atitle', self._get, 'title'),
            'journal': ('rft.jtitle', self._get, 'journal'),
            'year':    ('rft.date', self._get, 'year'),
            'volume':  ('rft.volume', self._get, 'volume'),
            'number':  ('rft.issue', self._get, 'number'),
            'pages':   ('rft.pages', self._get, 'pages'),
            'eprint':  ('rft.id', self._get, 'eprint'),
            'author':  ('rft.au', self._getAuthors, '')
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
            return [ ('rft.genre', 'proceeding'), ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:journal') ]
        elif entry_type.lower() in ('article', ):
            return [ ('rft.genre', 'article'), ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:journal') ]
        elif entry_type.lower() in ('book', 'collection'):
            return [ ('rft.genre', 'book'), ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:journal') ]
        elif entry_type.lower() in ('incollection', ):
            return [ ('rft.genre', 'incollection'), ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:journal') ]
        else:
            return [ ('rft.genre', 'unknown'), ('rft_val_fmt', 'info:ofi/fmt:kev:mtx:journal') ]

    def _getAuthors(self, field, d, key):
        first_author = d['author'].split("and")[0].strip()
        if ", " in first_author:
            last, first = first_author.split(", ", 1)
        else:
            first, last = first_author.split(" ", 1)

        result = [ ('rft.aufirst', first), ('rft.aulast', last) ]
        for author in str(d['author']).split("and"):
            result.append( ('rft.au', author.strip() ) )
        return result

    def _getSkeleton(self):
        return """<span class="Z3988" title="ctx_ver=Z39.88-2004&amp;%s" /> """

    @staticmethod
    def _getReferrer():
        """ returns a reference to the creator of the coin """
        return [ ('rfr_id', 'info:sid/semanticlab.net:bibTexSuite'), ]


class TestCoins(object):

    def setUp(self):
        from os.path import dirname, join as os_join
        import _bibtex
        self.bibtex_entry = BibTexEntry( _bibtex.next( _bibtex.open_file( os_join( dirname(__file__), "../test", BIBTEX_TEST_FILE ), 100 ) ) )

    def testBibtex(self):
        print(Coins().getCoin(self.bibtex_entry))


class TextBibTex(object):

    def testGetEntries(self):
        """ read an input file """
        b = BibTex(BIBTEX_TEST_FILE)
        for bibtex_entry in b:
            pass
            #print bibtex_entry.getCitation()


class TestBibTexEntry(object):

    def setUp(self):
        from os.path import dirname, join as os_join
        fname = os_join(dirname(__file__), "../test", BIBTEX_TEST_FILE)
        self.bibtex_entry = BibTex(fname).next()

    def testContains(self):
        """ tests whether the contains functions works as advertised """
        b = BibTexEntry(self.bibtex_entry)
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
