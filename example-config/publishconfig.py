# bibPublish example config file
from os.path import expanduser

DEFAULT_TEMPLATE = 'fides'
DEFAULT_TYPE_ORDER = ('book', 'article', 'incollection', 'inproceedings', 'unpublished', 'phdthesis', 'mastersthesis')

# a list of bibtex files to publish
BIB_PUBLISH_FILES = ('/home/albert/data/common/literature/self.bib', )

# a list of paths to search for pdf's
PDF_SEARCH_PATH   = ('/home/albert/data/ac/research', '/home/albert/data/ac/conferences', '/home/albert/data/ac/talks' )

# the output directory for the html-files
BIB_PUBLISH_OUTPUT_DIR = expanduser('html_bib')
