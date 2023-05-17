import re
import uuid
import flask
from flask import Flask, session, Blueprint, request, jsonify, make_response
import app.database as database

api_bp = Blueprint('api', __name__)

api_bp.secret_key = ""

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{13,}$"


@api_bp.route("/api/admin/login")
def admin_login():
    if request.method == "POST":
        try:
            auth = request.authorization
            if not auth or not auth.username or not auth.password:
                return make_response(jsonify({'message': 'username or password not present'}))

            user = database.check_auth(auth.username, auth.password)
            if user:
                session["user"] = user.id
                return make_response(jsonify({'message': 'success'}), 200)
            elif user == 0:
                return make_response(jsonify({'message': 'username not found'}))
            else:
                return make_response(jsonify({'message': 'incorrect password'}))
        except Exception as e:
            print(e)


@api_bp.route("/api/user/login")
def user_login():
    pass


@api_bp.route("/api/admin/register")
def register(role="admin"):
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data['email']
            username = data['username']
            password = data['password']
            if not re.search(email_regex, email):
                return jsonify({'message': 'invalid email format'})

            if len(username) < 10 or " " in username:
                return make_response(
                    jsonify({'message': 'username should be greater than 10 characters without spaces'}), 500)

            if not re.search(password_regex, password):
                return make_response(jsonify({'message': 'password '}), 500)

            user_id = uuid.uuid4().hex

            if database.insert_user(user_id, username, email, password, role):
                return make_response({jsonify({'message': 'success'})}, 200)

        except Exception as _:
            return make_response(jsonify({'message': 'incomplete or missing data'}), 404)


@api_bp.route("/api/user/register")
def user_register():
    register(role="user")
