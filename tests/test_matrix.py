import pytest
from engines.matrix import process_matrix

def test_process_matrix_inverse_valid():
    data = {
        "matrix": [["2", "1"], ["1", "3"]],
        "operation": "inverse",
        "mode": "symbolic"
    }
    result = process_matrix(data)
    
    assert result["status"] == "success"
    assert result["operation"] == "inverse"
    assert result["result"] == [["3/5", "-1/5"], ["-1/5", "2/5"]]
    assert len(result["steps"]) == 2

def test_process_matrix_inverse_zero_det():
    data = {
        "matrix": [["1", "1"], ["1", "1"]],
        "operation": "inverse"
    }
    with pytest.raises(ValueError, match="El determinante es 0"):
        process_matrix(data)

def test_process_matrix_determinant_valid():
    data = {
        "matrix": [["2", "1"], ["1", "3"]],
        "operation": "determinant"
    }
    result = process_matrix(data)
    
    assert result["status"] == "success"
    assert result["operation"] == "determinant"
    assert result["result"] == [["5"]]
    assert len(result["steps"]) == 1

def test_process_matrix_rref_valid():
    data = {
        "matrix": [["1", "2", "3"], ["4", "5", "6"]],
        "operation": "rref"
    }
    result = process_matrix(data)
    
    assert result["status"] == "success"
    assert result["operation"] == "rref"
    assert len(result["result"]) > 0
    assert len(result["steps"]) == 1

def test_process_matrix_missing_data():
    data = {"operation": "inverse"}
    with pytest.raises(ValueError, match="Matrix data is missing"):
        process_matrix(data)

def test_process_matrix_invalid_operation():
    data = {
        "matrix": [["1", "0"], ["0", "1"]],
        "operation": "unknown"
    }
    with pytest.raises(ValueError, match="Unsupported operation"):
        process_matrix(data)
