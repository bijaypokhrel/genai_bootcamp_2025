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
