def test_health_endpoint_returns_200(client):
    response = client.get("/health")
    assert response.status_code == 200


def test_health_endpoint_reports_model_loaded(client):
    response = client.get("/health")
    data = response.get_json()
    assert data["status"] == "ok"
    assert data["model_loaded"] is True


def test_classify_endpoint_returns_200_for_valid_text(client):
    response = client.post("/classify", json={"text": "me encantó, excelente"})
    assert response.status_code == 200


def test_classify_endpoint_returns_label_and_confidence(client):
    response = client.post("/classify", json={"text": "excelente producto, muy feliz"})
    data = response.get_json()
    assert data["label"] in {"positive", "negative"}
    assert "confidence" in data
    assert "probabilities" in data


def test_classify_endpoint_rejects_empty_text(client):
    response = client.post("/classify", json={"text": ""})
    assert response.status_code == 400


def test_classify_endpoint_rejects_missing_text_field(client):
    response = client.post("/classify", json={})
    assert response.status_code == 400


def test_classify_endpoint_rejects_non_json_body(client):
    response = client.post("/classify", data="no soy json")
    assert response.status_code == 400


def test_unknown_route_returns_404(client):
    response = client.get("/ruta-que-no-existe")
    assert response.status_code == 404
