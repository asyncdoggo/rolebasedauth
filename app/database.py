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


class Message(db.Model):
    __tablename__ = "data"
    id = db.Column(db.Integer, primary_key=True)
    message = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.String(35), db.ForeignKey("users.id", ondelete="CASCADE"))


def insert_user(user_id, username, email, password, role):
    try:
        hashed = ph.hash(password)
        user: Users = Users(username=username, id=user_id, password=hashed, role=role, email=email)
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


def create_message(usr, d):
    try:
        data = Message(message=d, user_id=usr)
        db.session.add(data)
        db.session.commit()
        return True
    except Exception as e:
        print(e)


def get_message(uid, message_id=None):
    user = Users.query.filter_by(id=uid).one_or_none()
    msg = []
    if message_id and user.role == "admin":
        msg = Message.query.filter_by(id=message_id).one_or_none()
        if msg:
            msg = {
                "id": msg.id,
                "message": msg.message,
                "user": msg.user_id
            }
    elif message_id and user.role == "user":
        msg = Message.query.filter_by(id=message_id, user_id=uid).one_or_none()
        if msg:
            msg = {
                "id": msg.id,
                "message": msg.message,
                "user": msg.user_id
            }
    elif not message_id and user.role == "admin":
        data = Message.query.all()
        if data:
            for i in data:
                msg.append(
                    {
                        "id": i.id,
                        "message": i.message,
                        "user": i.user_id
                    }
                )
    elif not message_id and user.role == "user":
        data = Message.query.filter_by(user_id=uid).all()
        if data:
            for i in data:
                msg.append(
                    {
                        "id": i.id,
                        "message": i.message,
                        "user": i.user_id
                    }
                )

    return msg


def get_user(uid):
    return Users.query.filter_by(id=uid).one_or_none()
