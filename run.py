"""
InsightFlow Application Entry Point.
"""
import os
from app import create_app, socketio

# Get configuration from environment
config_name = os.getenv('FLASK_ENV', 'development')

# Create application
app = create_app(config_name)


if __name__ == '__main__':
    # Run with SocketIO for WebSocket support
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=app.config['DEBUG']
    )
