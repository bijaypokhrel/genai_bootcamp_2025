from flask_sqlalchemy import SQLAlchemy
import json
from datetime import datetime

# Create db instance here, not import from app
db = SQLAlchemy()

class Word(db.Model):
    __tablename__ = 'words'
    
    id = db.Column(db.Integer, primary_key=True)
    japanese = db.Column(db.String(255), nullable=False)
    romaji = db.Column(db.String(255), nullable=False)
    english = db.Column(db.String(255), nullable=False)
    parts = db.Column(db.String(500))
    
    def to_dict(self, include_groups=False):
        data = {
            'id': self.id,
            'japanese': self.japanese,
            'romaji': self.romaji,
            'english': self.english,
        }
        
        if self.parts:
            try:
                data['parts'] = json.loads(self.parts)
            except:
                data['parts'] = []
        
        correct_count = sum(1 for item in self.review_items if item.correct)
        wrong_count = sum(1 for item in self.review_items if not item.correct)
        data['correct_count'] = correct_count
        data['wrong_count'] = wrong_count
        
        if include_groups:
            data['groups'] = [{'id': g.id, 'name': g.name} for g in self.groups]
        
        return data

class Group(db.Model):
    __tablename__ = 'groups'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    
    words = db.relationship('Word', secondary='words_groups', backref='groups')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'word_count': len(self.words),
        }

class WordsGroup(db.Model):
    __tablename__ = 'words_groups'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)

class StudyActivity(db.Model):
    __tablename__ = 'study_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(500))
    thumbnail_url = db.Column(db.String(500))
    activity_type = db.Column(db.String(100))
    launch_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'thumbnail_url': self.thumbnail_url,
            'activity_type': self.activity_type,
            'launch_url': self.launch_url,
            'created_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }

class StudySession(db.Model):
    __tablename__ = 'study_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    study_activity_id = db.Column(db.Integer, db.ForeignKey('study_activities.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    group = db.relationship('Group', backref='study_sessions')
    activity = db.relationship('StudyActivity', backref='study_sessions')
    review_items = db.relationship('WordsReviewItem', backref='study_session', cascade='all, delete-orphan')

class WordsReviewItem(db.Model):
    __tablename__ = 'words_review_items'
    
    id = db.Column(db.Integer, primary_key=True)
    word_id = db.Column(db.Integer, db.ForeignKey('words.id'), nullable=False)
    study_session_id = db.Column(db.Integer, db.ForeignKey('study_sessions.id'), nullable=False)
    correct = db.Column(db.Boolean, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    word = db.relationship('Word', backref='review_items')
    
    def to_dict(self, include_word_details=False):
        data = {
            'id': self.id,
            'word_id': self.word_id,
            'study_session_id': self.study_session_id,
            'correct': self.correct,
            'reviewed_at': self.created_at.isoformat() + 'Z' if self.created_at else None,
        }
        
        if include_word_details and self.word:
            data.update({
                'japanese': self.word.japanese,
                'romaji': self.word.romaji,
                'english': self.word.english,
            })
        
        return data
