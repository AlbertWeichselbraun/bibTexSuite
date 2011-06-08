# bibPublish style config file

# the order in which the data is published
DEFAULT_TYPE_ORDER     = ('article', 'inproceedings', 'incollection', 'book', 'phdthesis', 'mastersthesis', 'unpublished', )

# translation of bibTex attributes
ATTR_TRANSLATION_TABLE = {'booktitle': ' %s',
                          'year'     : '%s.',
                          'editor'   : ', Ed. %s',
                          'address'  : ', %s',
                          'number'   : '(%s):',
                          'volume'   : ' %s',
                          'pages'    : ' %s',
                          'doi'      : 'doi:%s',
                          'series'   : '%s, ',
                          'note'     : '%s.',
                         }

# publications to ignore
PUBLICATION_BLACKLIST = ()

# translation of strings (required to translate latex constructs
# into matching html, etc.
STR_TRANSLATION_TABLE  = {}

# translation of the file menu
FILE_TRANSLATION_TABLE = {'abstract_url': '',
                          'url'         : '',
                          'eprint'      : '',
                          'bibtex'      : '',
                          'title'       : '%(title)s',
                          'doi'         : '%(doi)s',
                         }

