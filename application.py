import os
from flask import Flask, render_template, request, redirect, url_for, flash, abort, jsonify
from flask_session import Session
from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.schema import UniqueConstraint
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy import text
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import requests
from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)

# Define the Base class
Base = declarative_base()

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine("postgresql://postgres:1898@localhost:5432/postgres")
db = scoped_session(sessionmaker(bind=engine))

# Set up Flask-Login
login_manager = LoginManager(app)
login_manager.login_view = 'login'


import requests
res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": "isbn:080213825X"})
print(res.json())

# User model
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

    @staticmethod
    def get(user_id):
        user = db.execute("SELECT * FROM users WHERE id = :id", {"id": user_id}).fetchone()
        if user:
            return User(user_id)
        return None


@login_manager.user_loader
def load_user(user_id):
    query = text("SELECT * FROM users WHERE id = :id")
    user = db.execute(query, {"id": user_id}).fetchone()
    if user:
        return User(user.id)
    return None

#@app.route("/")
#def index():
  #  return "Project 1: TODO"

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the username is already taken
        if db.execute("SELECT * FROM users WHERE username = :username", {"username": username}).fetchone():
            flash("Username already taken. Choose another one.")
        else:
            query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
            db.execute(query, {"username": username, "password": password})
            db.commit()

            flash("Registration successful. You can now log in.")
            return redirect(url_for("login"))

    return render_template("register.html")


# ********** LOG IN **************
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")

        # Check if the username and password are correct
        user = db.execute(text("SELECT * FROM users WHERE username = :username AND password = :password"),
                          {"username": username, "password": password}).fetchone()

        if user:
            user_obj = User(user.id)
            login_user(user_obj)
            flash("Login successful.")
            return redirect(url_for("search"))  # Redirect to the search route
        else:
            flash("Invalid username or password.")

    return render_template("login.html")

# ********** LOG OUT **************
@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("index"))


# FUNCTION TO SEARCH BOOKS
def search_books(db, search_query):
    # Perform a case-insensitive search on ISBN, title, and author
    query = text("""
        SELECT * FROM books
        WHERE LOWER(isbn) LIKE LOWER(:search_query)
           OR LOWER(title) LIKE LOWER(:search_query)
           OR LOWER(author) LIKE LOWER(:search_query)
    """)

    # Execute the query with the search query as a parameter
    results = db.execute(query, {"search_query": f"%{search_query}%"}).fetchall()

    # Convert the results to a list of dictionaries
    books = [{"isbn": result.isbn, "title": result.title, "author": result.author, "year": result.year} for result in results]

    return books


# SEARCH ROUTE
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        search_query = request.form.get("search_query")
        matching_books = search_books(db, search_query)
        return render_template("search.html", books=matching_books, search_query=search_query)
    else:
        return render_template("search.html", books=[], search_query="")

#trying to get google books to work
'''
def get_book_details(isbn):
    api_key = "AIzaSyDltVf3cU12JB-9HH2MnZ0973NnMNFB2FE"
    api_url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}&key={api_key}"

    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if "items" in data and data["items"]:
            book_info = data["items"][0]["volumeInfo"]
            book_details = {
                "title": book_info.get("title", ""),
                "author": ", ".join(book_info.get("authors", [])),
                "year": book_info.get("publishedDate", "")[:4],
                "isbn": isbn,
                # Add more details as needed
            }
            return book_details

    # Print the response content for debugging
    print(response.content)
    return None
'''


def get_book_details(isbn):
    # Query the database to get book details
    query = text("SELECT * FROM books WHERE isbn = :isbn")
    result = db.execute(query, {"isbn": isbn}).fetchone()

    if result:
        book_details = {
            "title": result.title,
            "author": result.author,
            "year": result.year,
            "isbn": isbn,
            # Add more details as needed
        }
        return book_details

    return None

def get_google_books_review_data(isbn):
    res = requests.get("https://www.googleapis.com/books/v1/volumes", params={"q": f"isbn:{isbn}"})
    if res.status_code == 200:
        data = res.json()
        if data["totalItems"] > 0:
            book_data = data["items"][0]  # Assuming the first item is the desired one
            text_snippet = book_data.get("searchInfo", {}).get("textSnippet", "Description not available.")
            return {
                "averageRating": book_data["volumeInfo"].get("averageRating", "N/A"),
                "ratingsCount": book_data["volumeInfo"].get("ratingsCount", "N/A"),
                "textSnippet": text_snippet
            }
    return {"averageRating": "N/A", "ratingsCount": "N/A", "textSnippet": "Description not available."}


class Review(Base):
    __tablename__ = 'reviews'

    id = Column(Integer, primary_key=True)
    book_isbn = Column(String, ForeignKey('books.isbn'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)  # 'users.id' matches the 'id' column in the 'users' table
    rating = Column(Integer, nullable=False)
    review_text = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (UniqueConstraint('book_isbn', 'user_id', name='uix_1'),)

# Function to add a review
def add_review(db, isbn, user_id, rating, comment):
    print(f"Inserting review: ISBN={isbn}, User ID={user_id}, Rating={rating}, Comment={comment}")
    query = text("INSERT INTO reviews (isbn, user_id, rating, review_text) VALUES (:isbn, :user_id, :rating, :comment)")
    db.execute(query, {"isbn": isbn, "user_id": user_id, "rating": rating, "comment": comment})
    db.commit()



# Function to get reviews for a book
def get_reviews(db, isbn):
    query = text("SELECT * FROM reviews WHERE isbn = :isbn ORDER BY created_at DESC")
    results = db.execute(query, {"isbn": isbn}).fetchall()

    reviews = [{
        "user_id": result.user_id,
        "rating": result.rating,
        "comment": result.review_text,
        "created_at": result.created_at
    } for result in results]

    return reviews


@app.route('/book/<isbn>', methods=['GET', 'POST'])
def book(isbn):
    if request.method == 'POST' and current_user.is_authenticated:
        user_id = int(current_user.get_id())  # Cast user_id to integer
        print(f"Current User ID: {user_id}")
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')

        # Check for existing review
        existing_review = db.execute(text('SELECT * FROM reviews WHERE isbn = :isbn AND user_id = :user_id'),
                                     {'isbn': isbn, 'user_id': user_id}).fetchone()
        if existing_review:
            flash('You have already reviewed this book.')
            print("Duplicate review attempt detected")  # Additional logging
            return redirect(url_for('book', isbn=isbn))

        # Ensure book exists
        book_exists = db.execute(text('SELECT * FROM books WHERE isbn = :isbn'), {'isbn': isbn}).fetchone()
        if not book_exists:
            flash("Book not found.")
            return redirect(url_for('index'))

        try:
            # Attempt to insert the review
            db.execute(text(
                'INSERT INTO reviews (isbn, user_id, rating, review_text) VALUES (:isbn, :user_id, :rating, :comment)'),
                {'isbn': isbn, 'user_id': user_id, 'rating': rating, 'comment': comment})
            db.commit()
            flash('Your review has been added.')
        except IntegrityError:
            # Rollback in case of a constraint violation (e.g., duplicate review)
            db.rollback()
            flash('You have already reviewed this book.')
        return redirect(url_for('book', isbn=isbn))



    # Retrieve book details and reviews for GET requests or after handling POST
    book = db.execute(text('SELECT * FROM books WHERE isbn = :isbn'), {'isbn': isbn}).fetchone()
    reviews = db.execute(text('SELECT * FROM reviews WHERE isbn = :isbn ORDER BY created_at DESC'),
                         {'isbn': isbn}).fetchall()

    # Fetch Google Books review data
    google_books_data = get_google_books_review_data(isbn)

    return render_template('book.html', book=book, reviews=reviews, google_books_data=google_books_data)

@app.route("/api/<isbn>") # NEW for task #4
def api_isbn(isbn):
    # Query the database for the book with the provided ISBN
    book = db.execute(text("SELECT * FROM books WHERE isbn = :isbn"), {"isbn": isbn}).fetchone()

    # If the book doesn't exist, return a 404 error
    if book is None:
        return jsonify({"error": "Invalid ISBN"}), 404

    # extra query to get stuff
    review_stats = db.execute(text("""
        SELECT COUNT(*) AS review_count, AVG(rating) AS average_rating
        FROM reviews
        WHERE isbn = :isbn
        GROUP BY isbn
    """), {"isbn": isbn}).fetchone()

    #json response
    response = {
        "title": book.title,
        "author": book.author,
        "publishedDate": book.year,  # Assuming 'year' corresponds to 'publishedDate'
        "ISBN_10": isbn if len(isbn) == 10 else None,
        "ISBN_13": isbn if len(isbn) == 13 else None,
        "reviewCount": review_stats.review_count if review_stats else 0,
        "averageRating": float(review_stats.average_rating) if review_stats else 0
    }

    return jsonify(response)



if __name__ == "__main__":
    app.secret_key = os.urandom(24)
    app.run(debug=True)

