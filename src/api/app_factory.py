"""
Flask application factory.
"""

import logging
from flask import Flask
from flask_cors import CORS
from src.config.settings import settings
from src.config.database import get_chroma_client, get_openai_client, get_collection
from src.repositories.routine_repository import RoutineRepository
from src.services.embedding_service import EmbeddingService
from src.services.routine_service import RoutineService
from src.api.routes import api_bp, init_routes

logger = logging.getLogger(__name__)


def create_app():
    """
    Create and configure the Flask application.

    Returns:
        Flask: Configured Flask application instance.
    """
    # Configure logging
    logging.basicConfig(
        level=logging.INFO if settings.DEBUG else logging.WARNING,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    logger.info("Creating Flask application")

    # Create Flask app
    app = Flask(__name__)

    # Configure CORS
    if settings.CORS_ORIGINS == "*":
        CORS(app)
        logger.info("CORS enabled for all origins")
    else:
        origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
        CORS(app, resources={r"/api/*": {"origins": origins}})
        logger.info(f"CORS enabled for origins: {origins}")

    # Initialize database connections
    try:
        logger.info("Initializing database connections")
        chroma_client = get_chroma_client()
        openai_client = get_openai_client()
        collection = get_collection()
        logger.info("Database connections initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database connections: {e}")
        raise RuntimeError(f"Application startup failed: {e}") from e

    # Initialize layers
    repository = RoutineRepository(collection)
    embedding_service = EmbeddingService(openai_client, settings.EMBEDDING_MODEL)
    routine_service = RoutineService(repository, embedding_service)

    # Initialize routes with dependencies
    init_routes(routine_service)

    # Register blueprints
    app.register_blueprint(api_bp)

    logger.info("Flask application created successfully")

    return app
