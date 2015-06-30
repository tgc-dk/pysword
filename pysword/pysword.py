#!/usr/bin/env python

# A native Python implementation of the SWORD Project Bible Reader
# Currently only ztext Bible modules are implemented.

# * ztext format documentation
# I'll use Python's struct module's format strings.
# See http://docs.python.org/lib/module-struct.html
# Take the Old Testament (OT) for example. Three files:
#
#  - ot.bzv: Maps verses to character ranges in compressed buffers.
#    10 bytes ('<IIH') for each verse in the Bible:
#    - buffer_num (I): which compressed buffer the verse is located in
#    - verse_start (I): the location in the uncompressed buffer where the verse begins
#    - verse_len (H): length of the verse, in uncompressed characters
#    These 10-byte records are densely packed, indexed by VerseKey 'Indicies' (docs later).
#    So the record for the verse with index x starts at byte 10*x.
#
#  - ot.bzs: Tells where the compressed buffers start and end.
#    12 bytes ('<III') for each compressed buffer:
#    - offset (I): where the compressed buffer starts in the file
#    - size (I): the length of the compressed data, in bytes
#    - uc_size (I): the length of the uncompressed data, in bytes (unused)
#    These 12-byte records are densely packed, indexed by buffer_num (see previous).
#    So the record for compressed buffer buffer_num starts at byte 12*buffer_num.
#
#  - ot.bzz: Contains the compressed text. Read 'size' bytes starting at 'offset'.
#
#  NT is analogous.
#
# Example usage:
#  python pysword.py /path/to/modules/ esv 1pet 2 9
#  python pysword.py /path/to/modules/ esv 1pet 2     (displays entire chapter)

import os, struct, zlib
from os.path import join as path_join

from .books import BibleStructure
modules_path = os.environ["HOME"]+"/.sword/modules/texts/ztext"

class SwordBible(object):

    def __init__(self, module):
        self.__structure = BibleStructure()
        self.__module = module
        self.__files = {
            'ot': None,
            'nt': None 
            }
        try: self.__files['ot'] = self.__get_files('ot')
        except IOError: pass
        try: self.__files['nt'] = self.__get_files('nt')
        except IOError: pass
        if self.__files['ot'] is None and self.__files['nt'] is None:
          raise Error('Could not open OT or NT for module')
   
    def __get_files(self, testament):
        '''Given a testament ('ot' or 'nt'), returns a tuple of files
        (verse_to_buf, buf_to_loc, text)
        '''
        base = path_join(modules_path, self.__module)
        v2b_name, b2l_name, text_name = [path_join(base, '%s.bz%s' % (testament, code))
                                         for code in ('v', 's', 'z')]
        return [open(name, 'rb') for name in (v2b_name, b2l_name, text_name)]

    def __text_for_index(self, testament, index):
        '''Get the text for a given index.'''
        verse_to_buf, buf_to_loc, text = self.__files[testament]

        # Read the verse record.
        verse_to_buf.seek(10*index)
        buf_num, verse_start, verse_len = struct.unpack('<IIH', verse_to_buf.read(10))
       
        uncompressed_text = self.__uncompressed_text(testament, buf_num)
        return uncompressed_text[verse_start:verse_start+verse_len]

    def __uncompressed_text(self, testament, buf_num):
        verse_to_buf, buf_to_loc, text = self.__files[testament]

        # Determine where the compressed data starts and ends.
        buf_to_loc.seek(buf_num*12)
        offset, size, uc_size = struct.unpack('<III', buf_to_loc.read(12))

        # Get the compressed data.
        text.seek(offset)
        compressed_data = text.read(size)
        return zlib.decompress(compressed_data)

    ###### USER FACING #################################################################################
    def getiter(self, books=None, chapters=None, verses=None):
        '''Retrieve the text for a given reference'''
        indicies = self.__structure.ref_to_indicies(books=books, chapters=chapters, verses=verses)

        for testament,idxs in indicies.items():
            for idx in idxs:
                yield self.__text_for_index(testament, idx).decode()

    def get(self, books=None, chapters=None, verses=None, join='\n'):
        output = []
        output.extend(list(self.getiter(books=books,chapters=chapters,verses=verses)))
        return join.join(output)
