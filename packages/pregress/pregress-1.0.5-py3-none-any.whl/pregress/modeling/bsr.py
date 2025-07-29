import numpy as np
import pandas as pd
import statsmodels.api as sm
from itertools import combinations
from .parse_formula import parse_formula  # Ensure correct import based on your setup

def bsr(formula, data, max_var=8, sortby="adjr2"):
    """
    Perform Best Subset Regression based on the given formula, data, and parameters.

    Parameters:
    formula (str): A string representing the regression formula (e.g., "y ~ x1 + x2 + x3").
    data (pd.DataFrame): A pandas DataFrame containing the data.
    max_var (int): The maximum number of predictor variables to consider in subsets.
    sortby (str): The metric by which to sort the results (default is "adjr2").

    Returns:
    pd.DataFrame: A DataFrame containing the results for all subsets of predictors, sorted by the specified metric.
    """
    
    # Parse the formula to get initial predictors and response
    y_var, x_vars, y, X = parse_formula(formula + "+0", data)
    
    def get_subsets(X, max_size):
        subsets = []
        for size in range(1, max_size+1):
            for subset in combinations(X.columns, size):
                subsets.append(subset)
        return subsets
    
    def fit_linear_regression(X, y, features):
        # Subset the predictors and add a constant term
        X_subset = X[list(features)]
        X_subset = sm.add_constant(X_subset)
        
        # Fit the OLS regression model
        model = sm.OLS(y, X_subset).fit()
        
        # Calculate the desired metrics
        r2 = model.rsquared
        adj_r2 = model.rsquared_adj
        aic = model.aic
        bic = model.bic
        n = len(y)
        p = len(features) + 1
        mse = np.sum(model.resid**2) / (n-p)
        cp = (np.sum(model.resid**2) / mse) - (n - 2*p)
        rmse = np.sqrt(mse)
        mae = np.mean(np.abs(model.resid))
        
        return r2, adj_r2, aic, bic, cp, rmse, mae
    
    # Generate all possible subsets of features up to max_var size
    subsets = get_subsets(X, max_size=max_var)
    
    # Fit linear regression models to each subset of features and record metrics
    results = []
    for subset in subsets:
        r2, adj_r2, aic, bic, cp, rmse, mae = fit_linear_regression(X, y, subset)
        results.append((subset, r2, adj_r2, aic, bic, cp, rmse, mae))
    
    # Convert results to a pandas DataFrame
    results_df = pd.DataFrame(results, columns=['Features', 'R-squared', 'Adj. R-squared', 'AIC', 'BIC', "Mallow's Cp", 'RMSE', 'MAE'])
    
    # Define a dictionary to map sortby parameter to DataFrame columns
    sortby_column = {
        "r2": "R-squared",
        "adjr2": "Adj. R-squared",
        "aic": "AIC",
        "bic": "BIC",
        "cp": "Mallow's Cp",
        "rmse": "RMSE",
        "mae": "MAE"
    }
    
    # Raise an error if an invalid sortby value is provided
    if sortby not in sortby_column:
        raise ValueError("Invalid sortby value. Must be one of 'r2', 'adjr2', 'aic', 'bic', 'cp', 'rmse', 'mae'.")
    
    # Sort results by the specified metric
    results_df = results_df.sort_values(by=sortby_column[sortby], ascending=(sortby not in ["r2", "adjr2"]))
    
    return results_df
