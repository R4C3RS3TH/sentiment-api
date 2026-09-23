import pytest

from app.model import ModelNotLoadedError, SentimentClassifier


def test_model_loads_without_error(classifier):
    assert classifier.is_loaded is True


def test_predict_returns_expected_keys(classifier):
    result = classifier.predict("me encantó este producto, excelente calidad")
    assert set(result.keys()) == {"label", "confidence", "probabilities"}


def test_predict_positive_text_is_classified_positive(classifier):
    result = classifier.predict("excelente producto, lo recomiendo totalmente")
    assert result["label"] == "positive"


def test_predict_negative_text_is_classified_negative(classifier):
    result = classifier.predict("pésimo servicio, el producto llegó roto")
    assert result["label"] == "negative"


def test_predict_confidence_is_between_zero_and_one(classifier):
    result = classifier.predict("una experiencia normal")
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_raises_when_model_not_loaded():
    unloaded_classifier = SentimentClassifier()
    with pytest.raises(ModelNotLoadedError):
        unloaded_classifier.predict("cualquier texto")


def test_predict_raises_file_not_found_for_invalid_path():
    bad_classifier = SentimentClassifier(model_path="/tmp/no-existe-modelo.pkl")
    with pytest.raises(FileNotFoundError):
        bad_classifier.load()
