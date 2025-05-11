import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.models.models import Project, Milestone, Document
from app import db
from datetime import datetime
import uuid
from sqlalchemy.exc import IntegrityError

bp = Blueprint('projects', __name__, url_prefix='/api/projects')


# -----------------------------------------------
# 1. PROJECT CREATION
# -----------------------------------------------
@bp.route('/', methods=['POST'])
def create_project():
    try:
        data = request.get_json()

        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400

        new_project = Project(
            id=data.get('id', str(uuid.uuid4())),
            title=data['title'],
            motivations=data.get('motivations', []),
            overall_performance=data.get('overall_performance'),
            difficulty=data.get('difficulty'),
            interest=data.get('interest')
        )

        db.session.add(new_project)
        db.session.commit()

        return jsonify(new_project.to_dict()), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 2. DOCUMENT ADDITION TO PROJECT
# -----------------------------------------------
@bp.route('/<project_id>/documents', methods=['POST'])
def add_document(project_id):
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400

        file = request.files['file']
        project = Project.query.get_or_404(project_id)

        # Salva il file (esempio semplice)
        filename = secure_filename(file.filename)
        os.makedirs(f"uploads/{project_id}", exist_ok=True)
        filepath = os.path.join(f"uploads/{project_id}", filename)
        file.save(filepath)

        new_doc = Document(
            project_id=project_id,
            filename=filename,
            file_path=filepath,
            category=request.form.get('category', 'RESOURCE')
        )

        db.session.add(new_doc)
        db.session.commit()

        return jsonify(new_doc.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500





