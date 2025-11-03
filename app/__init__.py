"""
Broker Assistant Flask Application Factory.
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from flask_socketio import SocketIO
import redis

from config.config import config_by_name

# Initialize extensions
db = SQLAlchemy()
migrate = Migrate()
socketio = SocketIO(cors_allowed_origins="*")
redis_client = None


def create_app(config_name='default'):
    """
    Application factory pattern.

    Args:
        config_name: Configuration name (development, production, testing)

    Returns:
        Flask application instance
    """
    app = Flask(__name__)

    # Load configuration
    app.config.from_object(config_by_name[config_name])

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    CORS(app)
    socketio.init_app(app)

    # Initialize Redis
    global redis_client
    redis_client = redis.from_url(
        app.config['REDIS_URL'],
        decode_responses=True
    )

    # Register blueprints
    from app.routes import main, portfolio, analysis, websocket
    app.register_blueprint(main.bp)
    app.register_blueprint(portfolio.bp)
    app.register_blueprint(analysis.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
