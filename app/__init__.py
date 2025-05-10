from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
import os


def create_app():
    load_dotenv()
    app = Flask(__name__)

    @app.route('/')
    def index():
        return {
            'message': 'Learning Gym API',
            'status': 'running'
        }

    return app