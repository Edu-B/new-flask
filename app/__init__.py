# Native imports
import logging
import os.path

# 3rd party imports
import requests
from flask import Flask, request
from flask_cors import CORS

# Project imports
from app.config import Config, settings
from app.helpers.logger import setup_logger
from app.helpers.postgres import DatabaseConnection


def create_app() -> Flask:
    """
    Create Flask server app.
    """
    logger = logging.getLogger(settings.app_name)
    setup_logger(
        logger,
        settings.app_env,
        settings.app_name,
        settings.pt_host,
        settings.pt_port,
    )

    # Setup Flask application
    app = Flask(settings.app_name)
    app.config.from_object(Config)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db = DatabaseConnection(
        settings.db_host,
        settings.db_port,
        settings.db_user,
        settings.db_password,
        settings.db_name,
    )

    # Setup request logger
    @app.before_request
    def log_request():
        path = request.path
        method = request.method
        body = (
            request.get_json() if request.content_type == "application/json" else None
        )
        args = request.args

        # Ignore health check endpoint
        if path != "/api/status":
            logger.info({"path": path, "method": method, "body": body, "args": args})

    # Setup blueprints
    from .blueprints import core_blueprint

    app.register_blueprint(core_blueprint, url_prefix="/api")

    return app
