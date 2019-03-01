import os
from flask import Flask, session, render_template, request, flash, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
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

@app.route("/register")
def registerPage():
    return render_template("register.html")

@app.route("/login")
def loginPage():
    return render_template("login.html")

@app.route("/hello", methods=["POST"])
def hello():
    name = request.form.get("name")
    password = request.form.get("password")
    if name == "" or password == "":
        flash("Please fill in your username and password")
        return redirect(url_for('registerPage'))
    else:
        flash("Your account was created! You can login now!")
        return render_template("hello.html", name=name, password=password)
