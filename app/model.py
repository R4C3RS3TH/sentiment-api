"""Carga del modelo entrenado y lógica de predicción."""
import os

import joblib

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_MODEL_PATH = os.path.join(BASE_DIR, "models", "sentiment_model.pkl")


class ModelNotLoadedError(RuntimeError):
    """Se lanza cuando se intenta predecir sin haber cargado un modelo."""


class SentimentClassifier:
    """Envuelve el pipeline de scikit-learn entrenado para clasificar texto."""

    def __init__(self, model_path: str = DEFAULT_MODEL_PATH):
        self.model_path = model_path
        self._pipeline = None

    def load(self) -> None:
        """Carga el modelo serializado desde disco."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(
                f"No se encontró el modelo en {self.model_path}. "
                "Ejecuta 'python train/train_model.py' primero."
            )
        self._pipeline = joblib.load(self.model_path)

    @property
    def is_loaded(self) -> bool:
        return self._pipeline is not None

    def predict(self, text: str) -> dict:
        """Predice el sentimiento de un texto y retorna la etiqueta + probabilidad."""
        if not self.is_loaded:
            raise ModelNotLoadedError("El modelo no ha sido cargado. Llama a load() primero.")

        label = self._pipeline.predict([text])[0]
        probabilities = self._pipeline.predict_proba([text])[0]
        classes = self._pipeline.classes_
        confidence = float(max(probabilities))
        proba_by_class = {
            str(cls): float(prob) for cls, prob in zip(classes, probabilities)
        }

        return {
            "label": str(label),
            "confidence": round(confidence, 4),
            "probabilities": proba_by_class,
        }
