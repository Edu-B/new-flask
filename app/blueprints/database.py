# 3rd party imports
from flask import Blueprint, current_app, jsonify, request
import time
import numpy as np
import pandas as pd
import tensorflow as tf
import random as rn

# Project imports
from app.config import settings
from app.helpers.postgres import DatabaseConnection
from app.helpers.model_prediction import PrediccionRutinas

predictor = PrediccionRutinas.load_custom_model("./model/modelo_recomendador.h5")


curs = DatabaseConnection().return_connection().cursor()

database = Blueprint("database", settings.app_name)

df_ej = pd.read_csv("ejercicios.csv")
ejercicios = df_ej["nombre_ejercicio"].unique().tolist()


def codificar_ejercicio(ejercicios, y_ejercicio):
    ejercicio_idx = np.array([ejercicios.index(e) for e in y_ejercicio])
    y_onehot = tf.keras.utils.to_categorical(ejercicio_idx, num_classes=len(ejercicios))
    return y_onehot


def predecir_lista(
    model, ejercicios, all_diseases, paciente, enfermedades_paciente, top_n=5
):
    # Convertir enfermedades del paciente a vector
    disease_to_idx = {d: i for i, d in enumerate(all_diseases)}
    disease_vector = np.zeros((len(all_diseases),), dtype=int)
    for d in enfermedades_paciente:
        if d in disease_to_idx:
            disease_vector[disease_to_idx[d]] = 1

    arr = np.array(
        [paciente["edad"], paciente["peso"], paciente["estatura"], paciente["genero"]]
    )
    arr = np.hstack([arr, disease_vector])
    arr = arr.reshape(1, -1)
    pred = model.predict(arr)[0]
    top_indices = np.argsort(pred)[::-1][:top_n]
    resultados = [(ejercicios[i], float(pred[i])) for i in top_indices]
    return resultados


def cargar_data_usuarios(filepath="data_usuarios.csv"):
    df = pd.read_csv(filepath)
    # Extraer todas las enfermedades del dataset
    all_diseases = set()
    for val in df["enfermedades"]:
        if pd.isna(val) or val.strip() == "":
            continue
        for d in val.split(";"):
            d = d.strip()
            if d != "":
                all_diseases.add(d)
    all_diseases = list(all_diseases)
    all_diseases.sort()

    # Crear un map enfermedad -> indice
    disease_to_idx = {d: i for i, d in enumerate(all_diseases)}

    # Crear una matriz de enfermedades one-hot
    disease_matrix = np.zeros((len(df), len(all_diseases)), dtype=int)
    for i, val in enumerate(df["enfermedades"]):
        if pd.isna(val) or val.strip() == "":
            continue
        for d in val.split(";"):
            d = d.strip()
            if d in disease_to_idx:
                disease_matrix[i, disease_to_idx[d]] = 1

    # Features: edad, peso, estatura, genero + enfermedades one-hot
    X = np.hstack([df[["edad", "peso", "estatura", "genero"]].values, disease_matrix])

    return df, X, all_diseases


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
    df_data, X, all_diseases = cargar_data_usuarios("data_usuarios.csv")
    paciente_ejemplo = {"edad": 60, "peso": 95.0, "estatura": 1.75, "genero": 1}
    enfermedades_paciente = ["Asma", "Osteoporosis"]  # Por ejemplo

    top_ej = predecir_lista(
        predictor,
        ejercicios,
        all_diseases,
        paciente_ejemplo,
        enfermedades_paciente,
        top_n=5,
    )

    print(top_ej)

    peso_min = 0
    peso_max = 0
    repeticiones = 0
    series = 0
    # create rule based on enfermedades_paciente to get the random reps and series and peso_min and peso_max
    for enfermedad in enfermedades_paciente:
        if enfermedad == "Asma":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Osteoporosis":
            repeticiones += rn.randint(3, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 3)
            peso_max += rn.randint(3, 8)
        elif enfermedad == "Diabetes":
            repeticiones += rn.randint(4, 9)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 9)
        elif enfermedad == "Hipertensión":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Artritis":
            repeticiones += rn.randint(3, 7)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 3)
            peso_max += rn.randint(3, 7)
        elif enfermedad == "Cardiopatía":
            repeticiones += rn.randint(4, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 8)
        elif enfermedad == "Obesidad":
            repeticiones += rn.randint(6, 12)
            series += rn.randint(2, 4)
            peso_min += rn.randint(5, 10)
            peso_max += rn.randint(10, 15)
        elif enfermedad == "Ansiedad":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Depresión":
            repeticiones += rn.randint(4, 9)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 9)
        elif enfermedad == "Colesterol alto":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "EPOC":
            repeticiones += rn.randint(3, 7)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 3)
            peso_max += rn.randint(3, 7)
        elif enfermedad == "Insuficiencia renal":
            repeticiones += rn.randint(4, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 8)
        elif enfermedad == "Hepatitis":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Parkinson":
            repeticiones += rn.randint(3, 7)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 3)
            peso_max += rn.randint(3, 7)
        elif enfermedad == "Alzheimer":
            repeticiones += rn.randint(4, 9)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 9)
        elif enfermedad == "Esclerosis múltiple":
            repeticiones += rn.randint(3, 7)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 3)
            peso_max += rn.randint(3, 7)
        elif enfermedad == "Fibromialgia":
            repeticiones += rn.randint(4, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 8)
        elif enfermedad == "Lupus":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Esquizofrenia":
            repeticiones += rn.randint(4, 9)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 9)
        elif enfermedad == "Trastorno bipolar":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Anemia":
            repeticiones += rn.randint(4, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 8)
        elif enfermedad == "Hipotiroidismo":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Hipertiroidismo":
            repeticiones += rn.randint(4, 9)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 9)
        elif enfermedad == "Gastritis":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Úlcera péptica":
            repeticiones += rn.randint(4, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 4)
            peso_max += rn.randint(4, 8)
        elif enfermedad == "Reflujo gastroesofágico":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        if enfermedad == "Asma":
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)
        elif enfermedad == "Osteoporosis":
            repeticiones += rn.randint(3, 8)
            series += rn.randint(1, 2)
            peso_min += rn.randint(0, 3)
            peso_max += rn.randint(3, 8)

        else:
            repeticiones += rn.randint(5, 10)
            series += rn.randint(1, 3)
            peso_min += rn.randint(0, 5)
            peso_max += rn.randint(5, 10)

    # merge the results with the top_ej list to get the final result
    res = []
    for exercise in top_ej:

        res.append(
            {
                "ejercicio": exercise[0],
                "repeticiones": repeticiones,
                "series": series,
                "peso_min": peso_min,
                "peso_max": peso_max,
            }
        )

    _result = {"code": 200, "result": res}
    return jsonify(_result)
