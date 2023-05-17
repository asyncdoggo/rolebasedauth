import datetime
import os
from flask_sqlalchemy import SQLAlchemy
from argon2 import PasswordHasher

db = SQLAlchemy()

ph = PasswordHasher()


class Users(db.Model):
    __tablename__ = "users"
    id = db.Column(db.String(35), primary_key=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(35), nullable=False)


def insert_user(user_id, username, email, password, role):
    try:
        hashed = ph.hash(password)
        user: Users = Users(username=username, id=user_id, password=hashed, role=role)
        db.session.add(user)
        db.session.commit()
        return True
    except Exception as e:
        print(e)


def check_auth(username, password):
    try:
        user = Users.query.filter_by(username=username).one()
        if not user:
            return 0
        hashed = user.password
        ph.verify(hashed, password)
        return user
    except Exception as e:
        print(e)
