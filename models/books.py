
class Books:
    id = 0
    author = ''
    title = ''
    isbn = ''
    year = ''
    
    def __init__(self, id, author, title, isbn, year):
        self.id = id
        self.author = author
        self.title = title
        self.isbn = isbn
        self.year = year
