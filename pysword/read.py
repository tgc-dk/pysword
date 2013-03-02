"""Defines the objects and methods that access sword files on disk"""

import struct
import zlib

_VRS_STRUCT_FORMAT = '<IIH'
_BUF_STRUCT_FORMAT = '<III'

_VRS_FILE_EXT = '.bzv'
_BUF_FILE_EXT = '.bzs'

class TESTAMENT(object):
    """Enums for Old and New Testament"""
    OLD, NEW = 'ot', 'nt'


