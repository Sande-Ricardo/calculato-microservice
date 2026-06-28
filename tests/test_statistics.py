import pytest
from engines.statistics import process_descriptive_stats, process_probability

def test_descriptive_stats_valid():
    data = {
        "dataset": [10.0, 12.0, 15.0, 18.0, 20.0],
        "sample": True
    }
    res = process_descriptive_stats(data)
    assert res["status"] == "success"
    assert res["data"]["count"] == 5
    assert res["data"]["central_tendency"]["mean"] == 15.0
    assert "variance" in res["data"]["dispersion"]
    assert "histogram" in res["data"]["chart_data"]

def test_descriptive_stats_empty():
    with pytest.raises(ValueError, match="The 'dataset' array cannot be empty."):
        process_descriptive_stats({"dataset": []})

def test_descriptive_stats_sample_size_1():
    with pytest.raises(ValueError, match="Sample variance requires at least 2 data points."):
        process_descriptive_stats({"dataset": [10.0], "sample": True})

def test_descriptive_stats_population_size_1():
    res = process_descriptive_stats({"dataset": [10.0], "sample": False})
    assert res["status"] == "success"
    assert res["data"]["dispersion"]["variance"] == 0.0

def test_probability_normal_cumulative_less():
    data = {
        "distribution": "normal",
        "parameters": {"mu": 0, "sigma": 1},
        "query_type": "cumulative_less",
        "query_value": 1.96
    }
    res = process_probability(data)
    assert res["status"] == "success"
    assert res["distribution"] == "normal"
    assert round(res["calculation"]["probability"], 3) == 0.975
    assert len(res["chart_data"]["curve_points"]) == 100
    assert res["chart_data"]["shaded_region"]["x_max"] == 1.96

def test_probability_binomial_exact():
    data = {
        "distribution": "binomial",
        "parameters": {"n": 10, "p": 0.5},
        "query_type": "exact",
        "query_value": 5
    }
    res = process_probability(data)
    assert res["status"] == "success"
    assert res["distribution"] == "binomial"
    assert round(res["calculation"]["probability"], 3) == 0.246
    assert len(res["chart_data"]["curve_points"]) == 11

def test_probability_poisson_between():
    data = {
        "distribution": "poisson",
        "parameters": {"lambda": 4},
        "query_type": "between",
        "query_value": [2, 4]
    }
    res = process_probability(data)
    assert res["status"] == "success"
    assert res["distribution"] == "poisson"
    assert "probability" in res["calculation"]
    assert res["chart_data"]["shaded_region"]["x_min"] == 2
    assert res["chart_data"]["shaded_region"]["x_max"] == 4

def test_probability_invalid_params():
    data = {
        "distribution": "normal",
        "parameters": {"mu": 0, "sigma": -1},
        "query_type": "cumulative_less",
        "query_value": 1.96
    }
    with pytest.raises(ValueError, match="Standard deviation"):
        process_probability(data)
