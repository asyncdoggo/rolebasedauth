import re
import uuid

from flask import session, Blueprint, request, jsonify, make_response
from flask_jwt_extended import create_access_token, JWTManager, set_access_cookies, get_jwt, unset_access_cookies
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required

import app.database as db

api_bp = Blueprint('api', __name__)

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
password_regex = r"^(?=.*[A-Za-z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!%*#?&]{13,}$"
jwt = JWTManager()


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
                session["id"] = uuid.uuid4().hex
                db.store_session(session["id"], user.id)
                return make_response(jsonify({'message': 'success'}), 200)
            elif user == 0:
                return make_response(jsonify({'message': 'username not found'}))
            else:
                return make_response(jsonify({'message': 'incorrect password'}))
        except Exception as e:
            print(e)


@api_bp.route("/api/user/login", methods=["POST"])
def user_login():
    if request.method == "POST":
        try:
            auth = request.authorization
            if not auth or not auth.username or not auth.password:
                return make_response(jsonify({'message': 'username or password not present'}))

            user = db.check_auth(auth.username, auth.password)
            if user:
                access_token = create_access_token(identity=user.id)
                resp = make_response(jsonify({'message': 'success'}), 200)
                set_access_cookies(resp, access_token, max_age=1800)  # 30 mins
                db.store_session(access_token, user.id)
                return resp
            elif user == 0:
                return make_response(jsonify({'message': 'username not found'}))
            else:
                return make_response(jsonify({'message': 'incorrect password'}))
        except Exception as e:
            print(e)


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
    return register(role="user")


@api_bp.route("/api/messages/<msg_id>", methods=["GET", "POST"])
@api_bp.route("/api/messages", methods=["GET", "POST"])
@jwt_required(optional=True, locations=["cookies"])
def message(msg_id=None):
    if "user" in session:
        uid = session["user"]
        sid = session["id"]

    else:
        # claims = get_jwt()
        uid = get_jwt_identity()
        sid = request.cookies.get("access_token_cookie")

    if not db.check_session(sid, uid):
        return make_response(jsonify({"message": "user not authenticated"}), 403)

    if request.method == "GET":
        msg = db.get_message(uid, msg_id)
        return make_response(jsonify(msg), 200)

    if request.method == "POST":
        try:
            data = request.get_json()

            if db.create_message(uid, data["message"]):
                return make_response(jsonify({"message": 'success'}), 201)
            return make_response(jsonify({"message": "failure"}), 500)
        except Exception as e:
            print(e)
            return make_response(jsonify({'message': repr(e)}))
