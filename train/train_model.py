"""
Script de entrenamiento del modelo de clasificación de sentimiento.

Entrena un pipeline TF-IDF + Regresión Logística sobre el dataset
`data/reviews.csv` y guarda el modelo entrenado en `models/sentiment_model.pkl`.

Uso:
    python train/train_model.py
"""
import os
import sys

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "reviews.csv")
MODEL_DIR = os.path.join(BASE_DIR, "models")
MODEL_PATH = os.path.join(MODEL_DIR, "sentiment_model.pkl")


def build_pipeline() -> Pipeline:
    """Crea el pipeline de preprocesamiento + modelo."""
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    lowercase=True,
                    strip_accents="unicode",
                    ngram_range=(1, 2),
                ),
            ),
            ("clf", LogisticRegression(max_iter=1000)),
        ]
    )


def train(data_path: str = DATA_PATH, model_path: str = MODEL_PATH) -> Pipeline:
    """Entrena el modelo y lo persiste en disco. Retorna el pipeline entrenado."""
    df = pd.read_csv(data_path)
    if "text" not in df.columns or "label" not in df.columns:
        raise ValueError("El dataset debe tener las columnas 'text' y 'label'")

    x_train, x_test, y_train, y_test = train_test_split(
        df["text"], df["label"], test_size=0.2, random_state=42, stratify=df["label"]
    )

    pipeline = build_pipeline()
    pipeline.fit(x_train, y_train)

    accuracy = pipeline.score(x_test, y_test)
    print(f"Accuracy en set de prueba: {accuracy:.2f}")

    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    joblib.dump(pipeline, model_path)
    print(f"Modelo guardado en: {model_path}")

    return pipeline


if __name__ == "__main__":
    try:
        train()
    except Exception as exc:  # noqa: BLE001
        print(f"Error entrenando el modelo: {exc}", file=sys.stderr)
        sys.exit(1)
