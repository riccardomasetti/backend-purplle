import os
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from app.models.models import *
from app import db
from datetime import datetime
import uuid
from flask import send_file
from sqlalchemy.exc import IntegrityError

bp = Blueprint('projects', __name__, url_prefix='/api/projects')


##########################
#      POST METHODS      #
##########################

# -----------------------------------------------
# 1. PROJECT CREATION
# -----------------------------------------------
@bp.route('/', methods=['POST'])
def create_project():
    try:
        data = request.get_json()

        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        new_project = Project(
            id=data.get('id', str(uuid.uuid4())),
            name=data['name'],
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

        custom_id = request.form.get('id')

        filename = secure_filename(file.filename)
        os.makedirs(f"uploads/{project_id}", exist_ok=True)
        filepath = os.path.join(f"uploads/{project_id}", filename)
        file.save(filepath)

        new_doc = Document(
            id=custom_id or str(uuid.uuid4()),  # Use custom ID if provided
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

        if not data.get('name'):
            return jsonify({'error': 'Name is required'}), 400

        if not data.get('date'):
            return jsonify({'error': 'Date is required'}), 400

        # Controlla se la nuova milestone è una deadline
        is_deadline = data.get('isDeadline', False)

        # Se è una deadline, disattiva qualsiasi deadline esistente
        if is_deadline:
            Milestone.query.filter_by(project_id=project_id, is_deadline=True).update({'is_deadline': False})

        new_milestone = Milestone(
            name=data['name'],
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

        if session.project_id != project_id:
            return jsonify({'error': 'Session does not belong to this project'}), 404

        if 'resourceDocumentIds' in data and isinstance(data['resourceDocumentIds'], list):
            for doc_id in data['resourceDocumentIds']:
                doc = Document.query.get(doc_id)
                if doc and doc.category == DocumentCategory.RESOURCE and doc not in session.resource_documents:
                    session.resource_documents.append(doc)

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


# --------------------------------------------------
# 7. TODO: ENDPOINT FOR TRIGGER QUESTIONS CREATIONS
#          BY THE LLM
# --------------------------------------------------







##########################
#      GETS METHODS      #
##########################

# -----------------------------------------------
# 7. GETTTING ALL THE PROJECTS
# -----------------------------------------------
@bp.route('/', methods=['GET'])
def get_all_projects():
    try:
        projects = Project.query.all()
        return jsonify([project.to_dict() for project in projects]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 8. GETTING THE PROJECT WITH A CERTAIN ID
# -----------------------------------------------
@bp.route('/<project_id>', methods=['GET'])
def get_project(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify(project.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# --------------------------------------------------
# 9. GETTING ALL THE DOCUMENTS OF A CERTAIN PROJECT
# --------------------------------------------------
@bp.route('/<project_id>/documents', methods=['GET'])
def get_project_documents(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        documents = Document.query.filter_by(project_id=project_id).all()
        return jsonify([doc.to_dict() for doc in documents]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 10. GETTING THE DOCUMENT OF A CERTAIN INDEX
# -----------------------------------------------
@bp.route('/<project_id>/documents/<document_id>', methods=['GET'])
def get_document(project_id, document_id):
    try:
        document = Document.query.get_or_404(document_id)

        if document.project_id != project_id:
            return jsonify({'error': 'Document does not belong to this project'}), 404

        return jsonify(document.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 11. DOWNLOAD THE FIE WITH THE SELECTED ID
# -----------------------------------------------
# call it with:curl -X GET "http://localhost:5000/api/projects/{project_id}/documents/{document_id}/download" -J -O
@bp.route('/<project_id>/documents/<document_id>/download', methods=['GET'])
def download_document(project_id, document_id):
    try:
        from flask import send_file
        import os

        document = Document.query.get_or_404(document_id)

        if document.project_id != project_id:
            return jsonify({'error': 'Document does not belong to this project'}), 404

        # Check if the path is absolute or relative
        if os.path.isabs(document.file_path):
            file_path = document.file_path
        else:
            # If it's a relative path, make it relative to the application root
            file_path = os.path.join(os.getcwd(), document.file_path)

        # Verify the file exists
        if not os.path.exists(file_path):
            return jsonify({'error': f'File not found: {file_path}'}), 404

        return send_file(file_path, download_name=document.filename)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# 12. GETTING ALL THE MILESTONES OF A CERTAIN PROJECT
# ---------------------------------------------------
@bp.route('/<project_id>/milestones', methods=['GET'])
def get_project_milestones(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        milestones = Milestone.query.filter_by(project_id=project_id).all()
        return jsonify([milestone.to_dict() for milestone in milestones]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# -----------------------------------------------
# 13. GETTING THE MILESTONE WITH A CERTAIN ID
# -----------------------------------------------
@bp.route('/<project_id>/milestones/<milestone_id>', methods=['GET'])
def get_milestone(project_id, milestone_id):
    try:
        milestone = Milestone.query.get_or_404(milestone_id)

        if milestone.project_id != project_id:
            return jsonify({'error': 'Milestone does not belong to this project'}), 404

        return jsonify(milestone.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# 14. GETTING ALL THE MILESTONES OF A CERTAIN PROJECT
# ---------------------------------------------------
@bp.route('/<project_id>/sessions', methods=['GET'])
def get_project_sessions(project_id):
    try:
        project = Project.query.get_or_404(project_id)
        sessions = LearningSession.query.filter_by(project_id=project_id).all()
        return jsonify([session.to_dict() for session in sessions]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# 15. GETTING THE SESSION WITH A CERTAIN ID
# ---------------------------------------------------
@bp.route('/<project_id>/sessions/<session_id>', methods=['GET'])
def get_session(project_id, session_id):
    try:
        session = LearningSession.query.get_or_404(session_id)

        if session.project_id != project_id:
            return jsonify({'error': 'Session does not belong to this project'}), 404

        return jsonify(session.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# 16. GET ALL THE TASK OF A CERTAIN PROJECT
# ---------------------------------------------------
@bp.route('/<project_id>/tasks', methods=['GET'])
def get_project_tasks(project_id):
    """Get all tasks for a specific project"""
    try:
        project = Project.query.get_or_404(project_id)
        return jsonify([task.to_dict() for task in project.tasks]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ---------------------------------------------------
# 17. CREATE A NEW TASK FOR A CERTAIN PROJECT
# ---------------------------------------------------
@bp.route('/<project_id>/tasks', methods=['POST'])
def create_project_task(project_id):
    """Create a new task for a specific project"""
    try:
        # Verify project exists
        project = Project.query.get_or_404(project_id)

        data = request.json
        if not data or 'name' not in data:
            return jsonify({'error': 'Task name is required'}), 400

        new_task = Task(
            name=data['name'],
            project_id=project_id,
            milestone_id=data.get('milestone_id')  # Optional milestone connection
        )

        db.session.add(new_task)
        db.session.commit()

        return jsonify(new_task.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


# ---------------------------------------------------
# 18. GET A SPECIFIC TASK FOR A CERTAIN PROJECT
# ---------------------------------------------------
@bp.route('/<project_id>/tasks/<task_id>', methods=['GET'])
def get_task(project_id, task_id):
    """Get a specific task by ID"""
    try:
        task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
        return jsonify(task.to_dict()), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 404

# --------------------------------------------------
# TODO: ENDPOINT FOR GETTING QUESTIONS
# --------------------------------------------------

# --------------------------------------------------
# TODO: MANAGEMENT OF DOCUMENT REFERENCE
# --------------------------------------------------


# -----------------------------------------------------------------
# 18. ENDPOINT FOR TRIGGER RESOURCE QUESTIONS CREATIONS BY THE LLM
# -----------------------------------------------------------------
@bp.route('/<project_id>/sessions/<session_id>/generate-questions', methods=['POST'])
def generate_questions(project_id, session_id):
    """Generate questions for a learning session based on resource documents"""
    try:
        session = LearningSession.query.get_or_404(session_id)
        if session.project_id != project_id:
            return jsonify({'error': 'Session does not belong to this project'}), 404

        resource_documents = session.resource_documents

        if not resource_documents:
            return jsonify({'error': 'No resource documents found for this session'}), 400

        from app.utils.ai_services import generate_question_from_document

        generated_questions = []

        for document in resource_documents:

            question_text, answer_text = generate_question_from_document(document.file_path)

            if question_text.startswith("Error") or question_text.startswith("Could not"):
                continue

            new_question = Question(
                session_id=session_id,
                question=question_text,
                answer=answer_text,
                #test_document_id=document.id, it is not needed, there is a ManyToMany relation between question and document
                source_type=QuestionSourceType.RESOURCE
            )


            new_question.resource_documents.append(document)
            db.session.add(new_question)
            generated_questions.append(new_question)

        db.session.commit()

        return jsonify({
            'message': f'Generated {len(generated_questions)} questions',
            'questions': [q.to_dict() for q in generated_questions]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500


# -------------------------------------------------------------
# 19. ENDPOINT FOR TRIGGER TEST QUESTIONS CREATIONS BY THE LLM
# -------------------------------------------------------------
@bp.route('/<project_id>/sessions/<session_id>/extract-test-questions', methods=['POST'])
def extract_test_questions(project_id, session_id):
    """
    Extract questions from TEST documents associated with a learning session.
    The questions are extracted as they appear in the text without modification.
    """
    try:
        session = LearningSession.query.get(session_id)
        if not session or session.project_id != project_id:
            return jsonify({'error': 'Session not found or does not belong to the project'}), 404

        test_documents = session.test_documents
        if not test_documents:
            return jsonify({'error': 'No TEST documents associated with this session'}), 400

        created_questions = []
        for doc in test_documents:
            if doc.category != DocumentCategory.TEST:
                continue

            from app.utils.ai_services import extract_questions_from_test
            question_answer_pairs = extract_questions_from_test(doc.file_path)

            for question_text, answer_text in question_answer_pairs:
                question = Question(
                    session_id=session_id,
                    question=question_text,
                    answer=answer_text,
                    test_document_id=doc.id,
                    source_type=QuestionSourceType.TEST
                )
                db.session.add(question)
                created_questions.append(question)

        db.session.commit()

        return jsonify({
            'message': f'Successfully extracted {len(created_questions)} questions from TEST documents',
            'questions': [q.to_dict() for q in created_questions]
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500