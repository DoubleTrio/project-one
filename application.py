import os

from flask import Flask, session, render_template, request
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
    return "Project 1: TODO"

@app.route("/register")

@app.route("/login")

@app.route("/books/<str>")
# @app.route("/<string:word>")
# def testing(word):
#     return f"<h1>hello, {word}!</h1>"
#
# @app.route("/testing")
# def testing():
#     var = "testing for works"
#     return render_template("index.html", var=var)
#
# @app.route("/condition")
# def condition():
#     condition = False
#     return render_template("index.html", condition=condition)
#
# @app.route("/loops")
# def loops():
#     names = ['Charlie', 'Bob', 'Joe']
#     return render_template("index.html", names=names)
#
# @app.route("/links")
# def link():
#     return render_template("more.html")
#
# @app.route("/forms", methods=['POST'])
# def form():
#     input = request.form.get("input")
#     return render_template("index.html", input=input)
