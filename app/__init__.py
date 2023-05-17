from flask import Flask
import app.database as Data
from app.app import api_bp

app = Flask(__name__)

app.config.from_pyfile('config.py')

with app.app_context():
    Data.db.init_app(app)
    Data.db.create_all()


app.register_blueprint(api_bp)
