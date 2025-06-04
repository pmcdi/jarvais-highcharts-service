import pandas as pd
from typing import Dict, List

def create_series_from_data(data: list[dict], x_key: str, y_key: str, hue_key: str) -> list[dict]:
    """
    Mimics seaborn's hue functionality by grouping flat data into a Highcharts series format.

    Args:
        data: A list of dictionaries (like a pandas DataFrame.to_dict('records')).
        x_key: The dictionary key for the x-value.
        y_key: The dictionary key for the y-value.
        hue_key: The dictionary key to group by for color (category).

    Returns:
        A list of dictionaries in a Highcharts-compatible series format.
    """
    groups = {}
    for item in data:
        category = item[hue_key]
        # If we haven't seen this category yet, initialize its dictionary
        if category not in groups:
            groups[category] = {
                'name': category,
                'data': []
            }
        # Append the [x, y] point to the correct category's data list
        point = [item[x_key], item[y_key]]
        groups[category]['data'].append(point)

    # Return the values of the dictionary as a list, which is the final series
    return list(groups.values())

# --- Example Usage ---
# Sample data (same as the JavaScript example)
sample_data = [
    {'city': 'New York', 'temperature': 5, 'rainfall': 80},
    {'city': 'London', 'temperature': 6, 'rainfall': 95},
    {'city': 'New York', 'temperature': 10, 'rainfall': 65},
    {'city': 'Tokyo', 'temperature': 12, 'rainfall': 150},
    {'city': 'London', 'temperature': 11, 'rainfall': 70},
    {'city': 'Tokyo', 'temperature': 15, 'rainfall': 120},
    {'city': 'New York', 'temperature': 18, 'rainfall': 50},
    {'city': 'London', 'temperature': 16, 'rainfall': 60},
    {'city': 'Tokyo', 'temperature': 20, 'rainfall': 110}
]

# Generate the series
series_data = create_series_from_data(
    data=sample_data,
    x_key='temperature',
    y_key='rainfall',
    hue_key='city'
)

# Print the result (using pprint for nice formatting)
import pprint
pprint.pprint(series_data)

# def get_scatterplot_json(
#     x: List,
#     y: List,
#     hue: List,
#     title: str = "Scatter Plot"
# ) -> Dict:
#     """
#     Converts a DataFrame into a Highcharts scatter plot JSON object.
#     """

#      # 2. UMAP Scatter Plot JSON
#     scatter_series_data = []
#     for name, group in data.groupby(var):
#         indices = group.index
#         scatter_series_data.append({
#             "name": str(name),
#             "type": "scatter",
#             "data": umap_data[indices].tolist() # Get points corresponding to the group
#         })
#     umap_scatter_json = {
#         "title": {"text": f'UMAP of Continuous Variables with {var}'},
#         "xAxis": {"title": {"text": "UMAP 1"}},
#         "yAxis": {"title": {"text": "UMAP 2"}},
#         "series": scatter_series_data
#     }
#     return umap_scatter_json