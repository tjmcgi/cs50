import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd
import requests 

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
			result = db.execute("SELECT * from users where username = :user and password = :password", {"user": user, "password":password}).fetchone()
			user_id = result['id']
		except:
			return render_template("error.html", message="Login Failed.")

		## if user authenticates, log them in
		session['user_id'] = user_id	
		return render_template("index.html", user_id=user_id, session=session)

		## if user fails to authenticate, send back to log-in screen with failure message
		
	else:
		return render_template("login.html")

@app.route("/login/")
def login():
	return render_template("login.html")

@app.route("/signup/")
def signup():
	return render_template("signup.html")

@app.route("/results/", methods=["GET", "POST"])
def results():
	if request.method=='POST':
		isbn = request.form.get("isbn")
		author = request.form.get("author")
		title = request.form.get("title")
		qry = "select * from books where lower(author) like '%%{}%%' and lower(isbn) like '%%{}%%' and lower(title) like '%%{}%%'".format(author, isbn, title)
		results = db.execute(qry).fetchall()

	return render_template("results.html", results = results, session=session)

@app.route("/logout/")
def logout():
	session.pop('username', None)
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
		return render_template("success.html", message="Successfully submitted review")


