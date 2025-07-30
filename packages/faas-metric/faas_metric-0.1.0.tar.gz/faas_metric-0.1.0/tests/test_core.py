from faas_metric import compute_faas

def test_compute_faas():
    data = [
        {"WER": 0.15, "demographic_attribute": "A", "covariate": 1},
        {"WER": 0.30, "demographic_attribute": "B", "covariate": 0},
        {"WER": 0.25, "demographic_attribute": "B", "covariate": 1},
    ]
    score = compute_faas(data)
    assert isinstance(score, float)
