#!/usr/bin/env python

import shutil, os, sys
from os.path import join, exists
from csv import reader
from bibtex import NameFormatter
from collections import defaultdict

def cleanup( txt ):
    """ basic cleanup's to prevent formatting errors """
    txt = txt.replace(", ,", ", ")
    txt = txt.replace(", :", ", ")
    return txt

class Template(object):
    """ creates an HTML file using a given template """

    def __init__(self, template_path):
        self._get_file_name = lambda x: join(template_path, x)
        self._get_content   = lambda x: open(self._get_file_name(x)).read()
        # import preferences
        sys.path.append(template_path)
        try:
            from templateconfig import DEFAULT_TYPE_ORDER, ATTR_TRANSLATION_TABLE, STR_TRANSLATION_TABLE, FILE_TRANSLATION_TABLE, PUBLICATION_BLACKLIST
            self._default_order = DEFAULT_TYPE_ORDER
            self._attr_translation_tbl  = ATTR_TRANSLATION_TABLE
            self._str_translation_tbl   = STR_TRANSLATION_TABLE
            self._file_translation_tbl  = FILE_TRANSLATION_TABLE
            self._publication_blacklist = PUBLICATION_BLACKLIST   # a list of publications to ignore in the publishing process
        except ImportError: # use old schema
            from publishconfig import DEFAULT_TYPE_ORDER
            self._default_order         = DEFAULT_TYPE_ORDER
            self._attr_translation_tbl  = self._get_translation_table( "attr.csv" )
            self._str_translation_tbl   = self._get_translation_table( "str.csv" )
            self._file_translation_tbl  = self._get_translation_table( "files.csv")
            self._publication_blacklist = () 
        


    def getHtmlFile(self, bibtex_entry_list, publish_types=None):
        """ returns a bibtex file describing the given list
            of bibtex_entries """

        html = []
        html.append( self._get_head() )

        bd = self._get_per_type_listing( bibtex_entry_list )
        for tp in self._default_order:
            if not bd.has_key( tp ): 
                continue
            if publish_types is not None and tp not in publish_types:
                continue

            html.append(self._get_bibtex_type_head( tp ) )
            html += [ cleanup(self._get_bibtex_entry_content(b)) for b in reversed(sorted(bd.get(tp))) ]
            html.append(self._get_bibtex_type_foot( tp ) )

        html.append( self._get_foot() )
        return "\n".join(html)


    def getAbstract(self, bibtex_entry):
        """ returns the abstract for the given bibtex entry """
        d=self._get_entry_dict( bibtex_entry, ('editor', 'pages', 'journal', 'address', 'volume', 'number', 'booktitle', '_bibpublish' ) )
        d['citation'] = bibtex_entry.getCitation().replace("\n", "<br/>")
        return self._get_content("abstract.html") % d

    
    def setDescriptor(self, bibtex_entry, d):
        """ sets the descriptor for the given bibtex entry """
        d.update(bibtex_entry.entry)
        desc = [ self._file_translation_tbl[t] % d for t in ('abstract_url', 'url', 'eprint', 'bibtex') if t in d ]

        # set _bibpublish descriptor
        bibtex_entry.entry['_bibpublish'] = " %s " % " ".join(desc)

        # adjust title (adds a linked title, if necessary)
        if 'eprint' in d:
            u = self._file_translation_tbl['title'] % d
            bibtex_entry.entry['title'] = u
         


    def recreateTheme(self, dest_dir):
        """ recreates the theme infrastructure at dest_dir (deleting all files
            present in this directory """

        if exists(dest_dir):
           shutil.rmtree(dest_dir)

        os.mkdir( dest_dir )
        os.mkdir( os.path.join(dest_dir, "abstract") )
        os.mkdir( os.path.join(dest_dir, "bibtex") )
        os.mkdir( os.path.join(dest_dir, "pdf") )
        shutil.copytree( self._get_file_name('icons'), os.path.join(dest_dir, 'icons') )
        shutil.copytree( self._get_file_name('css'), os.path.join(dest_dir, 'css') )
       

    def _get_translation_table(self, fname):
        """ returns the translation table for formating items """
        d = dict( [ data for data in reader( open(self._get_file_name(fname) )) ] )
        return d


    def _translate_str(self, s):
        """ translates the given string using the _str_translation_table """
        for src, dest in self._str_translation_tbl.iteritems():
            s=s.replace(src,dest)
        return s


    def _get_entry_dict( self, bibtex_entry, keys ):
        """ formats optional items and sets missing items to '' """
        data = dict( [ (k,self._translate_str(v)) for k,v in bibtex_entry.entry.iteritems() ] )
        if 'author' in data:
            data['author'] = NameFormatter( data['author'] ).getAuthors()
        for k in keys:
            if not k in data:
                data[k] = ''
            elif k in self._attr_translation_tbl: 
                data[k] = self._attr_translation_tbl.get(k) % data[k]
        return data
                

    def _get_per_type_listing( self, bibtex_entry_list ):
        """ returns a dictinary with the publication_type + publications """
        bd = defaultdict( list )
        for b in bibtex_entry_list:
            # ignore blacklisted items
            if b.key in self._publication_blacklist:
                continue
            bd[b.type].append( b )
        return bd


    def _get_head(self):
        """ returns the file's head """
        return self._get_content("head.html") 


    def _get_foot(self):
        """ returns the template's foot """
        return self._get_content("foot.html")


    def _get_bibtex_entry_content(self, bibtex_entry):
        """ returns the html snippet for the given entry """
        d=self._get_entry_dict( bibtex_entry, ('editor', 'pages', 'journal', 'address', 'volume', 'number', 'booktitle', '_bibpublish', 'year', 'note', 'series' ) )

        template_string = self._get_content("%s-entry.html" % bibtex_entry.type )
        return template_string % d


    def _get_bibtex_type_head(self, tp ):
        """ returns the head for the given bibtex type """
        return self._get_content("%s-head.html" % tp )


    def _get_bibtex_type_foot(self, tp ):
        """ returns the foot for the given bibtex type """
        return self._get_content("%s-foot.html" % tp )


if __name__ == '__main__':
    from unittest import TestCase, main
    from bibtex import BibTex

    BIBTEX_TEST_FILE = "self.bib"
    TEMPLATE_PATH = "/home/albert/.bibTexSuite/templates/fides"

    class TemplateTest(TestCase):

        def testReturnHtml(self):
            """ read an input file """
            ts = Template(TEMPLATE_PATH)
            bibtex_entries = [ b for b in BibTex( BIBTEX_TEST_FILE ) ]
            print ts.getHtmlFile( bibtex_entries )



    main()

