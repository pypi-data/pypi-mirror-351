import statsmodels.api as sm
from .parse_formula import parse_formula
from .summary import summary
from .fit import fit

def step(formula, data, method='backward', criterion='aic', thresh=0.05, start=None, verbose=True):
    # Normalize method names
    method = method.lower()
    method_map = {
        'forward': 'forward', 'fwd': 'forward', 'f': 'forward',
        'backward': 'backward', 'bw': 'backward', 'b': 'backward', 'be': 'backward',
        'stepwise': 'stepwise', 'sw': 'stepwise', 's': 'stepwise'
    }
    if method not in method_map:
        raise ValueError("Invalid method. Use one of: 'forward', 'fwd', 'f', 'backward', 'bw', 'b', 'be', 'stepwise', 'sw', 's'")
    method = method_map[method]

    # Parse the formula to get initial predictors and response
    Y_name, X_names, Y_out, X_out = parse_formula(formula, data)
    
    if start:
        current_model = start
    else:
        if method == "backward":
            current_model = fit(formula, data)
        else:
            current_model = fit(Y_name + "~1", data)

    def get_criterion_value(model):
        if criterion == 'aic':
            return model.aic
        elif criterion == 'bic':
            return model.bic
        elif criterion == 'adjr2':
            return 1 - model.rsquared_adj  # Continue using this for minimization
        elif criterion == 'p-value':
            return max(model.pvalues[1:])  # Ignore intercept p-value
        else:
            raise ValueError("Criterion must be one of 'aic', 'bic', 'adjr2', 'p-value'")

    best_criterion = get_criterion_value(current_model)
    best_model = current_model
    real_adjr2 = current_model.rsquared_adj if criterion == 'adjr2' else None

    if verbose:
        if criterion == 'adjr2':
            print(f"Initial adjusted R-square value: {best_model.rsquared_adj}")
        else:
            print(f"Initial {criterion}: {best_criterion}")
           
        if verbose == 'summary':
            summary(current_model, out = "simple")

    def forward_selection():
        nonlocal best_model, best_criterion
        remaining_predictors = [p for p in X_names if p not in best_model.model.exog_names]
        for predictor in remaining_predictors:
            X_new = sm.add_constant(data[best_model.model.exog_names[1:]].join(data[[predictor]])).rename(columns={'const': 'Intercept'})
            new_model = sm.OLS(Y_out, X_new).fit()
            new_criterion = get_criterion_value(new_model)
            if new_criterion < best_criterion:
                best_model = new_model
                best_criterion = new_criterion
                if verbose:
                    if verbose == 'summary':
                        summary(new_model, out = "simple")
                    else:
                        if criterion == 'adjr2':
                            print(f"Real adjusted R-square value: {best_model.rsquared_adj}")
                        else:
                            print(f"Best {criterion}: {best_criterion}")

    def backward_elimination():
        nonlocal best_model, best_criterion
        for predictor in best_model.model.exog_names[1:]:
            X_new = sm.add_constant(data[[p for p in best_model.model.exog_names[1:] if p != predictor]]).rename(columns={'const': 'Intercept'})
            new_model = sm.OLS(Y_out, X_new).fit()
            new_criterion = get_criterion_value(new_model)
            if new_criterion < best_criterion:
                best_model = new_model
                best_criterion = new_criterion
                if verbose:
                    if verbose == 'summary':
                        summary(new_model, out = "simple")
                    else:
                        if criterion == 'adjr2':
                            print(f"Real adjusted R-square value: {best_model.rsquared_adj}")
                        else:
                            print(f"Best {criterion}: {best_criterion}")

    change = True
    while change:
        change = False
        if method in ['forward', 'stepwise']:
            current_criterion = best_criterion
            forward_selection()
            if best_criterion < current_criterion:
                if criterion == 'adjr2':
                    real_adjr2 = best_model.rsquared_adj  # Update real adjR²
                change = True
        
        if method in ['backward', 'stepwise']:
            current_criterion = best_criterion
            backward_elimination()
            if best_criterion < current_criterion:
                if criterion == 'adjr2':
                    real_adjr2 = best_model.rsquared_adj  # Update real adjR²
                change = True

    return best_model
