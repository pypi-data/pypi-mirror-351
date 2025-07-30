import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf

def run_regression(data):
    df = pd.DataFrame(data)
    model = smf.glm(
        formula="WER ~ C(demographic_attribute) + covariate",
        data=df,
        family=sm.families.Poisson()
    ).fit()
    return model
