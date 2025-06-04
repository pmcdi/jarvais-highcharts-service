import pandas as pd
import numpy as np
from typing import Dict, List

def get_multiplot_json_list(
    data: pd.DataFrame,
    umap_data: np.ndarray, # Expecting a numpy array like the original
    var: str,
    continuous_columns: list,
) -> List[Dict]:
    """
    Generates a list of Highcharts JSON objects for the multi-plot visualization.
    1. Pie Chart for the categorical variable distribution.
    2. Scatter Plot for the UMAP colored by the variable.
    3. Box Plots (as a substitute for Violin Plots) for each continuous variable.

    Args:
        data (pd.DataFrame): The input DataFrame.
        umap_data (np.ndarray): 2D numpy array with UMAP coordinates.
        var (str): The categorical variable to analyze.
        continuous_columns (list): List of continuous columns for box plots.

    Returns:
        List[Dict]: A list of Highcharts JSON configurations.
    """
    all_charts = []

    pie_chart = get_pie_chart_json(data, var)
    scatter_plot = get_scatter_plot_json(umap_data, var)
    for col in continuous_columns:
        box_plot = get_boxplot_json(data, var, col, p_values)
        all_charts.append(box_plot)

    return all_charts