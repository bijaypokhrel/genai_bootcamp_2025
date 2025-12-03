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
