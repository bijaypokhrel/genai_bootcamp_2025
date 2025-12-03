## backend_go/requirements.txt

``` text
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
SQLAlchemy==2.0.21
invoke==2.2.0
```


## backend_go/app.py

``` python
from flask import Flask, jsonify
from models import db
import os

def create_app():
    app = Flask(__name__)
    
    # Database configuration
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)
    
    # Health check route
    @app.route('/health', methods=['GET'])
    def health_check():
        return jsonify({'status': 'healthy'}), 200
    
    # Register blueprints
    from routes.dashboard import dashboard_bp
    from routes.words import words_bp
    from routes.groups import groups_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(words_bp, url_prefix='/api')
    app.register_blueprint(groups_bp, url_prefix='/api')
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Resource not found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal server error'}), 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, port=5000)
```


## backend_go/tasks.py

``` python
from invoke import task
import os
import sqlite3
import json

@task
def init(c):
    """Initialize the SQLite database file"""
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    
    if os.path.exists(db_path):
        print(f"✓ Database {db_path} already exists")
        return
    
    conn = sqlite3.connect(db_path)
    conn.close()
    print(f"✓ Database initialized at {db_path}")

@task
def migrate(c):
    """Run database migrations"""
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    migrations_dir = os.path.join(os.path.dirname(__file__), 'db', 'migrations')
    
    if not os.path.exists(db_path):
        print("✗ Database not initialized. Run 'invoke init' first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    migration_files = sorted([f for f in os.listdir(migrations_dir) if f.endswith('.sql')])
    
    for migration_file in migration_files:
        file_path = os.path.join(migrations_dir, migration_file)
        print(f"  Running: {migration_file}")
        
        with open(file_path, 'r') as f:
            sql = f.read()
        
        cursor.executescript(sql)
        conn.commit()
    
    conn.close()
    print("✓ Migrations completed successfully")

@task
def seed(c):
    """Seed the database with initial data from JSON files"""
    db_path = os.path.join(os.path.dirname(__file__), 'words.db')
    seeds_dir = os.path.join(os.path.dirname(__file__), 'db', 'seeds')
    
    if not os.path.exists(db_path):
        print("✗ Database not initialized. Run 'invoke init' first.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    for seed_file in sorted(os.listdir(seeds_dir)):
        if seed_file.endswith('.json'):
            group_name = seed_file.replace('.json', '').replace('_', ' ').title()
            print(f"  Seeding: {group_name}")
            
            with open(os.path.join(seeds_dir, seed_file)) as f:
                words_data = json.load(f)
            
            # Insert group
            cursor.execute('INSERT OR IGNORE INTO groups (name) VALUES (?)', (group_name,))
            conn.commit()
            
            cursor.execute('SELECT id FROM groups WHERE name = ?', (group_name,))
            group_id = cursor.fetchone()[0]
            
            # Insert words
            for word_data in words_data:
                cursor.execute(
                    'INSERT INTO words (japanese, romaji, english, parts) VALUES (?, ?, ?, ?)',
                    (word_data.get('kanji', ''), word_data.get('romaji', ''), word_data.get('english', ''), json.dumps(word_data.get('parts', [])))
                )
                conn.commit()
                
                word_id = cursor.lastrowid
                cursor.execute('INSERT INTO words_groups (word_id, group_id) VALUES (?, ?)', (word_id, group_id))
                conn.commit()
    
    conn.close()
    print("✓ Seeding completed successfully")
```

## backend_go/db/migrations/0001_init.sql

```sql
CREATE TABLE IF NOT EXISTS words (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    japanese TEXT NOT NULL,
    romaji TEXT NOT NULL,
    english TEXT NOT NULL,
    parts TEXT
);

CREATE TABLE IF NOT EXISTS groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS words_groups (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    group_id INTEGER NOT NULL,
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (group_id) REFERENCES groups(id),
    UNIQUE(word_id, group_id)
);

CREATE TABLE IF NOT EXISTS study_activities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    thumbnail_url TEXT,
    activity_type TEXT,
    launch_url TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    group_id INTEGER NOT NULL,
    study_activity_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (group_id) REFERENCES groups(id),
    FOREIGN KEY (study_activity_id) REFERENCES study_activities(id)
);

CREATE TABLE IF NOT EXISTS words_review_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    word_id INTEGER NOT NULL,
    study_session_id INTEGER NOT NULL,
    correct BOOLEAN NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (word_id) REFERENCES words(id),
    FOREIGN KEY (study_session_id) REFERENCES study_sessions(id)
);

CREATE INDEX IF NOT EXISTS idx_words_groups_word_id ON words_groups(word_id);
CREATE INDEX IF NOT EXISTS idx_words_groups_group_id ON words_groups(group_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_group_id ON study_sessions(group_id);
CREATE INDEX IF NOT EXISTS idx_study_sessions_activity_id ON study_sessions(study_activity_id);
CREATE INDEX IF NOT EXISTS idx_words_review_word_id ON words_review_items(word_id);
CREATE INDEX IF NOT EXISTS idx_words_review_session_id ON words_review_items(study_session_id);
```

## backend_go/db/seeds/hiragana.json

```json
[
    {
        "kanji": "あ",
        "romaji": "a",
        "english": "a"
    },
    {
        "kanji": "い",
        "romaji": "i",
        "english": "i"
    },
    {
        "kanji": "う",
        "romaji": "u",
        "english": "u"
    },
    {
        "kanji": "え",
        "romaji": "e",
        "english": "e"
    },
    {
        "kanji": "お",
        "romaji": "o",
        "english": "o"
    }
]
```

## backend_go/db/seeds/katakana.json

```json
[
    {
        "kanji": "ア",
        "romaji": "a",
        "english": "a"
    },
    {
        "kanji": "イ",
        "romaji": "i",
        "english": "i"
    },
    {
        "kanji": "ウ",
        "romaji": "u",
        "english": "u"
    },
    {
        "kanji": "エ",
        "romaji": "e",
        "english": "e"
    },
    {
        "kanji": "オ",
        "romaji": "o",
        "english": "o"
    }
]
```



## backend_go/models/__init__.py

``` python
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

```

## backend_go/routes/dashboard.py  

``` python
from flask import Blueprint, jsonify
from app import db
from models import StudySession, WordsReviewItem, Word
from sqlalchemy import func
from datetime import datetime, timedelta

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('/dashboard/last_study_session', methods=['GET'])
def last_study_session():
    session = StudySession.query.order_by(StudySession.created_at.desc()).first()
    
    if not session:
        return jsonify({'error': 'No study sessions found'}), 404
    
    correct_count = sum(1 for item in session.review_items if item.correct)
    wrong_count = sum(1 for item in session.review_items if not item.correct)
    
    return jsonify({
        'id': session.id,
        'study_activity_id': session.study_activity_id,
        'activity_name': session.activity.name if session.activity else None,
        'group_id': session.group_id,
        'group_name': session.group.name,
        'created_at': session.created_at.isoformat() + 'Z' if session.created_at else None,
        'correct_count': correct_count,
        'wrong_count': wrong_count,
        'total_reviews': len(session.review_items),
    })

@dashboard_bp.route('/dashboard/study_progress', methods=['GET'])
def study_progress():
    total_words_available = Word.query.count()
    
    studied_words = db.session.query(func.count(func.distinct(Word.id))).join(
        Word.review_items
    ).scalar() or 0
    
    last_studied = StudySession.query.order_by(StudySession.created_at.desc()).first()
    last_studied_date = last_studied.created_at.isoformat() + 'Z' if last_studied else None
    
    mastery_percentage = (studied_words / total_words_available * 100) if total_words_available > 0 else 0
    
    return jsonify({
        'total_words_studied': studied_words,
        'total_words_available': total_words_available,
        'mastery_percentage': round(mastery_percentage, 1),
        'last_studied_date': last_studied_date,
    })

@dashboard_bp.route('/dashboard/quick_stats', methods=['GET'])
def quick_stats():
    total_reviews = WordsReviewItem.query.count()
    correct_reviews = WordsReviewItem.query.filter_by(correct=True).count()
    success_rate = (correct_reviews / total_reviews * 100) if total_reviews > 0 else 0
    
    total_sessions = StudySession.query.count()
    
    total_active_groups = db.session.query(func.count(func.distinct(StudySession.group_id))).scalar() or 0
    
    # Calculate study streak
    today = datetime.utcnow().date()
    streak_days = 0
    current_date = today
    
    while True:
        sessions_on_date = StudySession.query.filter(
            db.func.date(StudySession.created_at) == current_date
        ).count()
        if sessions_on_date == 0:
            break
        streak_days += 1
        current_date -= timedelta(days=1)
    
    return jsonify({
        'success_rate': round(success_rate, 1),
        'total_study_sessions': total_sessions,
        'total_active_groups': total_active_groups,
        'study_streak_days': streak_days,
    })

```

## backend_go/rounts/groups.py

``` python
from flask import Blueprint, jsonify, request
from models import db, Group, Word, StudySession

groups_bp = Blueprint('groups', __name__)

def paginate_query(query, page=1, per_page=100):
    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return items, {
        'current_page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_items,
    }

@groups_bp.route('/groups', methods=['GET'])
def get_groups():
    page = request.args.get('page', 1, type=int)
    
    query = Group.query
    groups, pagination = paginate_query(query, page)
    
    return jsonify({
        'data': [g.to_dict() for g in groups],
        'pagination': pagination,
    })

@groups_bp.route('/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    group = Group.query.get_or_404(group_id)
    
    return jsonify({
        'id': group.id,
        'name': group.name,
        'total_word_count': len(group.words),
        'created_at': '2025-01-01T00:00:00Z',
    })

@groups_bp.route('/groups/<int:group_id>/words', methods=['GET'])
def get_group_words(group_id):
    group = Group.query.get_or_404(group_id)
    page = request.args.get('page', 1, type=int)
    
    query = Word.query.filter(Word.groups.contains(group))
    words, pagination = paginate_query(query, page)
    
    return jsonify({
        'data': [w.to_dict() for w in words],
        'pagination': pagination,
    })

@groups_bp.route('/groups/<int:group_id>/study_sessions', methods=['GET'])
def get_group_study_sessions(group_id):
    group = Group.query.get_or_404(group_id)
    page = request.args.get('page', 1, type=int)
    
    query = StudySession.query.filter_by(group_id=group_id).order_by(StudySession.created_at.desc())
    sessions, pagination = paginate_query(query, page)
    
    return jsonify({
        'data': [s.to_dict() for s in sessions],
        'pagination': pagination,
    })

```

## backend_go/routes/words.py

``` python
from flask import Blueprint, jsonify, request
from models import db, Word

words_bp = Blueprint('words', __name__)

def paginate_query(query, page=1, per_page=100):
    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return items, {
        'current_page': page,
        'per_page': per_page,
        'total_pages': total_pages,
        'total_items': total_items,
    }

@words_bp.route('/words', methods=['GET'])
def get_words():
    page = request.args.get('page', 1, type=int)
    
    query = Word.query
    words, pagination = paginate_query(query, page)
    
    return jsonify({
        'data': [w.to_dict() for w in words],
        'pagination': pagination,
    })

@words_bp.route('/words/<int:word_id>', methods=['GET'])
def get_word(word_id):
    word = Word.query.get_or_404(word_id)
    return jsonify(word.to_dict(include_groups=True))
```

