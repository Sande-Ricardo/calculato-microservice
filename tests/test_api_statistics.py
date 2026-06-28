def test_api_descriptive_success(client):
    payload = {
        "dataset": [10.0, 20.0, 30.0],
        "sample": True
    }
    response = client.post('/api/stats/descriptive', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["data"]["count"] == 3

def test_api_descriptive_empty_error(client):
    payload = {
        "dataset": []
    }
    response = client.post('/api/stats/descriptive', json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["status"] == "error"
    assert "empty" in data["message"]

def test_api_descriptive_math_error(client):
    payload = {
        "dataset": [10.0],
        "sample": True
    }
    response = client.post('/api/stats/descriptive', json=payload)
    assert response.status_code == 422
    data = response.get_json()
    assert data["status"] == "error"
    assert "variance" in data["message"]

def test_api_probability_success(client):
    payload = {
        "distribution": "normal",
        "parameters": {"mu": 10, "sigma": 2},
        "query_type": "cumulative_less",
        "query_value": 12.0
    }
    response = client.post('/api/stats/probability', json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["distribution"] == "normal"

def test_api_probability_invalid_params(client):
    payload = {
        "distribution": "binomial",
        "parameters": {"n": 5, "p": 1.5},
        "query_type": "exact",
        "query_value": 2
    }
    response = client.post('/api/stats/probability', json=payload)
    assert response.status_code == 422
    data = response.get_json()
    assert data["status"] == "error"
    assert "Probability" in data["message"]
