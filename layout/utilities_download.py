# utilities_download.py

import pandas as pd
from scipy.stats import linregress

from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, compile_met_pool_ratio_data, filter_and_order_isotopologue_data_by_met_class


def get_download_df_normalized_pool(df_pool, met_classes, normalization_selected, grouped_samples, met_ratio_selection):
    """
    Normalizes the given metabolomics data DataFrame and groups it based on selected metabolite classes.

    Parameters:
    ----------
    df_pool : pd.DataFrame
        A DataFrame containing raw metabolomics data.
    met_classes : list
        A list of metabolite classes to filter and group the data.
    normalization_selected : list
        A list of variables to be used for normalization.
    grouped_samples : dict
        A dictionary mapping group names to lists of sample column names.
    met_ratio_selection : list
        A list of metabolite ratios to be included if 'metabolite ratios' 
        is in the selected classes.

    Returns:
    -------
    pd.DataFrame
        A normalized and grouped DataFrame based on the specified metabolite classes and groups.
        Returns None if met_classes or grouped_samples is empty.
    """
    
    if not met_classes:
         return None

    if not grouped_samples:
        return None
    
    # Normalize the data based on the selected normalization variables
    df_pool_normalized = normalize_met_pool_data(df_pool, grouped_samples, normalization_selected)
    # Filter pool data based on selected metabolite classes
    df_pool_normalized_grouped = group_met_pool_data(df_pool_normalized, met_classes)

    # If metabolite ratios are in the selected sample class, then the metabolite ratio dataframe is
    # compiled and added to the end of the pool data dataframe
    if 'metabolite ratios' in met_classes and met_ratio_selection is not None:
        df_ratio = compile_met_pool_ratio_data(df_pool_normalized, met_ratio_selection)
        df_pool_normalized_grouped = pd.concat([df_pool_normalized_grouped, df_ratio])

    df_pool_normalized_grouped = df_pool_normalized_grouped.drop(columns=['pathway_class'])

    return df_pool_normalized_grouped


def get_download_df_iso(df_iso, met_classes):
    """
    Filters and prepares isotopologue data for download.

    Parameters:
    ----------
    df_iso : pd.DataFrame
        A DataFrame containing isotopologue data.
    met_classes : list
        A list of metabolite classes to filter the data.

    Returns:
    -------
    pd.DataFrame
        A filtered DataFrame based on the specified metabolite classes.
        Returns None if met_classes is empty.
    """

    if df_iso['Compound'].isin(['group']).any():
        df_iso = df_iso[~df_iso['Compound'].isin(['group'])]
        df_iso = df_iso.reset_index(drop=True)

    if not met_classes:
         return None
    
    return df_iso


def get_download_df_lingress(df_var_data, df_pool, met_classes, normalization_selected, grouped_samples, met_ratio_selection):
    """
    Performs linear regression analysis between metabolite data and an external variable for each compound
    and get it ready for downloading. 

    Parameters:
    ----------
    df_var_data : pd.DataFrame
        A DataFrame containing the external variable data.
    df_pool : pd.DataFrame
        A DataFrame containing normalized metabolomics data.
    met_classes : list
        A list of metabolite classes to filter and group the data.
    normalization_selected : list
        A list of variables to be used for normalization.
    grouped_samples : dict
        A dictionary mapping group names to lists of sample column names.
    met_ratio_selection : list
        A list of metabolite ratios to be included if 'metabolite ratios'
        is in the selected classes.

    Returns:
    -------
    pd.DataFrame
        A DataFrame containing the results of the linear regression analysis.
        Includes a 'ND Reason' column indicating reasons for compounds that were not analyzed.
    """

    # Initialize an empty dataframe to store the results
    results_list = []

    # Get normalized and grouped pool data
    df_pool_normalized_grouped = get_download_df_normalized_pool(df_pool, met_classes, normalization_selected, grouped_samples, met_ratio_selection)
    
    # Flatten grouped_samples to get a list of all relevant sample columns
    all_samples = [sample for group_samples in grouped_samples.values() for sample in group_samples]

    for _, row in df_pool_normalized_grouped.iterrows():
        compound_name = row['Compound']
        met_values = row[all_samples].astype(float)
        
        df_var_data_filtered = df_var_data[all_samples].astype(float)
        var_values = df_var_data_filtered.iloc[0]

        # Filter out NaN values and ensure equal lengths
        valid_indices = (~var_values.isna()) & (~met_values.isna())
        var_values_filtered = var_values[valid_indices]
        met_values_filtered = met_values[valid_indices]

        # Skip if not enough valid data points
        if len(var_values_filtered) < 2 or len(met_values_filtered) < 2:
            results_list.append({
                'Compound': compound_name,
                'ND Reason': 'Insufficient valid data points'
            })
            continue

        # Perform linear regression
        try:
            slope, intercept, r_value, p_value, std_err = linregress(var_values_filtered, met_values_filtered)
            results_list.append({
                'Compound': compound_name,
                'slope': slope,
                'intercept': intercept,
                'r_value': r_value,
                'p_value (two-sided Wald Test)': p_value,
                'std_err': std_err,
                'ND Reason': ''
            })
        except Exception as e:
            results_list.append({
                'Compound': compound_name,
                'ND Reason': f'Error during linregress: {e}'
            })

    # Convert the results_list to a DataFrame
    results_df = pd.DataFrame(results_list)

    return results_df