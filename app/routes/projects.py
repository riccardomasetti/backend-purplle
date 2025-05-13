import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.models.models import *
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


# -----------------------------------------------
# 4. CREATION OF A NEW LEARNING SESSION FOR A PROJECT
# -----------------------------------------------
@bp.route('/<project_id>/sessions', methods=['POST'])
def create_learning_session(project_id):
    try:
        data = request.get_json()
        project = Project.query.get_or_404(project_id)

        # Verifica che i campi obbligatori siano presenti
        if not data.get('durationMinutes'):
            return jsonify({'error': 'Duration in minutes is required'}), 400

        # Crea la sessione di apprendimento
        new_session = LearningSession(
            id=data.get('id', str(uuid.uuid4())),
            project_id=project_id,
            duration_minutes=data['durationMinutes'],
            motivation=data.get('motivation'),
            learning_objective=data.get('learningObjective'),
            # Metriche (opzionali)
            awareness_level=data.get('metrics', {}).get('awarenessLevel'),
            confidence_level=data.get('metrics', {}).get('confidenceLevel'),
            energy_level=data.get('metrics', {}).get('energyLevel'),
            performance_level=data.get('metrics', {}).get('performanceLevel'),
            satisfaction_level=data.get('metrics', {}).get('satisfactionLevel')
        )

        db.session.add(new_session)
        db.session.commit()

        return jsonify(new_session.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 5. LINKING DOCUMENTS TO A LEARNING SESSION FOR A PROJECT
# -----------------------------------------------
@bp.route('/<project_id>/sessions/<session_id>/documents', methods=['POST'])
def add_documents_to_session(project_id, session_id):
    try:
        data = request.get_json()
        session = LearningSession.query.get_or_404(session_id)
        project = Project.query.get_or_404(project_id)

        # Verifica che la sessione appartenga al progetto corretto
        if session.project_id != project_id:
            return jsonify({'error': 'Session does not belong to this project'}), 404

        # Aggiungi documenti di risorsa
        if 'resourceDocumentIds' in data and isinstance(data['resourceDocumentIds'], list):
            for doc_id in data['resourceDocumentIds']:
                doc = Document.query.get(doc_id)
                if doc and doc.category == DocumentCategory.RESOURCE and doc not in session.resource_documents:
                    session.resource_documents.append(doc)

        # Aggiungi documenti di test
        if 'testDocumentIds' in data and isinstance(data['testDocumentIds'], list):
            for doc_id in data['testDocumentIds']:
                doc = Document.query.get(doc_id)
                if doc and doc.category == DocumentCategory.TEST and doc not in session.test_documents:
                    session.test_documents.append(doc)

        db.session.commit()

        return jsonify(session.to_dict()), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 6. ADDING A QUESTION TO A LEARNING SESSION
# -----------------------------------------------
@bp.route('/<project_id>/sessions/<session_id>/questions', methods=['POST'])
def add_question_to_session(project_id, session_id):
    try:
        data = request.get_json()
        session = LearningSession.query.get_or_404(session_id)
        project = Project.query.get_or_404(project_id)

        # Verifica che la sessione appartenga al progetto corretto
        if session.project_id != project_id:
            return jsonify({'error': 'Session does not belong to this project'}), 404

        # Verifica che i campi obbligatori siano presenti
        if not data.get('question') or not data.get('answer') or not data.get('testDocumentId'):
            return jsonify({'error': 'Question, answer and testDocumentId are required'}), 400

        # Verifica che il documento di test esista
        test_doc = Document.query.get(data['testDocumentId'])
        if not test_doc:
            return jsonify({'error': 'Invalid test document'}), 400

        # Crea la nuova domanda
        new_question = Question(
            id=data.get('id', str(uuid.uuid4())),
            session_id=session_id,
            question=data['question'],
            answer=data['answer'],
            correction=data.get('correction'),
            evaluation=data.get('evaluation'),
            test_document_id=data['testDocumentId']
        )

        # Aggiungi riferimenti ai documenti di risorsa se presenti
        if 'references' in data and isinstance(data['references'], list):
            for ref_data in data['references']:
                doc_id = ref_data.get('documentId')
                if not doc_id:
                    continue

                doc = Document.query.get(doc_id)
                if not doc:
                    continue

                ref = DocumentReference(
                    question_id=new_question.id,
                    document_id=doc_id,
                    line_number=ref_data.get('lineNumber'),
                    page_number=ref_data.get('pageNumber'),
                    char_offset=ref_data.get('charOffset'),
                    context_text=ref_data.get('contextText')
                )
                db.session.add(ref)

        db.session.add(new_question)
        db.session.commit()

        return jsonify(new_question.to_dict()), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


