import csv
from application import db


with open('books.csv') as file:
   reader =  csv.reader(file)

   for isbn, title, author , year  in reader:
        db.execute("INSERT INTO Books (isbn, title, author, year) VALUES(:isbn, :title, :author, :year)",
         {"isbn":isbn, "title": title, "author": author, "year": year}   
        ) 
        print(f"Book with isbn{isbn} and title {title} and author{author} and year {year} is added")
   db.commit()    