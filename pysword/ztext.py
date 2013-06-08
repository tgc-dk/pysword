# * zText Format Mini-Documentation
#   each file is typically a testament
#
#   In zText, each "file" is separated into three files:
#
#   *.bzv: Maps verses to character ranges in compressed buffers
#     10 bytes ('<IIH' struct format string)
#     - buffer_num (I): the compressed buffer the verse is located in
#     - verse_start (I): the offset in the uncompressed buffer
#     - verse_len (H): the length of the verse, in uncompressed bytes
#     These records are indexed by VerseKey 'Indices'.
#     The verse reference must be translated to an VerseKey index to use.
#
#  *.bzs: Tells where the compressed buffers start and end
#     12 bytes ('<III' struct format string)
#     - offset (I): where the compressed buffer starts in the file
#     - size (I): the length of the compressed buffer, in bytes
#     - uc_size (I): the length of the uncompressed buffer, in bytes
#
#  *.bzz: The actual compressed text buffers, concatenated

from __future__ import unicode_literals
from collections import namedtuple
import os
import os.path
import struct
import zlib

class ZText(object):
    def __init__(self, path, encoding=None):
        if encoding is None:
            self.encoding = 'Latin-1'
        else:
            self.encoding = encoding
        self.path = path

    def read(self, filename, start_index, end_index=None):
        """Returns the passage given by the start and end indexes"""
        Index = namedtuple('Index', 'num start len')
        if end_index is None:
            end_index = start_index
        indexes = os.path.join(self.path, filename + '.bzv')
        with open(indexes, 'rb') as indexes:
            indexes.seek(start_index * 10)
            start = None
            for _ in range(start_index, end_index + 1):
                index = Index(*struct.unpack(b'<IIH', indexes.read(10)))
                if start == None:
                    start = end = index.num
                    offset = index.start
                    size = index.len
                elif index.num == start or index.num == end:
                    size += index.len
                else:
                    size = index.len

        buffers = self.get_buffers(filename, start, end, offset, size)
        return ''.join(x.decode(self.encoding) for x in buffers)

    def get_buffers(self, filename, start_index, end_index=None,
                    start_offset=None, end_size=None):
        """Yield the uncompressed byte buffers of sequential buffers"""
        if end_index is None:
            end_index = start_index
        indexes = os.path.join(self.path, filename + '.bzs')
        buffers = os.path.join(self.path, filename + '.bzz')

        with open(indexes, 'rb') as indexes, open(buffers, 'rb') as buffers:
            indexes.seek(start_index * 12)
            for i in range(start_index, end_index + 1):
                offset, size, uc_size = struct.unpack(b'<III', indexes.read(12))
                buffers.seek(offset)
                buffer = zlib.decompress(buffers.read(size))
                if i == start_index:
                    buffer = buffer[start_offset:]
                if i == end_index:
                    buffer = buffer[:end_size]
                yield buffer
