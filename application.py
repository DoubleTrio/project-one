import os
import requests
from flask import Flask, session, render_template, request, flash, redirect, url_for, request, jsonify, abort
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/register", methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")
        password_two = request.form.get("password_two")

        # Checking if all input fields are filled and whether the passwords match
        if username == "" or password == "" or password_two == "":
            flash("Please fill in all of the sections")
            return redirect(url_for('register'))
        elif password != password_two:
            flash("Passwords do not match")
            return redirect(url_for('register'))
        else:

            # Checking if the username has already been created
            users = db.execute("SELECT username FROM users")
            for user in users:
                if user.username == username:
                    flash("Username already taken")
                    return redirect(url_for('register'))

            # Inserting the name and password into the database
            db.execute("INSERT INTO users (username, password) VALUES (:name, :password)", {"name": username, "password": password})
            db.commit()
            return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        usernameLogin = request.form.get("usernameLogin")
        passwordLogin = request.form.get("passwordLogin")

        # Selecting the username to compare passwords
        loginInfo = db.execute("SELECT * FROM users WHERE username = :username", {"username": usernameLogin}).fetchone()

        # Try and except used to catch AttributeError when username is not found
        try:
            
            # Password matches registered password and creates a session of the user logged in
            if loginInfo.password == passwordLogin:
                session["logged_in"] = True
                session["name"] = usernameLogin
                session["id"] = loginInfo.id
                return redirect(url_for("search"))
            
            # Correct username, wrong password
            else:
                flash("Invalid username or password")
                return redirect(url_for("login"))

        except AttributeError:
            flash("Invalid username or password")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")  

# Clearing the session to "logout" the user
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searchInput = request.form.get("searchInput")
        
        # Invalid when the user searches nothing
        if len(searchInput) == 0:
            flash("Invalid input")
            return redirect(url_for("search"))

        # Initializing bookList and selecting the isbn, titles, and author matching searchInput
        session["bookList"] = []
        session["bookList"] = db.execute(f"SELECT * FROM books WHERE title ILIKE '%{searchInput}%' OR isbn ILIKE '%{searchInput}%' OR author ILIKE '%{searchInput}%'").fetchall()

        # Occurs when searchInput does not produce a result
        if len(session["bookList"]) == 0:
            flash(f"Your search - {searchInput} - did not produce any results")
            return redirect(url_for("search"))
            
        return render_template("result.html", bookList=session["bookList"])
    else:
        return render_template("search.html")

@app.route("/search/<string:isbn>", methods=['GET', 'POST'])
def book(isbn):
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn": isbn}).fetchone()
    session["reviews"] = []
    if request.method == 'POST':
        rating = request.form.get("rating")
        review = request.form.get("review")
        check = db.execute("SELECT * FROM reviews WHERE username = :username AND isbn = :isbn", {"username": session["name"], "isbn": book.isbn}).fetchone()
        if check:
            flash("You have already rated this book!")
            redirect(url_for("book", isbn = book.isbn))
        elif rating == None or review == "":
            flash("Please submit both your review and your rating")
            redirect(url_for("book", isbn = book.isbn))
        else:
            db.execute("INSERT into reviews (isbn, username, review, rating) VALUES (:isbn, :username, :review, :rating)", {"isbn": book.isbn, "username": session["name"], "review": review, "rating": rating})
            db.commit()
        return redirect(url_for("book", isbn = book.isbn))
    else:

        # Getting the average rating and number of ratings from Goodreads
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "bz2Jp4NrQ0RVCcbwFWYw", "isbns": isbn})
        data = res.json()["books"][0]
        average_rating = data["average_rating"]
        work_ratings_count = data["work_ratings_count"]

        # Getting all the reviews
        reviewList = db.execute("SELECT * FROM reviews WHERE isbn = :isbn", {"isbn": book.isbn}).fetchall()
        for review in reviewList:
            session["reviews"].append(review)
        return render_template("book.html", book = book, average_rating = average_rating, work_ratings_count = work_ratings_count, reviewList=session["reviews"])

@app.route("/api/<string:isbn>")
def api(isbn):

    # Searching for the book based isbn and checking if the isbn can be found
    book = db.execute("SELECT * FROM books WHERE isbn = :isbn", {"isbn":isbn}).fetchone()
    if not book:
        return render_template("404.html")

    # Gathering the average_rating and work_ratings_count from Goodreads, similar code to the book search but instead used to make a API    
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": "bz2Jp4NrQ0RVCcbwFWYw", "isbns": isbn})
    data = res.json()["books"][0]
    average_rating = data["average_rating"]
    work_ratings_count = data["work_ratings_count"]

    # Creating the API
    api = jsonify({
        "title":book.title,
        "author": book.author,
        "year": book.year,
        "isbn": book.isbn,
        "review_count": work_ratings_count,
        "average_score": average_rating
    })

    return api


