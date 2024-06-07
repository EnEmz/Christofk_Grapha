# utilities_download.py

import pandas as pd
from scipy.stats import linregress

from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, compile_met_pool_ratio_data, filter_and_order_isotopologue_data_by_met_class


def get_download_df_normalized_pool(df_pool, met_classes, normalization_selected, grouped_samples, met_ratio_selection):
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
    if df_iso['Compound'].isin(['group']).any():
        df_iso = df_iso[~df_iso['Compound'].isin(['group'])]
        df_iso = df_iso.reset_index(drop=True)

    if not met_classes:
         return None
    
    return df_iso


def get_download_df_lingress(df_var_data, df_pool, met_classes, normalization_selected, grouped_samples, met_ratio_selection):
    # Initialize an empty dataframe to store the results
    results_list = []

    # Get normalized and grouped pool data
    df_pool_normalized_grouped = get_download_df_normalized_pool(df_pool, met_classes, normalization_selected, grouped_samples, met_ratio_selection)
    
    # Flatten grouped_samples to get a list of all relevant sample columns
    all_samples = [sample for group_samples in grouped_samples.values() for sample in group_samples]

    for _, row in df_pool_normalized_grouped.iterrows():
        compound_name = row['Compound']
        met_values = row[all_samples].values
        
        df_var_data_filtered = df_var_data[all_samples]
        var_values = df_var_data_filtered.iloc[0].values

        # Perform linear regression
        slope, intercept, r_value, p_value, std_err = linregress(var_values, met_values)

        # Append the results to the results_list
        results_list.append({
            'Compound': compound_name,
            'slope': slope,
            'intercept': intercept,
            'r_value': r_value,
            'p_value (two-sided Wald Test)': p_value,
            'std_err': std_err
        })

    # Convert the results_list to a DataFrame
    results_df = pd.DataFrame(results_list)

    return results_df


def get_download_df_pool_pvalues():
    test = 2
    test2 = 2+2
    return None


def get_download_df_iso_pvalues():
    test = 2
    test2 = 2+2
    return None
