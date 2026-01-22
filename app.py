# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from pathlib import Path


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///soundboard.db'
app.config['JWT_SECRET_KEY'] = 'jwhe98349gefisdagfjfgw944g38gfw'  
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
jwt = JWTManager(app)

SOUNDS_DIR = Path("sounds")
SOUNDS_DIR.mkdir(exist_ok=True)


