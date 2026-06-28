def test_api_matrix_success(client):
    payload = {
        "matrix": [["2", "1"], ["1", "3"]],
        "operation": "inverse"
    }
    response = client.post('/api/matrix', json=payload)
    
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "success"
    assert data["operation"] == "inverse"
    assert "result" in data

def test_api_matrix_zero_det(client):
    payload = {
        "matrix": [["1", "1"], ["1", "1"]],
        "operation": "inverse"
    }
    response = client.post('/api/matrix', json=payload)
    
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data
    assert "Determinant is 0" in data["error"]

def test_api_matrix_validation_error(client):
    # Missing 'operation'
    payload = {
        "matrix": [["2", "1"], ["1", "3"]]
    }
    response = client.post('/api/matrix', json=payload)
    
    # Smorest returns 422 for schema validation errors
    assert response.status_code == 422
    data = response.get_json()
    assert "errors" in data
