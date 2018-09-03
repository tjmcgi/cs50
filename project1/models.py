import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    author = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    isbn = db.Column(db.String, nullable=False)
    year_published = db.Column(db.Integer, nullable=False)
    reviews = db.relationship("Review", backref="reviews", lazy=True)



class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey("books.id"), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    review = db.Column(db.String, nullable=False)

    def add_review(self, review):
        r = Review(book_id = self.book_id, user_ud=self.user_id, review=review)
        db.session.add(r)
        db.session.commit()

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    firstname = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)

    def add_user(username, password, firstname):
        u = User(username=username, password=password, firstname=firstname)
        db.session.add(u)
        db.session.commit()
