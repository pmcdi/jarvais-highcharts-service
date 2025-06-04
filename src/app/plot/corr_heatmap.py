import pandas as pd
import numpy as np
from typing import Dict, List

def get_corr_heatmap_json(
    corr: pd.DataFrame,
    title: str = "Correlation Matrix"
) -> Dict:
    """
    Converts a correlation DataFrame into a Highcharts heatmap JSON object.

    Args:
        corr (pd.DataFrame): Correlation matrix to visualize.
        title (str): Title for the chart.

    Returns:
        Dict: A dictionary representing a Highcharts JSON configuration.
    """
    # Highcharts heatmap data is a list of [x, y, value] triplets
    # We only want the lower triangle, so we iterate and check indices
    labels = corr.columns.tolist()
    data = []
    for y, row_label in enumerate(labels):
        for x, col_label in enumerate(labels):
            if x < y: # Only add points in the lower triangle
                value = corr.loc[row_label, col_label]
                data.append([x, y, round(value, 2)])

    highcharts_config = {
        "chart": {
            "type": 'heatmap',
            "marginTop": 40,
            "marginBottom": 80,
            "plotBorderWidth": 1
        },
        "title": {
            "text": title
        },
        "xAxis": {
            "categories": labels,
            "title": None
        },
        "yAxis": {
            "categories": labels,
            "title": None
        },
        "colorAxis": {
            "min": -1,
            "max": 1,
            "stops": [
                [0, '#3060cf'], # blue for -1
                [0.5, '#fffbbc'], # yellow for 0
                [1, '#c4463a'] # red for 1
            ]
        },
        "legend": {
            "align": 'right',
            "layout": 'vertical',
            "margin": 0,
            "verticalAlign": 'top',
            "y": 25,
            "symbolHeight": 280
        },
        "series": [{
            "name": 'Correlation',
            "borderWidth": 1,
            "data": data,
            "dataLabels": {
                "enabled": True,
                "color": '#000000',
                "format": '{point.value:.2f}'
            }
        }]
    }
    return highcharts_config

# --- Example Usage ---
# df = pd.DataFrame({'A': [1,2,3], 'B': [3,1,2], 'C': [2,3,1]})
# corr_matrix = df.corr(method='spearman')
# hc_json = get_corr_heatmap_json(corr_matrix)
# print(hc_json)