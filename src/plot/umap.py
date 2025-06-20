import pandas as pd
from typing import Dict, List
from umap import UMAP

def get_umap_json(umap_data: pd.DataFrame, 
                  hue: pd.Series) -> dict:
    """
    Generates a 2D UMAP projection of the specified continuous columns and returns a Highcharts JSON configuration.

    Args:
        data (pd.DataFrame): The input DataFrame containing the data to be visualized.
        continuous_columns (list): A list of column names corresponding to continuous variables 
            to be included in the UMAP projection.

    Returns:
        dict: A Highcharts configuration dictionary for rendering the UMAP scatter plot.
    """
    # Create Highcharts configuration
    highcharts_config = {
        "chart": {
            "type": "scatter",
            "zoomType": "xy"
        },
        "title": {
            "text": "UMAP of Continuous Variables"
        },
        "xAxis": {
            "title": {
                "text": "UMAP Component 1"
            }
        },
        "yAxis": {
            "title": {
                "text": "UMAP Component 2"
            }
        },
        "plotOptions": {
            "scatter": {
                "marker": {
                    "fillOpacity": 0.7,
                    "radius": 4,
                    "states": {
                        "hover": {
                            "enabled": True,
                            "lineColor": "rgb(100,100,100)"
                        }
                    }
                },
                "tooltip": {
                    "headerFormat": "<b>{series.name}</b><br>",
                    "pointFormat": "Component 1: {point.x:.3f}<br>Component 2: {point.y:.3f}"
                }
            }
        }
    }

    umap_subsets = {}
    series_list = []
    if hue:
        unique_categories = hue.unique()
        for category in unique_categories:
            mask = hue == category
            umap_subsets[category] = umap_data[mask]
        
        # Add legend
        highcharts_config["legend"] = {"enabled": True, "title": {"text": "Value"}}

        # Update tooltip to include hue information
        highcharts_config["plotOptions"]["scatter"]["tooltip"]["pointFormat"] = (
            f"{{series.name}}<br>"
            "Component 1: {point.x:.3f}<br>Component 2: {point.y:.3f}"
        )

    else:
        umap_subsets = {"Data Points": umap_data}
        
        # Disable legend if no hue is provided
        highcharts_config["legend"] = {"enabled": False}    

    # add data to series
    for category, umap_subset in umap_subsets.items():
        series_list.append({
            "name": str(category),
            "data": [{"x": float(point[0]), "y": float(point[1])} for point in umap_subset],
            "marker": {
                "fillOpacity": 0.7,
                "radius": 4
            }
        })
        
        
    highcharts_config["series"] = series_list

    return highcharts_config
