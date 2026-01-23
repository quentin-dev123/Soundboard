# app.py
import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from pathlib import Path


app = Flask(__name__)

# Configure database path
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'instance', 'soundboard.db')
app.config['SECRET_KEY'] = 'jwhe98349gefisdagfjfgw944g38gfw'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Create instance folder if it doesn't exist
instance_path = os.path.join(basedir, 'instance')
os.makedirs(instance_path, exist_ok=True)

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

SOUNDS_DIR = Path("sounds")
SOUNDS_DIR.mkdir(exist_ok=True)

# Import routes after app initialization
import routes


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
