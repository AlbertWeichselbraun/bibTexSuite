#!/usr/bin/env python

""" caches and restores data from the cache """

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

__revision__ = "$Revision$"

import os
from cPickle import dump, load
from md5 import md5
from stat import ST_MTIME

def cacheRetrieve( cachedir, fname, fn ):
    """ checks whether fname or cache_dir is newer
        - retrieves the data from the cache if fname is not newer than the data in cachedir
        - otherwise calls fn with fname """

    cacheFile = os.path.join( cachedir, md5(fname).hexdigest() )
    try:
        if os.stat(cacheFile)[ST_MTIME] >= os.stat(fname)[ST_MTIME]:
            return load( open(cacheFile) )

    except OSError,  FOFError:
        pass

    obj = fn(fname)
    dump( obj, open(cacheFile, "w") )
    return obj

