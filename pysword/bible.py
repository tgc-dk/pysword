import os
import struct
import zlib

from .books import BibleStructure


class SwordModuleType:
    RAWTEXT = 'rawtext'
    ZTEXT = 'ztext'
    RAWTEXT4 = 'rawtext4'
    ZTEXT4 = 'ztext4'


class SwordBible(object):

    def __init__(self, module_path, module_type=SwordModuleType.ZTEXT, versification='default'):
        self.__structure = BibleStructure(versification)
        self.__module_type = module_type
        self.__module_path = module_path
        #self.__modules_path = os.path.join(os.environ['HOME'], '.sword', 'modules', 'texts', self.__module_type)
        self.__files = {
            'ot': None,
            'nt': None
            }
        if self.__module_type in (SwordModuleType.ZTEXT, SwordModuleType.ZTEXT4):
            try:
                self.__files['ot'] = self.__get_ztext_files('ot')
            except OSError:
                pass
            try:
                self.__files['nt'] = self.__get_ztext_files('nt')
            except OSError:
                pass
        elif self.__module_type in (SwordModuleType.RAWTEXT, SwordModuleType.RAWTEXT4):
            try:
                self.__files['ot'] = self.__get_rawtext_files('ot')
            except OSError:
                pass
            try:
                self.__files['nt'] = self.__get_rawtext_files('nt')
            except OSError:
                pass
        else:
            raise ValueError('Invalid module type: %s' % module_type)
        if self.__files['ot'] is None and self.__files['nt'] is None:
            raise OSError('Could not open OT or NT for module')
        # Set verse record format and size
        if self.__module_type == SwordModuleType.ZTEXT:
            self.__verse_record_format = '<IIH'
            self.__verse_record_size = 10
        elif self.__module_type == SwordModuleType.ZTEXT4:
            self.__verse_record_format = '<III'
            self.__verse_record_size = 12
        elif self.__module_type == SwordModuleType.RAWTEXT:
            self.__verse_record_format = '<IH'
            self.__verse_record_size = 6
        elif self.__module_type == SwordModuleType.RAWTEXT4:
            self.__verse_record_format = '<II'
            self.__verse_record_size = 8

    def __get_ztext_files(self, testament):
        '''Given a testament ('ot' or 'nt'), returns a tuple of files
        (verse_to_buf, buf_to_loc, text)
        '''
        v2b_name, b2l_name, text_name = [os.path.join(self.__module_path,
                                                      '%s.bz%s' % (testament, code))
                                         for code in ('v', 's', 'z')]
        return [open(name, 'rb') for name in (v2b_name, b2l_name, text_name)]

    def __get_rawtext_files(self, testament):
        '''Given a testament ('ot' or 'nt'), returns a tuple of files
        (verse_to_loc, text)
        '''
        v2l_name = os.path.join(self.__module_path, '%s.vss' % testament)
        text_name = os.path.join(self.__module_path, '%s' % testament)
        return [open(name, 'rb') for name in (v2l_name, text_name)]

    def __ztext_for_index(self, testament, index):
        '''Get the ztext for a given index.'''
        verse_to_buf, buf_to_loc, text = self.__files[testament]

        # Read the verse record, verse_len differs in ztext and ztext4.
        verse_to_buf.seek(self.__verse_record_size*index)
        buf_num, verse_start, verse_len = struct.unpack(self.__verse_record_format,
                                                        verse_to_buf.read(self.__verse_record_size))
        uncompressed_text = self.__uncompressed_text(testament, buf_num)
        return uncompressed_text[verse_start:verse_start+verse_len].decode(errors='replace')

    def __uncompressed_text(self, testament, buf_num):
        verse_to_buf, buf_to_loc, text = self.__files[testament]

        # Determine where the compressed data starts and ends.
        buf_to_loc.seek(buf_num*12)
        offset, size, uc_size = struct.unpack('<III', buf_to_loc.read(12))

        # Get the compressed data.
        text.seek(offset)
        compressed_data = text.read(size)
        return zlib.decompress(compressed_data)

    def __rawtext_for_index(self, testament, index):
        '''Get the rawtext for a given index.'''
        verse_to_loc, text = self.__files[testament]

        # Read the verse record.
        verse_to_loc.seek(self.__verse_record_size*index)
        verse_start, verse_len = struct.unpack(self.__verse_record_format, verse_to_loc.read(self.__verse_record_size))
        text.seek(verse_start)
        return text.read(verse_len).decode(errors='replace')

    ###### USER FACING #################################################################################
    def getiter(self, books=None, chapters=None, verses=None):
        '''Retrieve the text for a given reference'''
        indicies = self.__structure.ref_to_indicies(books=books, chapters=chapters, verses=verses)

        for testament, idxs in indicies.items():
            for idx in idxs:
                if self.__module_type in (SwordModuleType.ZTEXT, SwordModuleType.ZTEXT4):
                    yield self.__ztext_for_index(testament, idx)
                else:
                    yield self.__rawtext_for_index(testament, idx)

    def get(self, books=None, chapters=None, verses=None, join='\n'):
        output = []
        output.extend(list(self.getiter(books=books, chapters=chapters, verses=verses)))
        return join.join(output)
