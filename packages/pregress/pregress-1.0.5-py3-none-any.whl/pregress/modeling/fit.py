from .parse_formula import parse_formula
import statsmodels.api as sm
import pandas as pd

def fit(formula: str, data: pd.DataFrame = None, method: str = "ols", dummies: bool = True):
    """
    Fits a statistical model based on a specified formula and data.

    Parameters:
    - formula (str): A string representing the statistical formula (e.g., 'Y ~ X1 + X2 - X3').
    - data (DataFrame, optional): The dataset containing the variables specified in the formula.
    - method (str, optional): The method used for fitting the model. Defaults to 'ols' (Ordinary Least Squares).
                              Supported methods: 'ols' for linear regression, 'logistic' for logistic regression.
    - dummies (bool, optional): A boolean indicating whether to automatically create dummy variables for categorical
                                predictors. Defaults to True.

    Returns:
    - model (statsmodels object): The fitted model object, which can be used for further analysis, such as
                                  making predictions or evaluating model performance.

    Raises:
    - ValueError: If the input data is empty or the specified variables are not found in the data.
    - NotImplementedError: If an unsupported method is specified.

    Notes:
    - The function currently supports OLS (Ordinary Least Squares) and logistic regression.
      Additional methods like random forest or k-nearest neighbors could be added as needed.
    - If 'dummies' is set to True, categorical variables in the predictors are converted into dummy/indicator
      variables, with the first category dropped to avoid multicollinearity. Binary variables (True/False) are
      converted to numeric (0/1) values.
    """

    def process_dummies(X_out):
        """Helper function to handle dummy variables and binary conversions."""
        X_out = pd.get_dummies(X_out, drop_first=True)

        # Convert binary variables (True/False) to numeric (0/1)
        binary_columns = X_out.select_dtypes(include=['bool']).columns
        X_out[binary_columns] = X_out[binary_columns].astype(int)
        return X_out

    def check_response_and_convert(Y_out):
        """Convert categorical response variable to dummies if necessary."""
        if not pd.api.types.is_numeric_dtype(Y_out):
            Y_out = pd.get_dummies(Y_out, drop_first=True)
            if Y_out.shape[1] > 1:
                raise ValueError("Response variable was converted to multiple columns, indicating it is multi-class. "
                                 "This function currently supports binary response variables only.")
        return Y_out

    Y_name, X_names, Y_out, X_out = parse_formula(formula, data)

    # Ensure Y_out is a Series and retains its name
    if isinstance(Y_out, (pd.Series, pd.DataFrame)):
        Y_out.name = Y_name  # Retain the response variable's name
    else:
        # Convert numpy array to pandas Series and set name
        Y_out = pd.Series(Y_out, name=Y_name)

    if X_out.empty:
        raise ValueError("The input data is empty or the specified variables are not found in the data.")

    if dummies:
        X_out = process_dummies(X_out)

    if method.lower() == "ols":
        model = sm.OLS(Y_out, X_out).fit()

    elif method.lower() == "logistic":
        # Process the response variable to ensure it is numeric or binary
        Y_out = check_response_and_convert(Y_out)
        model = sm.GLM(Y_out, X_out, family=sm.families.Binomial()).fit()

    else:
        raise NotImplementedError(f"Method '{method}' is not implemented. Supported methods: 'ols', 'logistic'.")

    return model

