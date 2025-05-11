from app import db
import datetime
import uuid
from sqlalchemy.orm import validates

class Project(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(100), nullable=True)  # Mettiamo?

    # Metrics
    overall_performance = db.Column(db.Float, default=0.0)
    difficulty = db.Column(db.Float, default=0.0)
    interest = db.Column(db.Float, default=0.0)

    motivations = db.Column(db.JSON, default=list)

    #documents = db.relationship('Document', backref='project', lazy=True, cascade='all, delete-orphan')

    milestones = db.relationship('Milestone',
                                 backref='project', lazy=True, cascade='all, delete-orphan')

    deadline_milestone = db.relationship('Milestone',
                                         primaryjoin="and_(Project.id==Milestone.project_id, "
                                                     "Milestone.is_deadline==True)",
                                         backref='project_as_deadline', lazy=True, uselist=False, viewonly=True)

    #learning_sessions = db.relationship('LearningSession', backref='project', lazy=True, cascade='all, delete-orphan')

    @validates('overall_performance', 'difficulty', 'interest')
    def validate_percentage(self, key, value):
        if not 0 <= value <= 100:
            raise ValueError(f"{key} must be between 0 and 100")
        return value

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'milestones': [m.to_dict() for m in self.milestones],
            'deadlineMilestone': self.deadline_milestone.to_dict() if self.deadline_milestone else None,
            #'documents': [d.to_dict() for d in self.documents],
            'motivations': self.motivations,
            #'sessions': [s.to_dict() for s in self.learning_sessions],
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

    __table_args__ = (
        db.CheckConstraint(
            'NOT (is_deadline AND EXISTS (SELECT 1 FROM milestone m '
            'WHERE m.project_id = project_id AND m.is_deadline AND m.id != id))',
            name='unique_deadline_per_project'
        ),
    )

    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'date': self.due_date.isoformat() if self.due_date else None,
            'isDeadline': self.is_deadline
        }

