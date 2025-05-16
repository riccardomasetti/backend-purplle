import os
import requests
import json
import uuid
from datetime import datetime, timedelta
import tempfile
import time


BASE_URL = "http://localhost:5000/api"
PROJECTS_URL = f"{BASE_URL}/projects"


PROJECT_ID = 1
RESOURCE_DOC_ID = 2
TEST_DOC_ID = 3
MILESTONE_ID = 4
SESSION_ID = 5
QUESTION_ID = 6


def print_response(response, description):
    print(f"\n--- {description} ---")
    print(f"Status: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Raw response: {response.text}")
    return response.json() if response.status_code < 400 else None


def create_temp_file(content="Test content", filename="test_file.txt"):
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    with open(file_path, 'w') as f:
        f.write(content)
    return file_path


def test_project_creation():
    global PROJECT_ID

    if PROJECT_ID:
        print(f"\n--- Using existing project ID: {PROJECT_ID} ---")
        return {"id": PROJECT_ID}

    project_data = {
        "title": f"Test Project {uuid.uuid4()}",
        "motivations": ["Learn Python", "Improve skills"],
        "overall_performance": 70,
        "difficulty": 60,
        "interest": 85
    }

    response = requests.post(PROJECTS_URL, json=project_data)
    result = print_response(response, "1. Project Creation")

    if result:
        PROJECT_ID = result.get('id')

    return result


def test_document_upload(project_id):
    global RESOURCE_DOC_ID, TEST_DOC_ID

    if RESOURCE_DOC_ID and TEST_DOC_ID:
        print(f"\n--- Using existing document IDs: Resource={RESOURCE_DOC_ID}, Test={TEST_DOC_ID} ---")
        return {"id": RESOURCE_DOC_ID}, {"id": TEST_DOC_ID}

    file_path = create_temp_file(content="Test resource document", filename="resource.txt")

    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, 'text/plain')}
        data = {'category': 'RESOURCE'}
        response = requests.post(f"{PROJECTS_URL}/{project_id}/documents", files=files, data=data)

    resource_document = print_response(response, "2. Document Upload (Resource)")

    if resource_document:
        RESOURCE_DOC_ID = resource_document.get('id')

    file_path = create_temp_file(content="Test test document", filename="test.txt")

    with open(file_path, 'rb') as file:
        files = {'file': (os.path.basename(file_path), file, 'text/plain')}
        data = {'category': 'TEST'}
        response = requests.post(f"{PROJECTS_URL}/{project_id}/documents", files=files, data=data)

    test_document = print_response(response, "3. Document Upload (Test)")

    if test_document:
        TEST_DOC_ID = test_document.get('id')

    return resource_document, test_document


def test_milestone_creation(project_id):
    global MILESTONE_ID

    if MILESTONE_ID:
        print(f"\n--- Using existing milestone ID: {MILESTONE_ID} ---")
        return {"id": MILESTONE_ID}, {"id": "deadline-milestone-id"}

    milestone_data = {
        "title": "Complete first module",
        "date": (datetime.now() + timedelta(days=7)).isoformat(),
        "isDeadline": False
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/milestones", json=milestone_data)
    regular_milestone = print_response(response, "4. Regular Milestone Creation")

    if regular_milestone:
        MILESTONE_ID = regular_milestone.get('id')

    deadline_data = {
        "title": "Project Completion",
        "date": (datetime.now() + timedelta(days=30)).isoformat(),
        "isDeadline": True
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/milestones", json=deadline_data)
    deadline_milestone = print_response(response, "5. Deadline Milestone Creation")

    return regular_milestone, deadline_milestone


def test_session_creation(project_id):
    global SESSION_ID

    if SESSION_ID:
        print(f"\n--- Using existing session ID: {SESSION_ID} ---")
        return {"id": SESSION_ID}

    session_data = {
        "durationMinutes": 60,
        "motivation": "Understanding core concepts",
        "learningObjective": "Master the basics",
        "metrics": {
            "awarenessLevel": 75,
            "confidenceLevel": 65,
            "energyLevel": 80,
            "performanceLevel": 70,
            "satisfactionLevel": 85
        }
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/sessions", json=session_data)
    session = print_response(response, "6. Learning Session Creation")

    if session:
        SESSION_ID = session.get('id')

    return session


def test_documents_to_session(project_id, session_id, resource_doc_id, test_doc_id):
    data = {
        "resourceDocumentIds": [resource_doc_id],
        "testDocumentIds": [test_doc_id]
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/documents", json=data)
    return print_response(response, "7. Adding Documents to Session")


def test_generate_questions(project_id, session_id):
    response = requests.post(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/generate-questions")
    return print_response(response, "8. Generate Questions Trigger")


def test_create_question(project_id, session_id, test_doc_id):
    global QUESTION_ID

    # Se l'ID della domanda è già impostato, usa quello
    if QUESTION_ID:
        print(f"\n--- Using existing question ID: {QUESTION_ID} ---")
        return {"id": QUESTION_ID}

    question_data = {
        "question": "What is the main purpose of Flask?",
        "answer": "Flask is a lightweight WSGI web application framework in Python.",
        "testDocumentId": test_doc_id,
        "evaluation": 85
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/questions", json=question_data)
    question = print_response(response, "9. Manual Question Creation")

    if question:
        QUESTION_ID = question.get('id')

    return question


def test_add_resources_to_question(project_id, session_id, question_id, resource_doc_id):
    data = {
        "resourceDocumentIds": [resource_doc_id]
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/questions/{question_id}/resources",
                             json=data)
    return print_response(response, "10. Adding Resources to Question")


def test_add_reference_to_question(project_id, session_id, question_id, resource_doc_id):
    data = {
        "documentId": resource_doc_id,
        "pageNumber": 1,
        "lineNumber": 5,
        "contextText": "Flask is a lightweight WSGI web application framework in Python."
    }

    response = requests.post(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/questions/{question_id}/references",
                             json=data)
    return print_response(response, "11. Adding Document Reference to Question")


def test_get_all_projects():
    response = requests.get(PROJECTS_URL)
    return print_response(response, "12. Get All Projects")


def test_get_project(project_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}")
    return print_response(response, "13. Get Specific Project")


def test_get_project_documents(project_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/documents")
    return print_response(response, "14. Get Project Documents")


def test_get_document(project_id, document_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/documents/{document_id}")
    return print_response(response, "15. Get Specific Document")


def test_get_project_milestones(project_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/milestones")
    return print_response(response, "16. Get Project Milestones")


def test_get_milestone(project_id, milestone_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/milestones/{milestone_id}")
    return print_response(response, "17. Get Specific Milestone")


def test_get_project_sessions(project_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/sessions")
    return print_response(response, "18. Get Project Sessions")


def test_get_session(project_id, session_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}")
    return print_response(response, "19. Get Specific Session")


def test_get_session_questions(project_id, session_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/questions")
    return print_response(response, "20. Get Session Questions")


def test_get_question(project_id, session_id, question_id):
    response = requests.get(f"{PROJECTS_URL}/{project_id}/sessions/{session_id}/questions/{question_id}")
    return print_response(response, "21. Get Specific Question")


def run_all_tests():
    print("\n\n========== STARTING PURPLLE API TESTS ==========\n")

    project = test_project_creation()
    if not project:
        print("Failed to create project. Stopping tests.")
        return

    project_id = PROJECT_ID

    resource_doc, test_doc = test_document_upload(project_id)
    if not resource_doc or not test_doc:
        print("Failed to upload documents. Stopping tests.")
        return

    resource_doc_id = RESOURCE_DOC_ID
    test_doc_id = TEST_DOC_ID

    regular_milestone, deadline_milestone = test_milestone_creation(project_id)
    if not regular_milestone or not deadline_milestone:
        print("Failed to create milestones. Stopping tests.")
        return

    milestone_id = MILESTONE_ID

    session = test_session_creation(project_id)
    if not session:
        print("Failed to create session. Stopping tests.")
        return

    session_id = SESSION_ID

    updated_session = test_documents_to_session(project_id, session_id, resource_doc_id, test_doc_id)
    if not updated_session:
        print("Failed to add documents to session. Stopping tests.")
        return

    test_generate_questions(project_id, session_id)

    question = test_create_question(project_id, session_id, test_doc_id)
    if not question:
        print("Failed to create question. Stopping tests.")
        return

    question_id = QUESTION_ID

    test_add_resources_to_question(project_id, session_id, question_id, resource_doc_id)

    test_add_reference_to_question(project_id, session_id, question_id, resource_doc_id)

    test_get_all_projects()
    test_get_project(project_id)
    test_get_project_documents(project_id)
    test_get_document(project_id, resource_doc_id)
    test_get_project_milestones(project_id)
    test_get_milestone(project_id, milestone_id)
    test_get_project_sessions(project_id)
    test_get_session(project_id, session_id)
    test_get_session_questions(project_id, session_id)
    test_get_question(project_id, session_id, question_id)

    print("\n\n========== ALL TESTS COMPLETED ==========\n")
    print(f"PROJECT_ID = {PROJECT_ID}")
    print(f"RESOURCE_DOC_ID = {RESOURCE_DOC_ID}")
    print(f"TEST_DOC_ID = {TEST_DOC_ID}")
    print(f"MILESTONE_ID = {MILESTONE_ID}")
    print(f"SESSION_ID = {SESSION_ID}")
    print(f"QUESTION_ID = {QUESTION_ID}")


if __name__ == "__main__":
    run_all_tests()
