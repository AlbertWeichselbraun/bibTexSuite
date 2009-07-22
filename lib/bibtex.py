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
            return """[%s, %s] %s (%s). ''%s'', %s""" % \
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
        return "@%s{%s\n%s\n}" % ( self.type.upper(), self.key, ",\n".join(entries) )


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



if __name__ == '__main__':
    from unittest import TestCase, main

    class NameFormatterTest(TestCase):
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
                self.assertEqual( name_obj.getFirstAuthorLastname(), solution )

        def testGetAuthors(self):
            """ tests whether the function corretly formats the authors """
            for name_obj, solution in zip(self.name_obj, self.LASTNAME_FORMAT):
                self.assertEqual( name_obj.getAuthors(), solution )

            for name_obj, solution in zip(self.name_obj, self.FIRSTNAME_FORMAT): 
                self.assertEqual( name_obj.getAuthors(NameFormatter.getFirstnameFirst), solution )
           
 

    class BibTexTest(TestCase):
        
        def testGetEntries(self):
            """ read an input file """
            b=BibTex( BIBTEX_TEST_FILE )
            for bibtex_entry in b:
                pass
                #print bibtex_entry.getCitation()


    class BibTexEntryTest(TestCase):
        
        def setUp(self):
            self.bibtex_entry = _bibtex.next( _bibtex.open_file( BIBTEX_TEST_FILE, 100 ) )
        
        def testContains(self):
            """ tests whether the contains functions works as advertised """
            b = BibTexEntry( self.bibtex_entry )
            self.assertTrue ( ('Albert',) in b )
            self.assertTrue ( ('albert',) in b )
            self.assertFalse( ('albert', 'Anna') in b )
            self.assertFalse( ('Julius',) in b )

            #print b.getCitation()
            #print "xxxx", b.entry


           


    main()


