from scipy.stats import ttest_ind, f_oneway
from random import random

def get_boxplot_json(data, var, col, p_values):
    categories = data[var].unique().astype(str).tolist()
    # Data for Box Plot
    boxplot_data = []
    # 3. Box Plots (for original Violin Plots)
    # First, calculate p-values to sort the columns
    p_values = {}
    unique_values = data[var].unique()
    if len(unique_values) > 1:
        if len(unique_values) == 2:
            group1 = data[data[var] == unique_values[0]][col].dropna()
            group2 = data[data[var] == unique_values[1]][col].dropna()
            _, p_value = ttest_ind(group1, group2, equal_var=False)
        else:
            groups = [data[data[var] == value][col].dropna() for value in unique_values]
            _, p_value = f_oneway(*groups)
        p_values[col] = p_value

    sorted_columns = sorted(p_values, key=p_values.get)
    
    for col in sorted_columns:
        categories = data[var].unique().astype(str).tolist()
        # Data for Box Plot
        boxplot_data = []
        # Data for Scatter overlay
        scatter_data = []

        for i, category in enumerate(categories):
            cat_data = data[data[var] == category][col].dropna()
            if not cat_data.empty:
                # Boxplot needs 5-number summary: [low, q1, median, q3, high]
                stats = cat_data.describe()
                boxplot_data.append([i, stats['min'], stats['25%'], stats['50%'], stats['75%'], stats['max']])
                # Scatter points need jitter for better visibility
                for point in cat_data:
                    jitter = (random() - 0.5) * 0.4 # a small random value
                    scatter_data.append([i + jitter, point])

        p_val_text = f"(p-value: {p_values.get(col, float('nan')):.4f})"
        
        boxplot_json = {
            "title": {"text": f"{var} vs {col} {p_val_text}"},
            "legend": {"enabled": False},
            "xAxis": {"categories": categories, "title": {"text": var}},
            "yAxis": {"title": {"text": col}},
            "series": [
                {"name": "Summary", "type": "boxplot", "data": boxplot_data},
                {
                    "name": "Observations", "type": "scatter", "data": scatter_data,
                    "marker": {"radius": 1.5, "symbol": "circle"},
                    "tooltip": {"pointFormat": 'Value: {point.y}'}
                }
            ]
        }
        return boxplot_json