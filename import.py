'''
Import: Provided for you in this project is a file called books.csv, which is a spreadsheet in CSV format of 5000 different books.
Each one has an ISBN number, a title, an author, and a publication year.

In a Python file called import.py separate from your web application, write a program that will take the books and import
them into your PostgreSQL database. You will first need to decide what table(s) to create, what columns those tables should have,
and how they should relate to one another. Run this program by running python3 import.py to import the books into your database,
and submit this program with the rest of your project code.
'''


import csv
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import text



# Set up database
engine = create_engine("postgresql://postgres:1898@localhost:5432/postgres")
db = scoped_session(sessionmaker(bind=engine))

# Set up Flask-Login - maybe don't need this?
#login_manager = LoginManager(app)
#login_manager.login_view = 'login'


# SAMPLE OF BOOKS CSV
#isbn	title	author	year
#1416949658	The Dark Is Rising	Susan Cooper	1973
#1857231082	The Black Unicorn 	Terry Brooks	1987

def create_books_table():
    query = text("""
        CREATE TABLE IF NOT EXISTS books (
            id SERIAL PRIMARY KEY,
            isbn VARCHAR NOT NULL,
            title VARCHAR NOT NULL,
            author VARCHAR NOT NULL,
            year INTEGER NOT NULL
        )
    """)
    db.execute(query) # just use execute not ORM
    db.commit()

def import_books_sql():
    # books.csv is in the same directory as import.py
    with open("books.csv", "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # this just skips the header row

        for row in reader:
            isbn, title, author, year = row
            query = text("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)")
            db.execute(query, {"isbn": isbn, "title": title, "author": author, "year": year})

    db.commit()




if __name__ == "__main__":
    create_books_table()
    print("Created books table")
    import_books_sql()
    print("Books imported to SQL successfully.")
