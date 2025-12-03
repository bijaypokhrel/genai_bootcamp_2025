from flask import Blueprint, jsonify
from models import db, StudySession, WordsReviewItem
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/reset_history', methods=['POST'])
def reset_history():
    """Clear all study sessions and review items, keep vocabulary."""
    deleted_sessions = StudySession.query.delete()
    deleted_reviews  = WordsReviewItem.query.delete()
    db.session.commit()
    return jsonify({
        'message': 'Study history reset successfully',
        'deleted_sessions': deleted_sessions,
        'deleted_reviews': deleted_reviews
    }), 200

@admin_bp.route('/full_reset', methods=['POST'])
def full_reset():
    """Drop all data, re-run migrations, re-seed with default sets."""
    db.drop_all()
    db.create_all()

    # re-insert default study activities
    from models import StudyActivity
    activities = [
        StudyActivity(name='Hiragana Quiz',  activity_type='quiz',
                      launch_url='https://external-app.com/hiragana'),
        StudyActivity(name='Katakana Quiz', activity_type='quiz',
                      launch_url='https://external-app.com/katakana')
    ]
    for a in activities:
        db.session.add(a)
    db.session.commit()

    return jsonify({
        'message': 'Database reset and reseeded successfully',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    }), 200