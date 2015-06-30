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

    def chapter_offset(self,chapter_index):
        # Add chapter lengths to this point; plus 1 for every chapter title; plus 1 for book title
        return sum(self.chapter_lengths[:chapter_index]) + (chapter_index + 1) + 1

    def get_indicies(self, chapters=None, verses=None, offset=0):
        if chapters is None:
            chapters = list(range(1,self.num_chapters+1))
        elif isinstance(chapters,int):
            chapters = [chapters]
        if len(chapters) != 1:
            verses = None
        elif isinstance(verses,int):
            verses = [verses]

        refs = []
        for chapter in chapters:
            if verses is None:
                tmp_verses = list(range(1,self.chapter_lengths[chapter-1]+1))
            else:
                tmp_verses = verses
            refs.extend( [offset + self.chapter_offset(chapter-1) + verse-1 for verse in tmp_verses])
        return refs

    @property
    def size(self):
        # Total verses + chapter heading for each chapter + 1 for book title
        return sum(self.chapter_lengths) + len(self.chapter_lengths) + 1

class BibleStructure(object):

    def __init__(self):
        self.__section_order = ['ot','nt']
        self.__book_offsets = None # offsets within sections

        # This data came from canon.h in the SWORD repository. Code to transform it to
        # this form can be found in the repository history.
        self.__books = {
            'ot': [
                BookStructure('Genesis', 'Gen', 'Gen', [31, 25, 24, 26, 32, 22, 24, 22, 29, 32, 32, 20, 18, 24, 21, 16, 27, 33, 38, 18, 34, 24, 20, 67, 34, 35, 46, 22, 35, 43, 55, 32, 20, 31, 29, 43, 36, 30, 23, 23, 57, 38, 34, 34, 28, 34, 31, 22, 33, 26]),
                BookStructure('Exodus', 'Exod', 'Exod', [22, 25, 22, 31, 23, 30, 25, 32, 35, 29, 10, 51, 22, 31, 27, 36, 16, 27, 25, 26, 36, 31, 33, 18, 40, 37, 21, 43, 46, 38, 18, 35, 23, 35, 35, 38, 29, 31, 43, 38]),
                BookStructure('Leviticus', 'Lev', 'Lev', [17, 16, 17, 35, 19, 30, 38, 36, 24, 20, 47, 8, 59, 57, 33, 34, 16, 30, 37, 27, 24, 33, 44, 23, 55, 46, 34]),
                BookStructure('Numbers', 'Num', 'Num', [54, 34, 51, 49, 31, 27, 89, 26, 23, 36, 35, 16, 33, 45, 41, 50, 13, 32, 22, 29, 35, 41, 30, 25, 18, 65, 23, 31, 40, 16, 54, 42, 56, 29, 34, 13]),
                BookStructure('Deuteronomy', 'Deut', 'Deut', [46, 37, 29, 49, 33, 25, 26, 20, 29, 22, 32, 32, 18, 29, 23, 22, 20, 22, 21, 20, 23, 30, 25, 22, 19, 19, 26, 68, 29, 20, 30, 52, 29, 12]),
                BookStructure('Joshua', 'Josh', 'Josh', [18, 24, 17, 24, 15, 27, 26, 35, 27, 43, 23, 24, 33, 15, 63, 10, 18, 28, 51, 9, 45, 34, 16, 33]),
                BookStructure('Judges', 'Judg', 'Judg', [36, 23, 31, 24, 31, 40, 25, 35, 57, 18, 40, 15, 25, 20, 20, 31, 13, 31, 30, 48, 25]),
                BookStructure('Ruth', 'Ruth', 'Ruth', [22, 23, 18, 22]),
                BookStructure('I Samuel', '1Sam', '1Sam', [28, 36, 21, 22, 12, 21, 17, 22, 27, 27, 15, 25, 23, 52, 35, 23, 58, 30, 24, 42, 15, 23, 29, 22, 44, 25, 12, 25, 11, 31, 13]),
                BookStructure('II Samuel', '2Sam', '2Sam', [27, 32, 39, 12, 25, 23, 29, 18, 13, 19, 27, 31, 39, 33, 37, 23, 29, 33, 43, 26, 22, 51, 39, 25]),
                BookStructure('I Kings', '1Kgs', '1Kgs', [53, 46, 28, 34, 18, 38, 51, 66, 28, 29, 43, 33, 34, 31, 34, 34, 24, 46, 21, 43, 29, 53]),
                BookStructure('II Kings', '2Kgs', '2Kgs', [18, 25, 27, 44, 27, 33, 20, 29, 37, 36, 21, 21, 25, 29, 38, 20, 41, 37, 37, 21, 26, 20, 37, 20, 30]),
                BookStructure('I Chronicles', '1Chr', '1Chr', [54, 55, 24, 43, 26, 81, 40, 40, 44, 14, 47, 40, 14, 17, 29, 43, 27, 17, 19, 8, 30, 19, 32, 31, 31, 32, 34, 21, 30]),
                BookStructure('II Chronicles', '2Chr', '2Chr', [17, 18, 17, 22, 14, 42, 22, 18, 31, 19, 23, 16, 22, 15, 19, 14, 19, 34, 11, 37, 20, 12, 21, 27, 28, 23, 9, 27, 36, 27, 21, 33, 25, 33, 27, 23]),
                BookStructure('Ezra', 'Ezra', 'Ezra', [11, 70, 13, 24, 17, 22, 28, 36, 15, 44]),
                BookStructure('Nehemiah', 'Neh', 'Neh', [11, 20, 32, 23, 19, 19, 73, 18, 38, 39, 36, 47, 31]),
                BookStructure('Esther', 'Esth', 'Esth', [22, 23, 15, 17, 14, 14, 10, 17, 32, 3]),
                BookStructure('Job', 'Job', 'Job', [22, 13, 26, 21, 27, 30, 21, 22, 35, 22, 20, 25, 28, 22, 35, 22, 16, 21, 29, 29, 34, 30, 17, 25, 6, 14, 23, 28, 25, 31, 40, 22, 33, 37, 16, 33, 24, 41, 30, 24, 34, 17]),
                BookStructure('Psalms', 'Ps', 'Ps', [6, 12, 8, 8, 12, 10, 17, 9, 20, 18, 7, 8, 6, 7, 5, 11, 15, 50, 14, 9, 13, 31, 6, 10, 22, 12, 14, 9, 11, 12, 24, 11, 22, 22, 28, 12, 40, 22, 13, 17, 13, 11, 5, 26, 17, 11, 9, 14, 20, 23, 19, 9, 6, 7, 23, 13, 11, 11, 17, 12, 8, 12, 11, 10, 13, 20, 7, 35, 36, 5, 24, 20, 28, 23, 10, 12, 20, 72, 13, 19, 16, 8, 18, 12, 13, 17, 7, 18, 52, 17, 16, 15, 5, 23, 11, 13, 12, 9, 9, 5, 8, 28, 22, 35, 45, 48, 43, 13, 31, 7, 10, 10, 9, 8, 18, 19, 2, 29, 176, 7, 8, 9, 4, 8, 5, 6, 5, 6, 8, 8, 3, 18, 3, 3, 21, 26, 9, 8, 24, 13, 10, 7, 12, 15, 21, 10, 20, 14, 9, 6]),
                BookStructure('Proverbs', 'Prov', 'Prov', [33, 22, 35, 27, 23, 35, 27, 36, 18, 32, 31, 28, 25, 35, 33, 33, 28, 24, 29, 30, 31, 29, 35, 34, 28, 28, 27, 28, 27, 33, 31]),
                BookStructure('Ecclesiastes', 'Eccl', 'Eccl', [18, 26, 22, 16, 20, 12, 29, 17, 18, 20, 10, 14]),
                BookStructure('Song of Solomon', 'Song', 'Song', [17, 17, 11, 16, 16, 13, 13, 14]),
                BookStructure('Isaiah', 'Isa', 'Isa', [31, 22, 26, 6, 30, 13, 25, 22, 21, 34, 16, 6, 22, 32, 9, 14, 14, 7, 25, 6, 17, 25, 18, 23, 12, 21, 13, 29, 24, 33, 9, 20, 24, 17, 10, 22, 38, 22, 8, 31, 29, 25, 28, 28, 25, 13, 15, 22, 26, 11, 23, 15, 12, 17, 13, 12, 21, 14, 21, 22, 11, 12, 19, 12, 25, 24]),
                BookStructure('Jeremiah', 'Jer', 'Jer', [19, 37, 25, 31, 31, 30, 34, 22, 26, 25, 23, 17, 27, 22, 21, 21, 27, 23, 15, 18, 14, 30, 40, 10, 38, 24, 22, 17, 32, 24, 40, 44, 26, 22, 19, 32, 21, 28, 18, 16, 18, 22, 13, 30, 5, 28, 7, 47, 39, 46, 64, 34]),
                BookStructure('Lamentations', 'Lam', 'Lam', [22, 22, 66, 22, 22]),
                BookStructure('Ezekiel', 'Ezek', 'Ezek', [28, 10, 27, 17, 17, 14, 27, 18, 11, 22, 25, 28, 23, 23, 8, 63, 24, 32, 14, 49, 32, 31, 49, 27, 17, 21, 36, 26, 21, 26, 18, 32, 33, 31, 15, 38, 28, 23, 29, 49, 26, 20, 27, 31, 25, 24, 23, 35]),
                BookStructure('Daniel', 'Dan', 'Dan', [21, 49, 30, 37, 31, 28, 28, 27, 27, 21, 45, 13]),
                BookStructure('Hosea', 'Hos', 'Hos', [11, 23, 5, 19, 15, 11, 16, 14, 17, 15, 12, 14, 16, 9]),
                BookStructure('Joel', 'Joel', 'Joel', [20, 32, 21]),
                BookStructure('Amos', 'Amos', 'Amos', [15, 16, 15, 13, 27, 14, 17, 14, 15]),
                BookStructure('Obadiah', 'Obad', 'Obad', [21]),
                BookStructure('Jonah', 'Jonah', 'Jonah', [17, 10, 10, 11]),
                BookStructure('Micah', 'Mic', 'Mic', [16, 13, 12, 13, 15, 16, 20]),
                BookStructure('Nahum', 'Nah', 'Nah', [15, 13, 19]),
                BookStructure('Habakkuk', 'Hab', 'Hab', [17, 20, 19]),
                BookStructure('Zephaniah', 'Zeph', 'Zeph', [18, 15, 20]),
                BookStructure('Haggai', 'Hag', 'Hag', [15, 23]),
                BookStructure('Zechariah', 'Zech', 'Zech', [21, 13, 10, 14, 11, 15, 14, 23, 17, 12, 17, 14, 9, 21]),
                BookStructure('Malachi', 'Mal', 'Mal', [14, 17, 18, 6]),
            ],
            'nt': [
                BookStructure('Matthew', 'Matt', 'Matt', [25, 23, 17, 25, 48, 34, 29, 34, 38, 42, 30, 50, 58, 36, 39, 28, 27, 35, 30, 34, 46, 46, 39, 51, 46, 75, 66, 20]),
                BookStructure('Mark', 'Mark', 'Mark', [45, 28, 35, 41, 43, 56, 37, 38, 50, 52, 33, 44, 37, 72, 47, 20]),
                BookStructure('Luke', 'Luke', 'Luke', [80, 52, 38, 44, 39, 49, 50, 56, 62, 42, 54, 59, 35, 35, 32, 31, 37, 43, 48, 47, 38, 71, 56, 53]),
                BookStructure('John', 'John', 'John', [51, 25, 36, 54, 47, 71, 53, 59, 41, 42, 57, 50, 38, 31, 27, 33, 26, 40, 42, 31, 25]),
                BookStructure('Acts', 'Acts', 'Acts', [26, 47, 26, 37, 42, 15, 60, 40, 43, 48, 30, 25, 52, 28, 41, 40, 34, 28, 41, 38, 40, 30, 35, 27, 27, 32, 44, 31]),
                BookStructure('Romans', 'Rom', 'Rom', [32, 29, 31, 25, 21, 23, 25, 39, 33, 21, 36, 21, 14, 23, 33, 27]),
                BookStructure('I Corinthians', '1Cor', '1Cor', [31, 16, 23, 21, 13, 20, 40, 13, 27, 33, 34, 31, 13, 40, 58, 24]),
                BookStructure('II Corinthians', '2Cor', '2Cor', [24, 17, 18, 18, 21, 18, 16, 24, 15, 18, 33, 21, 14]),
                BookStructure('Galatians', 'Gal', 'Gal', [24, 21, 29, 31, 26, 18]),
                BookStructure('Ephesians', 'Eph', 'Eph', [23, 22, 21, 32, 33, 24]),
                BookStructure('Philippians', 'Phil', 'Phil', [30, 30, 21, 23]),
                BookStructure('Colossians', 'Col', 'Col', [29, 23, 25, 18]),
                BookStructure('I Thessalonians', '1Thess', '1Thess', [10, 20, 13, 18, 28]),
                BookStructure('II Thessalonians', '2Thess', '2Thess', [12, 17, 18]),
                BookStructure('I Timothy', '1Tim', '1Tim', [20, 15, 16, 16, 25, 21]),
                BookStructure('II Timothy', '2Tim', '2Tim', [18, 26, 17, 22]),
                BookStructure('Titus', 'Titus', 'Titus', [16, 15, 15]),
                BookStructure('Philemon', 'Phlm', 'Phlm', [25]),
                BookStructure('Hebrews', 'Heb', 'Heb', [14, 18, 19, 16, 14, 20, 28, 13, 28, 39, 40, 29, 25]),
                BookStructure('James', 'Jas', 'Jas', [27, 26, 18, 17, 20]),
                BookStructure('I Peter', '1Pet', '1Pet', [25, 25, 22, 19, 14]),
                BookStructure('II Peter', '2Pet', '2Pet', [21, 22, 18]),
                BookStructure('I John', '1John', '1John', [10, 29, 24, 21, 21]),
                BookStructure('II John', '2John', '2John', [13]),
                BookStructure('III John', '3John', '3John', [14]),
                BookStructure('Jude', 'Jude', 'Jude', [25]),
                BookStructure('Revelation of John', 'Rev', 'Rev', [20, 29, 22, 11, 14, 17, 17, 13, 21, 11, 19, 17, 18, 20, 8, 21, 18, 24, 21, 15, 27, 21]),
            ],
        }

    def __update_book_offsets(self):
        # Compute index offsets and add other data
        # FIXME: this is still a little hairy.
        self.__book_offsets = {}
        for testament, books in self.__books.items():
            idx = 2 # start after the testament heading
            for book in books:
                self.__book_offsets[book.name] = idx
                offset = 1 # start after the book heading
                idx += book.size

    def __book_offset(self,book_name):
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
        elif isinstance(books,str):
            books = [books]

        refs = {}
        for book in books:
            testament, book = self.find_book(book)
            if testament not in refs:
                refs[testament] = []
            refs[testament].extend(book.get_indicies(chapters=chapters,verses=verses,offset=self.__book_offset(book.name)))
            # Deal with the one book presented.

        return refs