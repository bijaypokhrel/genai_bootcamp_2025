from flask import Blueprint, jsonify, request
from models import db, StudyActivity, StudySession

study_activities_bp = Blueprint('study_activities', __name__)

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

@study_activities_bp.route('/study_activities/<int:activity_id>', methods=['GET'])
def get_activity(activity_id):
    activity = StudyActivity.query.get_or_404(activity_id)
    return jsonify(activity.to_dict())

@study_activities_bp.route('/study_activities/<int:activity_id>/study_sessions', methods=['GET'])
def activity_sessions(activity_id):
    page = request.args.get('page', 1, type=int)
    # 404 if activity does not exist
    StudyActivity.query.get_or_404(activity_id)
    query = StudySession.query.filter_by(study_activity_id=activity_id)\
                              .order_by(StudySession.created_at.desc())
    sessions, pag = paginate_query(query, page)
    return jsonify({
        'data': [s.to_dict() for s in sessions],
        'pagination': pag
    })

@study_activities_bp.route('/study_activities', methods=['POST'])
def create_activity_session():
    data = request.get_json(silent=True) or {}
    group_id = data.get('group_id')
    activity_type = data.get('study_activity_type')

    if not group_id or not activity_type:
        return jsonify({'error': 'group_id and study_activity_type required'}), 400

    # create the activity row
    activity = StudyActivity(
        name=f'{activity_type} session',
        activity_type=activity_type,
        launch_url=f'https://external-app.com/{activity_type}'
    )
    db.session.add(activity)
    db.session.flush()  # to get activity.id

    # create the study session
    session = StudySession(group_id=group_id, study_activity_id=activity.id)
    db.session.add(session)
    db.session.commit()

    return jsonify({
        'id': session.id,
        'study_session_id': session.id,
        'group_id': session.group_id,
        'created_at': session.created_at.isoformat() + 'Z'
    }), 201