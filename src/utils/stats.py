import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from scipy import stats
from scipy.stats import mannwhitneyu, kruskal


def identify_variable_types(data: pd.DataFrame, 
                          categorical_threshold: int = 10,
                          min_observations: int = 5) -> Tuple[List[str], List[str]]:
    """
    Automatically identify categorical and continuous variables in a DataFrame.
    
    Args:
        data (pd.DataFrame): Input DataFrame
        categorical_threshold (int): Max unique values to consider a variable categorical
        min_observations (int): Minimum observations per group for valid testing
        
    Returns:
        Tuple[List[str], List[str]]: Lists of categorical and continuous variable names
    """
    categorical_vars = []
    continuous_vars = []
    
    for col in data.columns:
        # Skip if too many missing values
        if data[col].isnull().sum() / len(data) > 0.5:
            continue
            
        # Check if column is numeric
        if pd.api.types.is_numeric_dtype(data[col]):
            # If few unique values, consider categorical
            if data[col].nunique() <= categorical_threshold:
                # Check if each group has minimum observations
                value_counts = data[col].value_counts()
                if all(count >= min_observations for count in value_counts.values):
                    categorical_vars.append(col)
                else:
                    continuous_vars.append(col)
            else:
                continuous_vars.append(col)
        else:
            # Non-numeric columns are categorical if they have reasonable groups
            value_counts = data[col].value_counts()
            if (len(value_counts) <= categorical_threshold and 
                all(count >= min_observations for count in value_counts.values)):
                categorical_vars.append(col)
    
    return categorical_vars, continuous_vars


def calculate_effect_size(data: pd.DataFrame, 
                         categorical_var: str, 
                         continuous_var: str) -> float:
    """
    Calculate effect size (eta-squared) for categorical-continuous relationship.
    
    Args:
        data (pd.DataFrame): Input data
        categorical_var (str): Name of categorical variable
        continuous_var (str): Name of continuous variable
        
    Returns:
        float: Effect size (eta-squared)
    """
    # Remove missing values
    clean_data = data[[categorical_var, continuous_var]].dropna()
    
    if len(clean_data) < 3:
        return 0.0
    
    # Calculate between-group and within-group variance
    groups = [group[continuous_var].values for name, group in clean_data.groupby(categorical_var)]
    
    # Overall mean
    overall_mean = clean_data[continuous_var].mean()
    
    # Between-group sum of squares
    ss_between = sum(len(group) * (group.mean() - overall_mean)**2 for group in groups)
    
    # Total sum of squares
    ss_total = sum((clean_data[continuous_var] - overall_mean)**2)
    
    # Eta-squared (effect size)
    if ss_total == 0:
        return 0.0
    
    eta_squared = ss_between / ss_total
    return eta_squared


def perform_statistical_test(data: pd.DataFrame, 
                           categorical_var: str, 
                           continuous_var: str) -> Dict:
    """
    Perform appropriate statistical test for categorical-continuous pair.
    
    Args:
        data (pd.DataFrame): Input data
        categorical_var (str): Name of categorical variable
        continuous_var (str): Name of continuous variable
        
    Returns:
        Dict: Test results including p-value, test statistic, and effect size
    """
    # Remove missing values
    clean_data = data[[categorical_var, continuous_var]].dropna()
    
    if len(clean_data) < 3:
        return {
            'test_type': 'insufficient_data',
            'p_value': 1.0,
            'test_statistic': 0.0,
            'effect_size': 0.0,
            'n_groups': 0,
            'total_n': len(clean_data)
        }
    
    # Group data by categorical variable
    groups = [group[continuous_var].values for name, group in clean_data.groupby(categorical_var)]
    groups = [group for group in groups if len(group) > 0]  # Remove empty groups
    
    n_groups = len(groups)
    
    if n_groups < 2:
        return {
            'test_type': 'insufficient_groups',
            'p_value': 1.0,
            'test_statistic': 0.0,
            'effect_size': 0.0,
            'n_groups': n_groups,
            'total_n': len(clean_data)
        }
    
    # Calculate effect size
    effect_size = calculate_effect_size(clean_data, categorical_var, continuous_var)
    
    try:
        if n_groups == 2:
            # Mann-Whitney U test for 2 groups
            stat, p_value = mannwhitneyu(groups[0], groups[1], alternative='two-sided')
            test_type = 'mann_whitney_u'
        else:
            # Kruskal-Wallis test for 3+ groups
            stat, p_value = kruskal(*groups)
            test_type = 'kruskal_wallis'
            
        return {
            'test_type': test_type,
            'p_value': p_value,
            'test_statistic': stat,
            'effect_size': effect_size,
            'n_groups': n_groups,
            'total_n': len(clean_data)
        }
        
    except Exception as e:
        return {
            'test_type': 'error',
            'p_value': 1.0,
            'test_statistic': 0.0,
            'effect_size': 0.0,
            'n_groups': n_groups,
            'total_n': len(clean_data),
            'error': str(e)
        }


def find_significant_categorical_continuous_pairs(data: pd.DataFrame,
                                                categorical_vars: List[str] = None,
                                                continuous_vars: List[str] = None,
                                                alpha: float = 0.05,
                                                min_effect_size: float = 0.01) -> pd.DataFrame:
    """
    Find categorical-continuous variable pairs with significant statistical relationships.
    
    Args:
        data (pd.DataFrame): Input DataFrame
        categorical_vars (List[str], optional): List of categorical variables. If None, auto-detect.
        continuous_vars (List[str], optional): List of continuous variables. If None, auto-detect.
        alpha (float): Significance level (default: 0.05)
        min_effect_size (float): Minimum effect size to consider meaningful (default: 0.01)
        
    Returns:
        pd.DataFrame: Results sorted by statistical significance, with columns:
            - categorical_var: Name of categorical variable
            - continuous_var: Name of continuous variable
            - test_type: Type of statistical test used
            - p_value: P-value from statistical test
            - test_statistic: Test statistic value
            - effect_size: Effect size (eta-squared)
            - n_groups: Number of groups in categorical variable
            - total_n: Total number of observations
            - significant: Boolean indicating if p < alpha
            - meaningful: Boolean indicating if effect size >= min_effect_size
    """
    # Auto-detect variable types if not provided
    if categorical_vars is None or continuous_vars is None:
        detected_cat, detected_cont = identify_variable_types(data)
        categorical_vars = categorical_vars or detected_cat
        continuous_vars = continuous_vars or detected_cont
    
    results = []
    
    # Test all categorical-continuous pairs
    for cat_var in categorical_vars:
        for cont_var in continuous_vars:
            if cat_var != cont_var:  # Skip if same variable
                test_result = perform_statistical_test(data, cat_var, cont_var)
                
                result_row = {
                    'categorical_var': cat_var,
                    'continuous_var': cont_var,
                    'test_type': test_result['test_type'],
                    'p_value': test_result['p_value'],
                    'test_statistic': test_result['test_statistic'],
                    'effect_size': test_result['effect_size'],
                    'n_groups': test_result['n_groups'],
                    'total_n': test_result['total_n'],
                    'significant': test_result['p_value'] < alpha,
                    'meaningful': test_result['effect_size'] >= min_effect_size
                }
                
                # Add error information if present
                if 'error' in test_result:
                    result_row['error'] = test_result['error']
                
                results.append(result_row)
    
    # Convert to DataFrame and sort by significance
    results_df = pd.DataFrame(results)
    
    if len(results_df) == 0:
        return pd.DataFrame()
    
    # Sort by p-value (ascending) and then by effect size (descending)
    results_df = results_df.sort_values(['p_value', 'effect_size'], 
                                      ascending=[True, False]).reset_index(drop=True)
    
    return results_df


def get_top_significant_pairs(data: pd.DataFrame,
                            top_n: int = 10,
                            categorical_vars: List[str] = None,
                            continuous_vars: List[str] = None,
                            alpha: float = 0.05,
                            min_effect_size: float = 0.01) -> pd.DataFrame:
    """
    Get the top N most significant categorical-continuous variable pairs.
    
    Args:
        data (pd.DataFrame): Input DataFrame
        top_n (int): Number of top pairs to return
        categorical_vars (List[str], optional): List of categorical variables
        continuous_vars (List[str], optional): List of continuous variables
        alpha (float): Significance level
        min_effect_size (float): Minimum effect size to consider meaningful
        
    Returns:
        pd.DataFrame: Top N significant pairs
    """
    all_results = find_significant_categorical_continuous_pairs(
        data, categorical_vars, continuous_vars, alpha, min_effect_size
    )
    
    if len(all_results) == 0:
        return pd.DataFrame()
    
    # Filter for significant and meaningful results
    significant_results = all_results[
        (all_results['significant'] == True) & 
        (all_results['meaningful'] == True)
    ]
    
    # If no significant results, return top results anyway
    if len(significant_results) == 0:
        return all_results.head(top_n)
    
    return significant_results.head(top_n) 