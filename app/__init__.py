# Imports 
from flask import Flask
from app.api.routes import api

app = Flask(__name__)
app.register_blueprint(api)