A native Python3 reader of the SWORD Project Bible Modules

## Features
* Read SWORD bibles (not commentaries etc.)
* Detection of available modules (bibles).
* Supports all known SWORD module formats (ztext, ztext4, rawtext, rawtext4)

## TODO
* Clean text of OSIS and GBF tags.
* Support reading from zipped modules.

## License
Since parts of the code is derived and/or copied (see canons.py) from the SWORD project
which is GPL2, this code is also under the GPL2 license.

## Example code
```python
from pysword.modules import SwordModules
# Find available modules/bibles
modules = SwordModules()
# In this case we'll assume the modules found is:
# {'KJV': 'King James Version (1769) with Strongs Numbers and Morphology'}
found_modules = modules.parse_modules();
bible = modules.get_bible_from_module('KJV')
# Get John chapter 3 verse 16
output = bible.get(books=['john'], chapters=[3], verses=[16])
```

## Module formats
I'll use Python's struct module's format strings to describe byte formatting.
See https://docs.python.org/3/library/struct.html

There are current 4 formats for bible modules in SWORD.

### ztext format documentation
Take the Old Testament (OT) for example. Three files:

- ot.bzv: Maps verses to character ranges in compressed buffers.
  10 bytes ('<IIH') for each verse in the Bible:
    - buffer_num (I): which compressed buffer the verse is located in
    - verse_start (I): the location in the uncompressed buffer where the verse begins
    - verse_len (H): length of the verse, in uncompressed characters

  These 10-byte records are densely packed, indexed by VerseKey 'Indicies' (docs later).
  So the record for the verse with index x starts at byte 10*x.

- ot.bzs: Tells where the compressed buffers start and end.
   12 bytes ('<III') for each compressed buffer:
     - offset (I): where the compressed buffer starts in the file
     - size (I): the length of the compressed data, in bytes
     - uc_size (I): the length of the uncompressed data, in bytes (unused)

   These 12-byte records are densely packed, indexed by buffer_num (see previous).
   So the record for compressed buffer buffer_num starts at byte 12*buffer_num.

- ot.bzz: Contains the compressed text. Read 'size' bytes starting at 'offset'.

### ztext4 format documentation
ztext4 is the same as ztext, except that in the bzv-file the verse_len is now
represented by 4-byte integer (I), making the record 12 bytes in all.

### rawtext format documentation
Again OT example. Two files:

- ot.vss: Maps verses to character ranges in text file.
  6 bytes ('<IH') for each verse in the Bible:
    - verse_start (I): the location in the textfile where the verse begins
    - verse_len (H): length of the verse, in characters

- ot: Contains the text. Read 'verse_len' characters starting at 'verse_start'.

### rawtext4 format documentation
rawtext4 is the same as rawtext, except that in the vss-file the verse_len is now
represented by 4-byte integer (I), making the record 8 bytes in all.
