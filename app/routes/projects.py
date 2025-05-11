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


# -----------------------------------------------
# 3. MILESTONE ADDITION TO PROJECT
# -----------------------------------------------
@bp.route('/<project_id>/milestones', methods=['POST'])
def add_milestone(project_id):
    try:
        data = request.get_json()
        project = Project.query.get_or_404(project_id)

        if not data.get('title'):
            return jsonify({'error': 'Title is required'}), 400

        if not data.get('date'):
            return jsonify({'error': 'Date is required'}), 400

        # Controlla se la nuova milestone è una deadline
        is_deadline = data.get('isDeadline', False)

        # Se è una deadline, disattiva qualsiasi deadline esistente
        if is_deadline:
            Milestone.query.filter_by(project_id=project_id, is_deadline=True).update({'is_deadline': False})

        new_milestone = Milestone(
            title=data['title'],
            due_date=datetime.fromisoformat(data['date']),
            is_deadline=is_deadline,
            project_id=project_id
        )

        db.session.add(new_milestone)
        db.session.commit()

        return jsonify(new_milestone.to_dict()), 201

    except ValueError:
        return jsonify({'error': 'Invalid date format (use ISO 8601)'}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500



