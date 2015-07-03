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

from .canons import *


class BookStructure(object):
    def __init__(self, name, osis_name, preferred_abbreviation, chapter_lengths):
        self.name = name
        self.osis_name = osis_name
        self.preferred_abbreviation = preferred_abbreviation
        self.chapter_lengths = chapter_lengths
        self.num_chapters = len(chapter_lengths)

    def __repr__(self):
        return 'Book(%s)' % self.name

    def name_matches(self, name):
        name = name.lower()
        return name in [self.name.lower(), self.osis_name.lower(), self.preferred_abbreviation.lower()]

    def chapter_offset(self, chapter_index):
        # Add chapter lengths to this point; plus 1 for every chapter title; plus 1 for book title
        return sum(self.chapter_lengths[:chapter_index]) + (chapter_index + 1) + 1

    def get_indicies(self, chapters=None, verses=None, offset=0):
        if chapters is None:
            chapters = list(range(1, self.num_chapters+1))
        elif isinstance(chapters, int):
            chapters = [chapters]
        if len(chapters) != 1:
            verses = None
        elif isinstance(verses, int):
            verses = [verses]

        refs = []
        for chapter in chapters:
            if verses is None:
                tmp_verses = list(range(1, self.chapter_lengths[chapter-1]+1))
            else:
                tmp_verses = verses
            refs.extend([offset + self.chapter_offset(chapter-1) + verse-1 for verse in tmp_verses])
        return refs

    @property
    def size(self):
        # Total verses + chapter heading for each chapter + 1 for book title
        return sum(self.chapter_lengths) + len(self.chapter_lengths) + 1


class BibleStructure(object):

    def __init__(self, versification):
        self.__section_order = ['ot', 'nt']
        self.__book_offsets = None  # offsets within sections

        self.__books = {
            'ot': [],
            'nt': [],
        }
        # Find the canon used. The canons are original defined in SWORD header files.
        canon = default
        if versification == 'catholic2':
            canon = catholic2
        elif versification == 'german':
            canon = german
        elif versification == 'kjva':
            canon = kjva
        elif versification == 'leningrad':
            canon = leningrad
        elif versification == 'luther':
            canon = luther
        elif versification == 'lxx':
            canon = lxx
        elif versification == 'mt':
            canon = mt
        elif versification == 'nrsva':
            canon = nrsva
        elif versification == 'nrsv':
            canon = nrsv
        elif versification == 'orthodox':
            canon = orthodox
        elif versification == 'synodal':
            canon = synodal
        elif versification == 'synodalprot':
            canon = synodalprot
        elif versification == 'vulg':
            canon = vulg
        # Based on the canon create the BookStructure objects needed
        for book in canon['ot']:
            self.__books['ot'].append(BookStructure(*book))
        for book in canon['nt']:
            self.__books['nt'].append(BookStructure(*book))

    def __update_book_offsets(self):
        # Compute index offsets and add other data
        # FIXME: this is still a little hairy.
        self.__book_offsets = {}
        for testament, books in self.__books.items():
            idx = 2  # start after the testament heading
            for book in books:
                self.__book_offsets[book.name] = idx
                offset = 1  # start after the book heading
                idx += book.size

    def __book_offset(self, book_name):
        if self.__book_offsets is None:
            self.__update_book_offsets()
        return self.__book_offsets[book_name]

    def find_book(self, name):
        name = name.lower()
        for testament, books in self.__books.items():
            for num, book in enumerate(books):
                if book.name_matches(name):
                    return testament, book
        raise ValueError("Book name \'%s\' does not exist in BibleStructure." % name)

    def ref_to_indicies(self, books=None, chapters=None, verses=None):
        # TODO: CHECK NOT OVERSPECIFIED
        if books is None:
            # Return all books
            books = []
            for section in self.__books:
                books.extend([b.name for b in self.__books[section]])
        elif isinstance(books, str):
            books = [books]

        refs = {}
        for book in books:
            testament, book = self.find_book(book)
            if testament not in refs:
                refs[testament] = []
            refs[testament].extend(book.get_indicies(chapters=chapters, verses=verses,
                                                     offset=self.__book_offset(book.name)))
            # Deal with the one book presented.
        return refs
