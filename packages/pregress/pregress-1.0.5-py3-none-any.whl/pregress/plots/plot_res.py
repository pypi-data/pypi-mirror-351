import matplotlib.pyplot as plt
import numpy as np
import scipy.stats as stats


def plot_res(model, main="Residual Plot", xlab="Fitted values", ylab="Residuals", subplot=None):
    """
    Plots the residuals of a fitted statsmodels regression model.

    Args:
        model (statsmodels.regression.linear_model.RegressionResultsWrapper): A fitted statsmodels regression model.
        main (str, optional): Title for the plot.
        xlab (str, optional): Label for the x-axis.
        ylab (str, optional): Label for the y-axis.
        subplot (tuple, optional): A tuple specifying the subplot grid (nrows, ncols, index). If None, a new figure is created.

    Returns:
        None. Displays a residual plot.
    """

    # Calculate residuals
    residuals = model.resid

    # Calculate fitted values
    fitted = model.predict()

    # If a subplot is specified, create the subplot; otherwise, create a new figure
    if subplot:
        plt.subplot(*subplot)
    else:
        plt.figure()

    # Create the residual plot
    plt.scatter(fitted, residuals, color='blue')
    plt.axhline(0, color='red', linestyle='--')  # Adds a horizontal line at zero

    # Setting the title and labels using provided arguments
    plt.xlabel(xlab)
    plt.ylabel(ylab)
    plt.title(main)

    # Show the plot only if no subplot is provided
    if subplot is None:
        plt.show()
        plt.clf()
        plt.close()
