###############################################################################
# PySword - A native Python reader of the SWORD Project Bible Modules         #
# --------------------------------------------------------------------------- #
# Copyright (c) 2008-2015 Various developers:                                 #
# Kenneth Arnold, Joshua Gross, Ryan Hiebert, Matthew Wardrop, Tomas Groth    #
# --------------------------------------------------------------------------- #
# This program is free software; you can redistribute it and/or modify it     #
# under the terms of the GNU General Public License as published by the Free  #
# Software Foundation; version 2 of the License.                              #
#                                                                             #
# This program is distributed in the hope that it will be useful, but WITHOUT #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or       #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for    #
# more details.                                                               #
#                                                                             #
# You should have received a copy of the GNU General Public License along     #
# with this program; if not, write to the Free Software Foundation, Inc., 59  #
# Temple Place, Suite 330, Boston, MA 02111-1307 USA                          #
###############################################################################

import os
import configparser
import zipfile
import tempfile
import shutil

from .bible import SwordBible


class SwordModules(object):

    def __init__(self, path=None):
        if path is None:
            self.__sword_path = os.path.join(os.environ['HOME'], '.sword')
        else:
            self.__sword_path = path
        self.__modules = {}
        self.__temp_folder = None

    def __del__(self):
        if self.__temp_folder:
            shutil.rmtree(self.__temp_folder)

    def parse_modules(self):
        # If path is a zipfile, we extract it to a temp-folder
        if self.__sword_path.endswith('.zip'):
            self.__temp_folder = tempfile.mkdtemp()
            zipped_module = zipfile.ZipFile(self.__sword_path)
            zipped_module.extractall(self.__temp_folder)
            conf_folder = os.path.join(self.__temp_folder, 'mods.d')
        else:
            conf_folder = os.path.join(self.__sword_path, 'mods.d')
        # Loop over config files and save data in a dict
        for f in os.listdir(conf_folder):
            if f.endswith('.conf'):
                conf_filename = os.path.join(conf_folder, f)
                config = configparser.ConfigParser(strict=False)
                try:
                    conf_file = open(conf_filename, 'rt', errors='replace')
                    config.read_string(conf_file.read(), conf_filename)
                except Exception as e:
                    print('Exception while parsing %s' % f)
                    print(e)
                    continue
                module_name = config.sections()[0]
                self.__modules[module_name] = dict(config[module_name])
        # Create a simple dict with module ID and description and return it
        mods = {}
        for key in self.__modules.keys():
            mods[key] = self.__modules[key]['description']
        return mods

    def get_bible_from_module(self, module_key):
        bible_module = self.__modules[module_key]
        if self.__temp_folder:
            module_path = os.path.join(self.__temp_folder, bible_module['datapath'])
        else:
            module_path = os.path.join(self.__sword_path, bible_module['datapath'])
        module_type = bible_module['moddrv'].lower()
        try:
            module_versification = bible_module['versification'].lower()
        except KeyError:
            module_versification = 'default'
        return SwordBible(module_path, module_type, module_versification)
