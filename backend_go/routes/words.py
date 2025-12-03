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
