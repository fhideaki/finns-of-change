# Imports 
from flask import Flask
from app.api.routes import api

app = Flask(__name__)
app.config['SECRET_KEY'] = "\x11\xa6\x01\xa2\xaag\xfeu\xb9i\xbb`\xe4'P\x07\xcb\x9a6L\xae\x0f\xd0\x9f\xae_o\x008'[\x9d\xe8"
app.register_blueprint(api)