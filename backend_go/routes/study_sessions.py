from flask import Blueprint, jsonify, request
from models import db, StudySession, WordsReviewItem
from sqlalchemy import func

study_sessions_bp = Blueprint('study_sessions', __name__)

def paginate_query(query, page=1, per_page=100):
    total = query.count()
    pages = (total + per_page - 1) // per_page
    items = query.offset((page-1)*per_page).limit(per_page).all()
    return items, {
        'current_page': page,
        'per_page': per_page,
        'total_pages': pages,
        'total_items': total
    }

@study_sessions_bp.route('/study_sessions', methods=['GET'])
def list_sessions():
    page = request.args.get('page', 1, type=int)
    query = StudySession.query.order_by(StudySession.created_at.desc())
    sessions, pag = paginate_query(query, page)
    return jsonify({
        'data': [s.to_dict() for s in sessions],
        'pagination': pag
    })

@study_sessions_bp.route('/study_sessions/<int:session_id>', methods=['GET'])
def get_session(session_id):
    session = StudySession.query.get_or_404(session_id)
    return jsonify(session.to_dict())

@study_sessions_bp.route('/study_sessions/<int:session_id>/words', methods=['GET'])
def session_words(session_id):
    page = request.args.get('page', 1, type=int)
    query = WordsReviewItem.query.filter_by(study_session_id=session_id)\
                                  .order_by(WordsReviewItem.created_at.desc())
    items, pag = paginate_query(query, page)
    return jsonify({
        'data': [i.to_dict(include_word_details=True) for i in items],
        'pagination': pag
    })