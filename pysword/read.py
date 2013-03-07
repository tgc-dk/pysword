class Passage(object):
    __slots__ = ('version', 'start', 'end')
    
    def __init__(self, version, start=None, stop=None):
        """
        Represets a Bible passage, which is a range of verses. Passages 
        can be grouped together in an ordered list by using PassageList.
        PassageList may be able to optimize access to sequential Passages.
        
        start and end are 4-tuples of the form
        (testament_index, book_index, chapter_index, verse_index)
        
        book_index 0 is used for the testament headings.
        chapter_index 0 is used for the book heading.
        verse_index 0 is used for the chapter heading.
        
        This means that while the testaments are 0 (OT) and 1 (NT), the 
        books, chapters, and verses have indexes starting at 1, which makes 
        the getitem syntax more meaningful:
        
        Passage('kjv')[0][1][1][1] is Genesis 1:1, KJV
        
        (x, 0, 0, 0) and (x, 0, 0, 1) are the testament headers
        (x, y, 0, 0) is the book header
        (x, y, z, 0) is the chapter header
        
        If no end index is given, then it displays everything that the 
        tuple specifies:
        
        Passage('kjv', (0, 1, 1, None)) is Genesis 1, KJV
            (including the chapter header)
        Passage('kjv', (0, 1, None, None)) is Genesis, KJV
            (including the book and all chapter headers)

        If nothing more than the version is given, the passage refers to 
        the whole Bible.

        Passage('kjv') is the Bible, KJV
            (including testament, book, and chapter headers)
        """
        self.version, self.start, self.stop = version, start, stop

    def __getitem__(self, key):
        if self.end:
            raise ValueError('Cannot get item of a Passage with an end')
        if self.start[-1]:
            raise ValueError('Only one verse')
        
        seed = tuple()
        if self.start:
            seed = tuple(x for x in self.start if x is not None)
        
        if isinstance(slice, key):
            # Slicing is different from Python slicing. It is _inclusive_
            # of the stop value.
            start, stop = key.start, key.stop
            if not isinstance(tuple, start):
                start = (start,)
            if not isinstance(tuple, stop):
                stop = (stop,)
            
            if len(start) > 4 - len(seed):
                raise ValueError('slice start tuple too long')
            if len(stop) > 4 - len(seed):
                raise ValueError('slice stop tuple too long')

            return type(self)(seed + start, seed + stop)
        else:
            if not isinstance(tuple, key):
                key = (key,)
            if len(key) > 4 - len(seed):
                raise ValueError('reference tuple too long')
            return type(self)(seed + start)
            
def book_finder(reference):
    """Take a reference tuple, and return a book function"""
    pass

def book(name_string):
    """Give a (testament, book) reference tuple for a name string of a book"""
    pass

#example useage:

#from canon import Bible, book
#Bible[book('gen')][1][2]
#Bible[(book('gen')+(1,1):(book('rev')+(2,2)]
