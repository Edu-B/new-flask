# 3rd party imports
from flask import Blueprint, current_app, jsonify

# Project imports
from app.config import settings
from app.helpers.postgres import DatabaseConnection


curs = DatabaseConnection().return_connection().cursor()

core = Blueprint("core", settings.app_name)


@core.route("/status", methods=["GET"])
def status():
    """
    Status health check endpoint.
    """
    version = current_app.config.get("VERSION")
    result = {"version": version, "message": "pong"}
    return jsonify(result=result, code=200)
