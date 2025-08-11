from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_login import UserMixin



db = SQLAlchemy()

class Users(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(70), nullable=False)
    email = db.Column(db.String(70), nullable=False, unique = True)
    password = db.Column(db.String(50), nullable=False)

    def __init__(self, username, email, password):
        self.username = username
        self.email = email
        self.password = password


class Books(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(70), nullable=False)
    isbn = db.Column(db.String(70), nullable=False)
    author = db.Column(db.String(70), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    image_url = db.Column(db.String(90), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    count = db.Column(db.Integer, nullable=False)
    available_count = db.Column(db.Integer, nullable=False)
    rented_count = db.Column(db.Integer, nullable=False)

    def __init__(self, name, isbn, category,author, image_url, description, count, available_count, rented_count):

        self.name = name
        self.isbn = isbn
        self.category = category
        self.author = author
        self.image_url = image_url
        self.description = description
        self.count = count
        self.available_count = available_count
        self.rented_count = rented_count


class BooksRented(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    book = db.relationship('Books', backref = "books_rented")
    user = db.relationship('Users', backref = "books_rented")
    status = db.Column(db.String(30), default = "Pending")

    def __init__(self, book_id, user_id, created_at=None):

        self.book_id = book_id
        self.user_id = user_id
        self.created_at = created_at or datetime.utcnow()
