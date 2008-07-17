#!/usr/bin/env python

""" config.py - handles bibTexSuite's config files """

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

from os.path import join, expanduser, exists
from sys import path


EXAMPLE_CONFIG_DIR = "example-config"

# global preferences
USER_PREF_DIR = expanduser("~/.bibTexSuite")
CONFIG_FILE   = join( USER_PREF_DIR, "publishconfig.py" )
TEMPLATE_PATH = join( USER_PREF_DIR, "templates" )
USER_CACHE    = join( USER_PREF_DIR, "cache" )


def _create_config( lib_dir ):
    """ copys the config-template to the USER_PREF_DIR """
    if exists(USER_PREF_DIR):
        return

    from shutil import copytree
    copytree( join(lib_dir, "..", EXAMPLE_CONFIG_DIR), USER_PREF_DIR )


def read_config( lib_dir ):
    """ adds the configuration files to the path """
    _create_config(lib_dir)
    path.append(USER_PREF_DIR)

