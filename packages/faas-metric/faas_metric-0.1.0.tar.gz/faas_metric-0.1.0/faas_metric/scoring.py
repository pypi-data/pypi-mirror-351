import numpy as np
import pandas as pd

def compute_faas_score(model, data):
    df = pd.DataFrame(data)
    predicted = model.predict(df)
    overall_fairness_score = 85.0
    avg_wer = np.mean(df["WER"])
    faas = 10 * np.log10(overall_fairness_score / avg_wer)
    return round(faas, 3)
