import re
import uuid
import flask
from flask import Flask, session, Blueprint, request, jsonify, make_response
import app.database as db

api_bp = Blueprint('api', __name__)

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{13,}$"


@api_bp.route("/api/admin/login", methods=["POST"])
def admin_login():
    if request.method == "POST":
        try:
            auth = request.authorization
            if not auth or not auth.username or not auth.password:
                return make_response(jsonify({'message': 'username or password not present'}))

            user = db.check_auth(auth.username, auth.password)
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
    # TODO: IMPLEMENT TOKEN AUTH FOR USER


@api_bp.route("/api/admin/register", methods=["POST"])
def register(role="admin"):
    if request.method == "POST":
        try:
            data = request.get_json()
            email = data['email']
            username = data['username']
            password = data['password']
            if not re.search(email_regex, email):
                return jsonify({'message': 'invalid email format'})

            if len(username) < 6 or " " in username:
                return make_response(
                    jsonify({'message': 'username should be greater than 6 characters without spaces'}), 500)

            if not re.search(password_regex, password):
                return make_response(jsonify({'message': 'password should be more than 13 characters with at least a '
                                                         'number and a special character'}), 500)

            user_id = uuid.uuid4().hex

            if db.insert_user(user_id, username, email, password, role):
                return make_response(jsonify({'message': 'success'}), 201)
            else:
                return make_response(jsonify({'message': 'user or email already registered'}), 500)

        except Exception as _:
            return make_response(jsonify({'message': 'incomplete or missing data'}), 404)


@api_bp.route("/api/user/register", methods=["POST"])
def user_register():
    register(role="user")


@api_bp.route("/api/messages/<msg_id>", methods=["GET", "POST"])
@api_bp.route("/api/messages", methods=["GET", "POST"])
def message(msg_id=None):
    if "user" in session:
        uid = session["user"]

    else:
        uid = ""
        # TODO: check user token return error if neither are present

    if request.method == "GET":
        msg = db.get_message(uid, msg_id)
        return make_response(jsonify(msg), 200)

    if request.method == "POST":
        try:
            data = request.get_json()

            if "user" in session:
                uid = session["user"]
                if db.create_message(uid, data["message"]):
                    return make_response(jsonify({"message": 'success'}), 201)
                return make_response(jsonify({"message": "failure"}), 500)
            return make_response(jsonify({"message": "user not authenticated"}), 403)
        except Exception as e:
            print(e)
            return make_response(jsonify({'message': repr(e)}))
