# 3rd party imports
from flask import Blueprint, current_app, jsonify, request

# Project imports
from app.config import settings
from app.helpers.postgres import DatabaseConnection


curs = DatabaseConnection().return_connection().cursor()

database = Blueprint("database", settings.app_name)


@database.route("/personas", methods=["GET"])
def get_personas():
    """
    Get all personas from database.
    """
    curs.execute("SELECT * FROM personas")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/ejercicios", methods=["GET"])
def get_ejercicios():
    """
    Get all ejercicios from database.
    """
    curs.execute("SELECT * FROM ejercicios")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/ejercicios_recomendados", methods=["GET"])
def get_rutinas():
    """
    Get all ejercicios from database.
    """
    curs.execute("SELECT * FROM ejercicios_recomendados")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/enfermedades", methods=["GET"])
def get_enfermedades():
    """
    Get all enfermedades from database.
    """
    curs.execute("SELECT * FROM enfermedades")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/personas_enfermedades", methods=["GET"])
def get_personas_enfermedades():
    """
    Get all enfermedades from database.
    """
    curs.execute("SELECT * FROM personas_enfermedades")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/pesos_recomendados", methods=["GET"])
def get_pesos_recomendados():
    """
    Get all pesos_recomendados from database.
    """
    curs.execute("SELECT * FROM pesos_recomendados")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/tipos_ejercicios", methods=["GET"])
def get_tipos_ejercicios():
    """
    Get all tipos_ejercicios from database.
    """
    curs.execute("SELECT * FROM tipos_ejercicios")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/tipos_ejercicios_enfermedades", methods=["GET"])
def get_tipos_ejercicios_enfermedades():
    """
    Get all tipos_ejercicios_enfermedades from database.
    """
    curs.execute("SELECT * FROM tipos_ejercicios_enfermedades")
    rows = curs.fetchall()
    results = [dict(row) for row in rows]
    return jsonify(result=results, code=200)


@database.route("/predict", methods=["POST"])
def predict():
    """
    predict endpoint that base on a given data predict the result
    """
    data = request.json
    print(data)

    _result = {
        "code": 200,
        "result": {
            "ejercicio": "sentadillas",
            "repeticiones": 10,
            "series": 3,
            "peso_min": 20,
            "peso_max": 30,
        },
    }
    return jsonify(_result)
