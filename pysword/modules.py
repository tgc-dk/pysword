import os
import configparser

from .books import BibleStructure
from .pysword import SwordBible



class SwordModules(object):

    def __init__(self, path=None):
        self.sword_path = path
        self.modules = {}

    def parse_modules(self):
        if self.sword_path is None:
            self.sword_path = os.path.join(os.environ['HOME'], '.sword')
        conf_folder = os.path.join(self.sword_path, 'mods.d')
        for f in os.listdir(conf_folder):
            if f.endswith(".conf"):
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
                self.modules[module_name] = dict(config[module_name])
        mods = {}
        for key in self.modules.keys():
            mods[key] = self.modules[key]['description']
        return mods

    def get_bible_from_module(self, module_key):
        bible_module = self.modules[module_key]
        module_path = os.path.join(self.sword_path, bible_module['datapath'])
        module_type = bible_module['moddrv'].lower()
        try:
            module_versification = bible_module['versification'].lower()
        except KeyError:
            module_versification = 'default'
        return SwordBible(module_path, module_type, module_versification)