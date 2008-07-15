#!/usr/bin/env python

""" searches pdf-files matching the bibTex entry """

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

from os import walk
from os.path import join, basename


class PdfSearch(object):
    """ searches for pdf files matching a certain pattern in 
        a number of paths """

    def __init__(self, search_path):
        self.search_tree = self.get_search_tree( search_path ) 


    def match(self, fname, fqn):
        """ returns true if the file fits to the search pattern """
        fname = fname.lower()

        if fqn.lower().endswith(fname) or basename(fqn).lower()==fname:
            return True
        return False


    def search(self, bibtex_entry):
        """ searches the cached directory tree for a file matching
            the conditions self.match
        """
        fqn = bibtex_entry.getFilename(extension=".pdf")
        for f in self.search_tree:
            if self.match(f, fqn):
                return f
        return ""
        

    @staticmethod
    def get_search_tree(path_list):
        """ returns a tuple with all files in the directories in 
            the path_list
        """
        tree = []
        for p in path_list:
            for root,dirs,files in walk(p): 
                tree +=  [ join(root,fname) for fname in files if fname.lower().endswith(".pdf") ] 

        return tuple( tree )



if __name__ == '__main__':
    from unittest import TestCase, main


    class PdfSearchTest(TestCase):

        def testSearchTree(self):
            ps = PdfSearch( ("/tmp", ) )
            print ps.search_tree

    main()

