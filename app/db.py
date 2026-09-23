"""Registro de predicciones en PostgreSQL (monitoreo básico del modelo).

Si la base de datos no está disponible (por ejemplo, corriendo los tests
o en modo local sin Docker), el logging se omite silenciosamente para no
romper la API: el registro en base de datos es un extra de monitoreo,
no un requisito para servir predicciones.
"""
import os

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://sentiment_user:sentiment_pass@localhost:5432/sentiment_db",
)

_CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS predictions (
    id SERIAL PRIMARY KEY,
    input_text TEXT NOT NULL,
    predicted_label VARCHAR(50) NOT NULL,
    confidence FLOAT NOT NULL,
    created_at TIMESTAMP DEFAULT NOW()
);
"""

_INSERT_SQL = """
INSERT INTO predictions (input_text, predicted_label, confidence)
VALUES (%s, %s, %s);
"""


def get_connection():
    """Crea y retorna una nueva conexión a PostgreSQL usando psycopg2."""
    import psycopg2

    return psycopg2.connect(DATABASE_URL)


def init_db() -> bool:
    """Crea la tabla de predicciones si no existe. Retorna True si tuvo éxito."""
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(_CREATE_TABLE_SQL)
        conn.close()
        return True
    except Exception:  # noqa: BLE001
        return False


def log_prediction(input_text: str, predicted_label: str, confidence: float) -> bool:
    """Guarda una predicción en la base de datos. Retorna True si tuvo éxito."""
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(_INSERT_SQL, (input_text, predicted_label, confidence))
        conn.close()
        return True
    except Exception:  # noqa: BLE001
        return False
