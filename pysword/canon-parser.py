#!/usr/bin/env python3

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

# Util to convert SWORD canon header files into pysword format.
# Note that some canon headers doesn't contain a ntbooks struct, but instead in comments points to other
# canons ntbooks structs. This is not detected by this script. Because of this we also assume that canons
# that does not include a book list of a testament also uses the versenumbers of the replacement it points to.
#
# Batch convertion example:
# for f in canon*.h; do python3 canon-parser.py $f >> canons.py; done

import os


def parse_canon_header(filename):
    # Open file
    canon_header = open(filename, 'rt')
    fulltext = canon_header.read()
    # Detect if OT books are listed
    otbooks_pos = fulltext.find('struct sbook otbooks')
    if otbooks_pos > 0:
        # Find the declaration of the OT struct, first instance of "struct sbook otbooks[] = {",
        # but we just search for the last part
        ot_struct_start = fulltext.find('= {', otbooks_pos) + 4
        # Find end of OT struct
        ot_struct_end = fulltext.find('};', ot_struct_start)
        # Extract OT struct
        ot_struct = fulltext[ot_struct_start:ot_struct_end]
    else:
        ot_struct = ''
    # Detect if NT books are listed
    ntbooks_pos = fulltext.find('struct sbook ntbooks')
    if ntbooks_pos > 0:
        # Find start NT struct
        nt_struct_start = fulltext.find('= {', ntbooks_pos) + 4
        # Find end of NT struct
        nt_struct_end = fulltext.find('};', nt_struct_start)
        # Extract NT struct
        nt_struct = fulltext[nt_struct_start:nt_struct_end]
    else:
        nt_struct = ''
    verse_struct_loc = fulltext.find('int vm')
    # Find start verse number struct
    verse_struct_start = fulltext.find('= {', verse_struct_loc) + 4
    # Find end verse number struct
    verse_struct_end = fulltext.find('};', verse_struct_start)
    # Extract verse struct
    verse_struct = fulltext[verse_struct_start:verse_struct_end]
    # Convert/evaluate the ot and nt structs into python
    ot = eval('[' + ot_struct.replace('{', '[').replace('}', ']') + ']')
    nt = eval('[' + nt_struct.replace('{', '[').replace('}', ']') + ']')
    # Convert/evaluate the verse struct into python
    verses_per_chapter = eval('[' + verse_struct.replace('//', '#') + ']')
    # Print the structure in the format pysword uses
    name = os.path.splitext(os.path.basename(filename))[0][6:]
    idx = 0
    print(name + ' = {')
    for testament, contents in (('ot', ot), ('nt', nt)):
        print('%r: [' % testament)
        for num, (name, osis, pref_abbr, num_chapters) in enumerate(contents):
            new_idx = idx + num_chapters
            if name:
                print('(%r, %r, %r, %r),' % (name, osis, pref_abbr, verses_per_chapter[idx:new_idx]))
            idx = new_idx
        print('],')
    print('}')

if __name__ == '__main__':
    import sys
    canon_file_name = sys.argv[1]
    parse_canon_header(canon_file_name)
