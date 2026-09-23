"""API Flask para clasificación de sentimiento de texto en español."""
from flask import Flask, jsonify, request

from app.db import init_db, log_prediction
from app.model import ModelNotLoadedError, SentimentClassifier
from app.preprocessing import InvalidTextError, validate_text


def create_app(classifier: SentimentClassifier = None) -> Flask:
    """Application factory: crea y configura la instancia de Flask."""
    app = Flask(__name__)

    if classifier is None:
        classifier = SentimentClassifier()
        try:
            classifier.load()
        except FileNotFoundError:
            # El modelo se carga bajo demanda si no existe al iniciar
            # (por ejemplo, en el primer arranque antes de entrenar).
            pass

    app.classifier = classifier

    # Intento de inicializar la tabla de Postgres; no bloquea el arranque
    # si la base de datos aún no está disponible.
    init_db()

    @app.get("/health")
    def health():
        return jsonify(
            {
                "status": "ok",
                "model_loaded": app.classifier.is_loaded,
            }
        ), 200

    @app.post("/classify")
    def classify():
        payload = request.get_json(silent=True) or {}
        raw_text = payload.get("text")

        try:
            clean = validate_text(raw_text)
        except InvalidTextError as exc:
            return jsonify({"error": str(exc)}), 400

        try:
            result = app.classifier.predict(clean)
        except ModelNotLoadedError:
            return jsonify(
                {
                    "error": (
                        "El modelo no está cargado. Ejecuta "
                        "'python train/train_model.py' y reinicia la API."
                    )
                }
            ), 503

        log_prediction(clean, result["label"], result["confidence"])

        return jsonify(
            {
                "text": clean,
                "label": result["label"],
                "confidence": result["confidence"],
                "probabilities": result["probabilities"],
            }
        ), 200

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Recurso no encontrado"}), 404

    return app


app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
