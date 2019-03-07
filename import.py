import csv
import os


from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    # db.execute("CREATE TABLE books (isbn VARCHAR PRIMARY KEY, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year NOT NULL)")
    # db.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, username VARCHAR NOT NULL, password VARCHAR NOT NULL)")
    db.execute("CREATE TABLE reviews (isbn VARCHAR NOT NULL, username VARCHAR NOT NULL, review VARCHAR NOT NULL, rating VARCHAR NOT NULL)")
    # f = open("books.csv")
    # reader = csv.reader(f)
    # # Formatted strings seem to not work because some titles have '
    # for isbn, title, author, year in reader:
    #     db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
    #               {"isbn": isbn, "title": title, "author": author, "year": year})
    
    db.commit()
    # print("Success, after many tests. Thanks to a friend who allowed me to check why SQL wasn't working on my laptop by sending me his working db.execute command only to find that my laptop blocked SQL. I fixed up the db.execute commands at the end for how I would have styled it")

if __name__ == "__main__":
    main()
