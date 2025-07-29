from .extract_variable import extract_variable
from .apply_transformation import apply_transformation
from .handle_included_vars import handle_included_vars
from .environment import EvalEnvironment
import pandas as pd

def parse_formula(formula, data=None):
    """
    Parses a statistical formula and applies specified transformations to dataframe columns.

    Args:
        formula (str): A string formula, e.g., 'Y ~ X1 + X2 - X3' or 'Y ~ . - X1'
        data (pd.DataFrame): Dataframe containing the data for variables mentioned in the formula.

    Returns:
        tuple: A tuple containing a dictionary of transformed predictors, list of predictor names,
               the transformed response series, and a Dataframe of transformed predictors.
    """

    formula = formula.replace(' ', '')
    response, predictors = formula.split('~')

    # Extract and transform the response variable.
    response_trans, untransformed_Y = extract_variable(response)

    # Attempt to resolve variables from data, if not present try to get from globals.
    if data is None:
        data = pd.DataFrame()

    # Look for untransformed_Y in global variables (not working).
    if untransformed_Y not in data.columns:
        globals_dict = globals()
        if untransformed_Y in globals_dict:
            data[untransformed_Y] = globals_dict[untransformed_Y]
        else:
            raise KeyError(f"Variable '{untransformed_Y}' not found in DataFrame or global scope.")

    Y = apply_transformation(data[untransformed_Y], response_trans)

    # If predictors == 1 => "Y ~ 1" => null model
    if predictors == '1':
        X = pd.DataFrame(index=data.index)
        include_intercept = True
    else:
        # Check for intercept exclusion
        if '+0' in predictors or '-1' in predictors:
            include_intercept = False
            predictors = predictors.replace('+0', '').replace('-1', '').strip()
        else:
            include_intercept = True

        # Initialize lists to manage included and excluded variables.
        included_vars = []
        excluded_vars = []

        # Split the predictors on '+' and handle each segment separately.
        predictor_parts = predictors.split('+')
        for part in predictor_parts:
            if '-' in part:
                # If a '-' is present, split on '-' and manage exclusions.
                subparts = part.split('-')
                included_vars.append(subparts[0].strip())
                excluded_vars.extend([sub.strip() for sub in subparts[1:]])
            else:
                included_vars.append(part.strip())

        # Here we attempt to extract the variables from the data given the included/excluded
        X_vars = handle_included_vars(data, included_vars, excluded_vars, untransformed_Y)
        X = pd.DataFrame(X_vars)

    if include_intercept:
        X['Intercept'] = 1
        cols = ['Intercept'] + [col for col in X.columns if col != 'Intercept']
        X = X[cols]

    return response, X.columns.tolist(), Y, X
