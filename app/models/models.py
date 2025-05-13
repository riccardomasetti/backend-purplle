from app import db
import datetime
import uuid
from sqlalchemy.orm import validates
from enum import Enum


# tables for many-to-many relationships
learning_session_resource = db.Table('learning_session_resource',
    db.Column('session_id', db.String(36), db.ForeignKey('learning_session.id'), primary_key=True),
    db.Column('document_id', db.String(36), db.ForeignKey('document.id'), primary_key=True)
)

learning_session_test = db.Table('learning_session_test',
    db.Column('session_id', db.String(36), db.ForeignKey('learning_session.id'), primary_key=True),
    db.Column('document_id', db.String(36), db.ForeignKey('document.id'), primary_key=True)
)


# Types of documents
class DocumentCategory(Enum):
    RESOURCE = 'Resource'
    TEST = 'Test'

# Document model
class Document(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    filename = db.Column(db.String(200), nullable=False)
    category = db.Column(db.Enum(DocumentCategory), nullable=False)
    content = db.Column(db.Text, nullable=True)
    file_path = db.Column(db.String(500), nullable=False)

    def to_dict(self):
        return {
            'projectId': self.project_id,
            'filename': self.filename,
            'category': self.category.value,
            'content': self.content
        }


class DocumentReference(db.Model):
    __tablename__ = 'document_reference'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    question_id = db.Column(db.String(36), db.ForeignKey('question.id'), nullable=False)
    document_id = db.Column(db.String(36), db.ForeignKey('document.id'), nullable=False)

    line_number = db.Column(db.Integer, nullable=True)
    page_number = db.Column(db.Integer, nullable=True)
    char_offset = db.Column(db.Integer, nullable=True)
    context_text = db.Column(db.Text, nullable=True)

    document = db.relationship('Document', foreign_keys=[document_id])

    def to_dict(self):
        return {
            'document': self.document.to_dict(),
            'lineNumber': self.line_number,
            'pageNumber': self.page_number,
            'charOffset': self.char_offset,
            'contextText': self.context_text
        }

# Question model
class Question(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = db.Column(db.String(36), db.ForeignKey('learning_session.id'), nullable=False)
    question = db.Column(db.Text, nullable=False)
    answer = db.Column(db.Text, nullable=False)
    correction = db.Column(db.Text, nullable=True)
    evaluation = db.Column(db.Float, nullable=True)

    # Relazion with the document for the question
    test_document_id = db.Column(db.String(36), db.ForeignKey('document.id'), nullable=False)
    test_document = db.relationship('Document', foreign_keys=[test_document_id])

    references = db.relationship('DocumentReference',
                                 backref='question',
                                 cascade='all, delete-orphan',
                                 lazy=True)

    def to_dict(self):
        return {
            'question': self.question,
            'answer': self.answer,
            'correction': self.correction,
            'evaluation': self.evaluation,
            'testDocument': self.test_document.to_dict(),
            'resources': [ref.to_dict() for ref in self.references]
        }


# LearningSession moodel
class LearningSession(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    duration_minutes = db.Column(db.Integer, nullable=False)
    motivation = db.Column(db.Text, nullable=True)
    learning_objective = db.Column(db.Text, nullable=True)

    # Metriche
    awareness_level = db.Column(db.Float, nullable=True)
    confidence_level = db.Column(db.Float, nullable=True)
    energy_level = db.Column(db.Float, nullable=True)
    performance_level = db.Column(db.Float, nullable=True)
    satisfaction_level = db.Column(db.Float, nullable=True)

    # Relazioni
    resource_documents = db.relationship('Document',
                                       secondary=learning_session_resource,
                                       backref='resource_sessions')
    test_documents = db.relationship('Document',
                                    secondary=learning_session_test,
                                    backref='test_sessions')
    questions = db.relationship('Question', backref='session', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'projectId': self.project_id,
            'timestamp': self.timestamp.isoformat(),
            'durationMinutes': self.duration_minutes,
            'motivation': self.motivation,
            'learningObjective': self.learning_objective,
            'metrics': {
                'awarenessLevel': self.awareness_level,
                'confidenceLevel': self.confidence_level,
                'energyLevel': self.energy_level,
                'performanceLevel': self.performance_level,
                'satisfactionLevel': self.satisfaction_level
            },
            'resourceDocuments': [doc.to_dict() for doc in self.resource_documents],
            'testDocuments': [doc.to_dict() for doc in self.test_documents],
            'questions': [q.to_dict() for q in self.questions]
        }



class Project(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)

    # Metrics
    overall_performance = db.Column(db.Float, nullable=True)
    difficulty = db.Column(db.Float, nullable=True)
    interest = db.Column(db.Float, nullable=True)

    motivations = db.Column(db.JSON, default=list)

    documents = db.relationship('Document', backref='project', lazy=True, cascade='all, delete-orphan')

    milestones = db.relationship('Milestone',
                                 backref='project', lazy=True, cascade='all, delete-orphan')

    deadline_milestone = db.relationship('Milestone',
                                         primaryjoin="and_(Project.id==Milestone.project_id, "
                                                     "Milestone.is_deadline==True)",
                                         backref='project_as_deadline', lazy=True, uselist=False, viewonly=True)

    learning_sessions = db.relationship('LearningSession', backref='project', lazy=True, cascade='all, delete-orphan')

    @validates('overall_performance', 'difficulty', 'interest')
    def validate_percentage(self, key, value):
        if value is not None and not 0 <= value <= 100:
            raise ValueError(f"{key} must be between 0 and 100")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'milestones': [m.to_dict() for m in self.milestones],
            'deadlineMilestone': self.deadline_milestone.to_dict() if self.deadline_milestone else None,
            'documents': [d.to_dict() for d in self.documents],
            'motivations': self.motivations,
            'sessions': [s.to_dict() for s in self.learning_sessions],
            'metrics': {
                'overallPerformance': self.overall_performance,
                'difficulty': self.difficulty,
                'interest': self.interest
            }
        }

    def __repr__(self):
        return f'<Project {self.title}>'


class Milestone(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    is_deadline = db.Column(db.Boolean, default=False)
    project_id = db.Column(db.String(36), db.ForeignKey('project.id'), nullable=True)

    #__table_args__ = (
    #    db.CheckConstraint(
    #        'NOT (is_deadline AND EXISTS (SELECT 1 FROM milestone m '
    #        'WHERE m.project_id = project_id AND m.is_deadline AND m.id != id))',
    #        name='unique_deadline_per_project'
    #    ),
    #)

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.due_date.isoformat(),
            'isDeadline': self.is_deadline
        }

