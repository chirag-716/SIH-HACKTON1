"""
GUVNL Queue Management System - Flask Application Factory
"""

import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS
from flask_socketio import SocketIO
from celery import Celery
from prometheus_flask_exporter import PrometheusMetrics
import redis

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
socketio = SocketIO(cors_allowed_origins="*")
celery = Celery(__name__)

def create_app(config_name=None):
    """Application factory pattern"""
    app = Flask(__name__)
    
    # Load configuration
    if config_name is None:
        config_name = os.getenv('FLASK_ENV', 'development')
    
    if config_name == 'production':
        app.config.from_object('config.ProductionConfig')
    elif config_name == 'testing':
        app.config.from_object('config.TestingConfig')
    else:
        app.config.from_object('config.DevelopmentConfig')
    
    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    socketio.init_app(app, async_mode='eventlet')
    
    # Configure CORS
    CORS(app, resources={
        r"/api/*": {"origins": app.config['CORS_ORIGINS'].split(',')}
    })
    
    # Initialize Celery
    celery.conf.update(app.config)
    
    # Initialize Redis connection
    redis_client = redis.from_url(app.config['REDIS_URL'])
    app.redis = redis_client
    
    # Initialize monitoring
    metrics = PrometheusMetrics(app)
    metrics.info('app_info', 'GUVNL Queue Management System', version='1.0.0')
    
    # Register blueprints
    from app.routes import auth, appointments, queues, admin, notifications
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(appointments.bp, url_prefix='/api/appointments')
    app.register_blueprint(queues.bp, url_prefix='/api/queues')
    app.register_blueprint(admin.bp, url_prefix='/api/admin')
    app.register_blueprint(notifications.bp, url_prefix='/api/notifications')
    
    # Register SocketIO events
    from app.routes import socket_events
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'message': 'Resource not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'message': 'Internal server error'}, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        return {'message': 'Bad request'}, 400
    
    # Health check endpoint
    @app.route('/health')
    def health_check():
        try:
            # Check database connection
            db.engine.execute('SELECT 1')
            # Check Redis connection
            app.redis.ping()
            return {'status': 'healthy', 'database': 'connected', 'redis': 'connected'}, 200
        except Exception as e:
            return {'status': 'unhealthy', 'error': str(e)}, 500
    
    # API info endpoint
    @app.route('/api')
    def api_info():
        return {
            'name': 'GUVNL Queue Management API',
            'version': '1.0.0',
            'description': 'REST API for GUVNL Queue Management System',
            'endpoints': {
                'auth': '/api/auth',
                'appointments': '/api/appointments',
                'queues': '/api/queues',
                'admin': '/api/admin',
                'notifications': '/api/notifications',
                'docs': '/api/docs',
                'health': '/health'
            }
        }
    
    # Configure logging
    if not app.debug and not app.testing:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = logging.FileHandler('logs/guvnl_api.log')
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        app.logger.setLevel(logging.INFO)
        app.logger.info('GUVNL Queue Management API startup')
    
    return app

def make_celery(app):
    """Create Celery instance with Flask app context"""
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    
    class ContextTask(celery.Task):
        """Make celery tasks work with Flask app context"""
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
    
    celery.Task = ContextTask
    return celery