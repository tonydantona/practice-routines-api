"""
Flask application entry point.

This is the main entry point for running the Practice Routines API server.
"""

from src.api.app_factory import create_app
from src.config.settings import settings

# Create the Flask application
app = create_app()

if __name__ == "__main__":
    app.run(
        debug=settings.DEBUG,
        host=settings.FLASK_HOST,
        port=settings.FLASK_PORT
    )