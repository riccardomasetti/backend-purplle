from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


def create_app():

    app = Flask(__name__)

    @app.route('/')
    def index():
        return {
            'message': 'Learning Gym API',
            'status': 'running'
        }

    return app