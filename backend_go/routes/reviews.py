from flask import Blueprint, jsonify, request
from models import db, WordsReviewItem, StudySession, Word

reviews_bp = Blueprint('reviews', __name__)

@reviews_bp.route('/study_sessions/<int:session_id>/words/<int:word_id>/review', methods=['POST'])
def record_review(session_id, word_id):
    data = request.get_json(silent=True) or {}
    correct = data.get('correct')

    if not isinstance(correct, bool):
        return jsonify({'error': 'correct (boolean) is required'}), 400

    # ensure session and word exist
    StudySession.query.get_or_404(session_id)
    Word.query.get_or_404(word_id)

    item = WordsReviewItem(
        study_session_id=session_id,
        word_id=word_id,
        correct=correct
    )
    db.session.add(item)
    db.session.commit()

    return jsonify({
        'id': item.id,
        'word_id': item.word_id,
        'study_session_id': item.study_session_id,
        'correct': item.correct,
        'created_at': item.created_at.isoformat() + 'Z'
    }), 201