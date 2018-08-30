import os

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
import pandas as pd 

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


@app.route("/", methods=["GET", "POST"])
def index():
	if request.method == "POST":
		#authenticate user
		user = request.form.get("username")
		password = request.form.get("password")
		##

		## if user authenticates, log them in
		session['username'] = request.form.get("username")
		return render_template("index.html", name=user, session=session)

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
		qry = "select * from books where lower(author) like '%%{}%%'".format(author)
		results = pd.read_sql(qry, engine)

	return render_template("results.html", results = results)

@app.route("/logout/")
def logout():
	session.pop('username', None)
	return redirect(url_for('index'))

