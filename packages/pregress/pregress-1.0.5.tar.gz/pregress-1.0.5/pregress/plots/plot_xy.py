from pregress.modeling.parse_formula import parse_formula
from pregress.modeling.predict import predict
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def plot_xy(formula, data=None, model=None, pcolor="blue", lcolor="red", xlab=None, ylab=None, main=None, psize=50, subplot=None, **kwargs):
    """
    Generates and prints a plot of the regression model fit using a specified formula and data.
    It supports plotting for models with one predictor variable, including potentially nonlinear relationships.
    The function utilizes Seaborn for plotting the scatter plot and Matplotlib for the regression line.

    Args:
        formula (str): Formula to define the model (Y ~ X).
        data (DataFrame, optional): Data frame containing the data.
        model (list, optional): List of fitted statsmodels models or a single fitted model to use for predictions.
        pcolor (str or list, optional): Color of the points in the scatter plot. Can be a single color or a list of colors.
        lcolor (str or list, optional): Color of the regression line(s). Can be a single color or a list of colors corresponding to the models.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        main (str, optional): Title for the plot.
        psize (int, optional): Size of the points in the scatter plot. Default is 50.
        subplot (tuple, optional): Subplot configuration. Default is None.
        **kwargs: Additional keyword arguments for customization.

    Returns:
        None. The function creates and shows a plot.
    """
    
    # Parse the formula and ensure the formula includes an intercept
    formula = formula + "+0"
    Y_name, X_names, Y_out, X_out = parse_formula(formula, data)

    # Check the number of predictor variables in the model
    if X_out.shape[1] > 1:
        print("Only one predictor variable can be plotted.")
        return

    # If subplot is specified, create subplot
    if subplot is not None:
        if subplot[2] == 1:  # Check if it's the first subplot
            plt.figure(figsize=(15, 5))  # Specify figure size for better visibility
        plt.subplot(*subplot)


    # Check if pcolor is a list or an array
    if isinstance(pcolor, (list, np.ndarray)):
        unique_colors = np.unique(pcolor)
        for i, color in enumerate(unique_colors):
            sns.scatterplot(x=X_out[pcolor == color].values.flatten(), y=Y_out[pcolor == color], color=color, s=psize, label=kwargs.get('legend_labels', [None]*len(unique_colors))[i])
    else:
        sns.scatterplot(x=X_out.values.flatten(), y=Y_out, color=pcolor, s=psize)



    # If model is a single model, convert it to a list
    if not isinstance(model, list):
        model = [model]

    # If lcolor is a single color, convert it to a list
    if not isinstance(lcolor, list):
        lcolor = [lcolor] * len(model)

    # Plot each model's predictions
    for idx, (mdl, color) in enumerate(zip(model, lcolor)):
        if isinstance(mdl, str) and mdl.lower() in ["line", "l"]:
            sns.regplot(x=X_out, y=Y_out, scatter_kws={"color": pcolor, "s": psize}, line_kws={"color": color}, ci=None)
        elif mdl is not None:
            # Generate predictions across the range of X values
            X_range = np.linspace(X_out.min(), X_out.max(), 100).reshape(-1, 1)

            # Handle both cases where the predictor might be "X" or X_names[0]
            if "X" in mdl.model.exog_names:
                X_pred = pd.DataFrame({"X": X_range.flatten()})
            else:
                X_pred = pd.DataFrame({X_names[0]: X_range.flatten()})

            Y_pred = predict(mdl, X_pred)

            # Plot the regression line using matplotlib
            plt.plot(X_range, Y_pred, color=color, lw=2, label=kwargs.get('legend_labels', [None]*len(model))[idx])

    # Set labels for the x and y axes
    plt.xlabel(xlab if xlab is not None else X_names[0])
    plt.ylabel(ylab if ylab is not None else Y_name)

    # Set the plot title if provided
    if main is not None:
        plt.title(main)

    # Add legend if provided in kwargs
    if 'legend_labels' in kwargs:
        plt.legend(kwargs['legend_labels'])

    # Show the plot if subplot is not specified or if it is the last subplot
    if subplot is None or subplot[1] == subplot[2]:
        plt.show()
        plt.clf()
        plt.close()




