import numpy as np
import statsmodels.api as sm
from scipy.stats import chi2

def ncv_test(model, out=True):
    """
    Mimic R's car::ncvTest() — test for non-constant variance
    by regressing squared residuals on fitted values (with intercept).

    Args:
        model: A fitted statsmodels OLS regression model.
        out (bool): If True, prints results.

    Returns:
        float: The p-value of the test.
    """
    import numpy as np
    import statsmodels.api as sm
    from scipy.stats import chi2

    resid_sq = model.resid ** 2
    fitted = model.fittedvalues

    # Use intercept from original model, avoid double constant
    intercept = np.ones_like(fitted)
    aux_X = np.column_stack((intercept, fitted))

    aux_model = sm.OLS(resid_sq, aux_X).fit()
    r_squared = aux_model.rsquared
    n = len(resid_sq)

    test_stat = n * r_squared
    p_value = 1 - chi2.cdf(test_stat, df=1)

    if out:
        print("Nonconstant Variance Test")
        print("========================================")
        print(f"Auxiliary R-squared : {r_squared:.4f}")
        print(f"Chi-squared(1) Stat: {test_stat:.4f}")
        print(f"P-value             : {p_value:.4g}")
        print(f"Result              : {'Heteroscedastic (p < 0.05)' if p_value < 0.05 else 'Homoscedastic (p ≥ 0.05)'}")
        print("========================================")

    return
