import os
from flask import Flask, session, render_template, request, flash, redirect, url_for, request
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from werkzeug.security import generate_password_hash, check_password_hash
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-v-user-logins - Resource
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
            flash("Please fill in all sections")
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

            password = generate_password_hash(password)
            db.execute("INSERT INTO users (username, password) VALUES (:name, :password)",
                    {"name": username, "password": password})
            db.commit()
            flash(f"Success! Your account was created! Your username is {username} and your password is {password}")
            return redirect(url_for("login"))
    else:
        return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'POST':
        usernameLogin = request.form.get("usernameLogin")
        passwordLogin = request.form.get("passwordLogin")
        loginInfo = db.execute("SELECT * FROM users WHERE username = :username", {"username": usernameLogin}).fetchone()

        # Try and except used to catch AttributeError when username is not found
        try:
            if session["logged_in"]: 
                flash("You are already logged in. Logout first")
                return redirect(url_for("login"))
            elif loginInfo.password == passwordLogin:
                session["logged_in"] = True
                session["name"] = usernameLogin
                flash("Success")
                return redirect(url_for("search"))
            else:
                flash("Invalid username or password")
                return redirect(url_for("login"))
        except AttributeError:
            flash("Invalid username or password")
            return redirect(url_for("login"))
    else:
        return render_template("login.html")  

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/search", methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        searchInput = request.form.get("searchInput")
        session["bookList"] = []
        if len(searchInput) == 0:
            flash("Invalid input")
            return redirect(url_for("search"))

        session["bookList"] = db.execute(f"SELECT * FROM books WHERE title ILIKE '%{searchInput}%' OR isbn ILIKE '%{searchInput}%' OR author ILIKE '%{searchInput}%'").fetchall()

        if len(session["bookList"]) == 0:
            flash(f"Your search - {searchInput} - did not produce any results")
            return redirect(url_for("search"))
            
        return render_template("result.html", bookList=session["bookList"])
    else:
        return render_template("search.html")

@app.route("/book", methods=['GET', 'POST'])
def book():
    if request.method == 'POST':
        return True
    else:
        return render_template("book.html")