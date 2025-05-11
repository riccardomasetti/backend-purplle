from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from flask_migrate import Migrate
import os

db = SQLAlchemy()
cors = CORS()
migrate = Migrate()

def create_app():
    load_dotenv()

    app = Flask(__name__)

    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URI')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['UPLOAD_FOLDER'] = os.getenv('UPLOAD_FOLDER')
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH'))

    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    cors.init_app(app)

    from app.models import models

    migrate.init_app(app, db)

    from app.routes.projects import bp as projects_bp
    app.register_blueprint(projects_bp)

    @app.route('/')
    def index():
        return {
            'message': 'Purplle API',
            'status': 'running'
        }

    return app
