from datetime import timedelta
import flask
from flask import Flask
import app.database as database
from app.app import api_bp, jwt

app = Flask(__name__)

app.config.from_pyfile('config.py')

with app.app_context():
    database.db.init_app(app)
    database.db.create_all()
    jwt.init_app(app)

app.register_blueprint(api_bp)


@app.before_request
def make__session_permanent():
    flask.session.permanent = True
    app.permanent_session_lifetime = timedelta(minutes=30)
