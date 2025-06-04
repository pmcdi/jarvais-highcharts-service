from itertools import combinations
import pandas as pd
from typing import Dict, List

def get_pairplot_json(
    data: pd.DataFrame,
    continuous_columns: list,
    target_variable: str = None,
    n_keep: int = 10
) -> List[Dict]:
    """
    Generates a list of Highcharts scatter plot JSON objects, one for each
    pair of columns.

    Args:
        data (pd.DataFrame): Input DataFrame.
        continuous_columns (list): List of continuous variable names.
        target_variable (str, optional): Variable to use as a hue. Defaults to None.
        n_keep (int, optional): Max number of columns to include.

    Returns:
        List[Dict]: A list of dictionaries, each a Highcharts scatter plot config.
    """
    # This logic to select columns remains the same
    if len(continuous_columns) > n_keep:
        spearman_corr = data[continuous_columns].corr(method="spearman")
        corr_pairs = spearman_corr.abs().unstack().sort_values(ascending=False).drop_duplicates()
        top_pairs = corr_pairs[corr_pairs < 1].nlargest(5)
        columns_to_plot = list({index for pair in top_pairs.index for index in pair})
    else:
        columns_to_plot = continuous_columns.copy()

    json_outputs = []

    for col_x, col_y in combinations(columns_to_plot, 2):
        series = []
        if target_variable:
            # Create one series per category in the hue variable
            for name, group in data.groupby(target_variable):
                series.append({
                    "name": str(name),
                    "type": "scatter",
                    "data": group[[col_x, col_y]].values.tolist()
                })
        else:
            # Create a single series if no hue
            series.append({
                "name": "Data",
                "type": "scatter",
                "data": data[[col_x, col_y]].values.tolist()
            })

        highcharts_config = {
            "title": {"text": f'{col_x} vs. {col_y}'},
            "xAxis": {"title": {"text": col_x}},
            "yAxis": {"title": {"text": col_y}},
            "series": series,
            "plotOptions": {
                "scatter": {
                    "marker": {"radius": 2.5, "symbol": "circle"},
                    "tooltip": {"headerFormat": "", "pointFormat": f"<b>{col_x}:</b> {{point.x}}<br/><b>{col_y}:</b> {{point.y}}"}
                }
            }
        }
        json_outputs.append(highcharts_config)

    return json_outputs