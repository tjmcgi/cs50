import os

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine, and_, or_
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd
import requests
from models import *

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)



# goodreads api_key
key = 'jS0w2iLDkRPC5zph3W4TA'
goodreads_url = "https://www.goodreads.com/book/review_counts.json"


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        #authenticate user
        user = request.form.get("username")
        password = request.form.get("password")
        ##
        try:
            result = User.query.filter(and_(User.username==user, User.password==password)).first()
            user_id = result.id
            first_name = result.firstname
            message = "Hi {}, you are logged in now!".format(first_name)
        except:
            return render_template("error.html", message="Login Failed.")
        ## if user authenticates, log them in
        session['user_id'] = user_id
        session['first_name'] = first_name
        session['logged_in'] = True
        return render_template("index.html", user_id=user_id, session=session, message=message)
        ## if user fails to authenticate, send back to log-in screen with failure message
    if session.get('logged_in'):
        return render_template("index.html", user_id=session['user_id'], session=session)
    else:
        return render_template("login.html")

@app.route("/login/")
def login():
	return render_template("login.html")

@app.route("/signup/", methods=["GET", "POST"])
def signup():
  if request.method=="POST":
    username = request.form.get("username")
    firstname = request.form.get("firstname")
    password = request.form.get("password")
    confirm_password = request.form.get("confirm_password")
    if password != confirm_password:
      return render_template("error.html", message = "Passwords do not match.")
    User.add_user(username=username, password=password, firstname=firstname)
    user = User.query.filter(and_(User.username==username, User.password==password)).first()
    session['user_id'] = user.id 
    message = "Hi {}, you are logged in now!".format(user.firstname)
    session['first_name'] = user.firstname 
    return render_template("index.html", session=session, message=message)
  return render_template("signup.html")

@app.route("/results/", methods=["GET", "POST"])
def results():
	if request.method=='POST':
		isbn = request.form.get("isbn")
		author = request.form.get("author")
		title = request.form.get("title")
		qry = "select * from books where lower(author) like '%%{}%%' and lower(isbn) like '%%{}%%' and lower(title) like '%%{}%%'".format(author.lower(), isbn, title.lower())
		results = db.execute(qry).fetchall()

	return render_template("results.html", results = results, session=session)

@app.route("/logout/")
def logout():
	session.clear()
	return redirect(url_for('index'))

@app.route("/book/<isbn>")
def book_detail(isbn):
	book_qry="select * from books where isbn = '{}'".format(isbn)
	review_qry="select * from reviews where isbn= '{}'".format(isbn)
	goodreads_data = requests.get(goodreads_url, params={"key": key, "isbns": isbn})
	goodreads_data = goodreads_data.json()
	goodreads_avg_rating = goodreads_data['books'][0]['average_rating']
	goodreads_ratings = goodreads_data['books'][0]['work_ratings_count']
	user_review = db.execute("select * from reviews where isbn = :isbn and user_id = :user_id", {"isbn": isbn, "user_id": session['user_id']}).fetchone()
	user_has_reviewed = len(db.execute("select * from reviews where isbn = :isbn and user_id = :user_id", {"isbn": isbn, "user_id": session['user_id']}).fetchall())
	result = db.execute(book_qry).fetchone()
	reviews = db.execute(review_qry).fetchall()
	session['isbn'] = isbn
	return render_template("book_detail.html", isbn=isbn, result=result, goodreads_avg_rating = goodreads_avg_rating, goodreads_ratings=goodreads_ratings, reviews=reviews, session=session, user_review=user_review, user_has_reviewed=user_has_reviewed)

@app.route("/review", methods=["POST"])
def review():
	if request.method=="POST":
		review = request.form.get("review")
		user_id = session["user_id"]
		isbn = session["isbn"]
		db.execute("insert into reviews (user_id, isbn, review) values (:user_id, :isbn, :review)", {"user_id": user_id, "isbn": isbn, "review": review})
		db.commit()
		return render_template('index.html', message = "Review submitted successfully!")
