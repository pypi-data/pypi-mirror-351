def compute_faas(data):
    from .regression import run_regression
    from .scoring import compute_faas_score

    model = run_regression(data)
    return compute_faas_score(model, data)
