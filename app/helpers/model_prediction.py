import numpy as np
import tensorflow as tf


class PrediccionRutinas:
    def __init__(self, model_path):
        self.model = None
        self.load_custom_model(model_path)

    @staticmethod
    def load_custom_model(model_path):
        try:
            model = tf.keras.models.load_model(model_path)
            print("Modelo cargado exitosamente.")
        except Exception as e:
            print(f"Error al cargar el modelo: {e}")
        return model

    def predict(self, model_path, input_data):
        """Load the trained model and make predictions."""
        model = self.load_custom_model("./model/modelo_recomendador.h5")
        return model
