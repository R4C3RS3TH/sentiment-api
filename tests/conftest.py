import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import create_app  # noqa: E402
from app.model import SentimentClassifier  # noqa: E402


@pytest.fixture(scope="session")
def classifier():
    """Instancia del clasificador cargado una sola vez para toda la sesión de tests."""
    clf = SentimentClassifier()
    clf.load()
    return clf


@pytest.fixture()
def client(classifier):
    """Cliente de pruebas de Flask, con el modelo ya cargado."""
    app = create_app(classifier=classifier)
    app.testing = True
    with app.test_client() as test_client:
        yield test_client
