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
    from routes.study_sessions import study_sessions_bp
    from routes.study_activities import study_activities_bp
    from routes.reviews import reviews_bp
    from routes.admin import admin_bp
    app.register_blueprint(dashboard_bp, url_prefix='/api')
    app.register_blueprint(words_bp, url_prefix='/api')
    app.register_blueprint(groups_bp, url_prefix='/api')
    app.register_blueprint(study_sessions_bp, url_prefix='/api')
    print("@@@ study_activities_bp registered")
    app.register_blueprint(study_activities_bp, url_prefix='/api')
    app.register_blueprint(reviews_bp, url_prefix='/api')
    app.register_blueprint(admin_bp, url_prefix='/api')
    
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
    app.run(debug=True, port=8000)
