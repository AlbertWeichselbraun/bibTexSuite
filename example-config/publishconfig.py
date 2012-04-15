# bibPublish example config file
from os.path import expanduser

# default output format (citation, bibtex, wikipedia)
DEFAULT_TEMPLATE = 'benno'
DEFAULT_TYPE_ORDER = ('book', 'article', 'incollection', 'inproceedings', 'unpublished', 'phdthesis', 'mastersthesis')

BIB_PUBLISH_FILES = ('/home/albert/data/ac.literature/self.bib', )

BIB_PUBLISH_BIB_TYPES = ('article', )
BIB_PUBLISH_BLACKLIST = ()
BIB_PUBLISH_WHITELIST = ()

BIB_PUBLISH_OUTPUT_DIR = expanduser('~/Public/publications')

