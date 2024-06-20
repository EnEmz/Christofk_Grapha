# utilities_download.py

import pandas as pd
import numpy as np
from scipy import stats
import warnings
from scipy.stats import linregress
from statsmodels.stats.multitest import multipletests

from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, compile_met_pool_ratio_data, filter_and_order_isotopologue_data_by_met_class
from layout.config import get_pvalue_label_from_value

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


def perform_two_sided_ttest_download(df, pvalue_comparisons, grouped_samples, variance_threshold=1e-5):
    df = df.copy()  # Make a copy of the DataFrame to avoid altering the original
    results = []
    all_p_values = []  # List to store all p-values from all comparisons
    pvalue_index_info = []  # List to store index information for placing p-values back correctly

    # Check if 'Compound' column is present
    if 'Compound' not in df.columns:
        print("Columns in the DataFrame:", df.columns)
        raise KeyError("The 'Compound' column is not found in the DataFrame.")
    
    
    for metabolite in df['Compound']:
        metabolite_results = {'Compound': metabolite}
        for index, column_pair in enumerate(pvalue_comparisons):
            group_list = list(grouped_samples.keys())
            
            # Access the group names using the indices provided by column_pair
            group1_key = group_list[column_pair[0]]
            group2_key = group_list[column_pair[1]]
            
            # Now use the keys to get the sample names from the grouped_samples dictionary
            group1_sample_names = grouped_samples[group1_key]
            group2_sample_names = grouped_samples[group2_key]
            
            # Extract the data for each group for the current metabolite and convert to numeric
            group1_data = pd.to_numeric(df.loc[df['Compound'] == metabolite, group1_sample_names].values.flatten(), errors='coerce')
            group2_data = pd.to_numeric(df.loc[df['Compound'] == metabolite, group2_sample_names].values.flatten(), errors='coerce')
            
            # Col name for the pvalue column with group names
            p_col_name = f'p | {group1_key} vs {group2_key}'

            # Handle cases with insufficient data with less than 2 datapoints in either group
            if len(group1_data) < 2 or len(group2_data) < 2:
                pvalue = np.nan
                metabolite_results[p_col_name] = "insufficient data"
            elif np.std(group1_data) < variance_threshold or np.std(group2_data) < variance_threshold:
                pvalue = np.nan
                metabolite_results[p_col_name] = "variance < 1E-08"
            elif np.all(group1_data == group2_data):
                pvalue = np.nan
                metabolite_results[p_col_name] = "identical data"
            else:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", category=RuntimeWarning)
                    pvalue = stats.ttest_ind(group1_data, 
                                             group2_data, 
                                             equal_var=False, 
                                             nan_policy='omit', 
                                             alternative='two-sided')[1]
                metabolite_results[p_col_name] = pvalue

            all_p_values.append(pvalue)
            pvalue_index_info.append((metabolite, f'{group1_key} vs {group2_key}'))
        
        results.append(metabolite_results)
    
    return pd.DataFrame(results), all_p_values, pvalue_index_info


def apply_pvalue_correction_download(pvalues, correction_method):
    """
    Applies a correction method to a list of p-values based on specified multiple testing correction method.
    Preserves the position of np.nan values.

    Parameters:
    ----------
    pvalues : list
        A list of p-values to be corrected, which may contain np.nan values.
    correction_method : str
        The correction method to be applied; options include 'bonferroni', 'fdr_bh', etc.

    Returns:
    -------
    array
        An array of corrected p-values with np.nan values in their original positions.
    """

    # Identify the indices of valid p-values (non-NaN)
    valid_indices = [i for i, p in enumerate(pvalues) if not np.isnan(p)]
    valid_pvalues = [pvalues[i] for i in valid_indices]

    # Apply correction only to valid p-values
    if valid_pvalues:
        corrected_pvalues = multipletests(valid_pvalues, alpha=0.05, method=correction_method)[1]

        # Re-integrate the corrected p-values into the original list, preserving NaN positions
        corrected_full = np.full_like(pvalues, np.nan, dtype=np.float64)  # Initialize array of NaNs with the same shape
        for idx, corr_pval in zip(valid_indices, corrected_pvalues):
            corrected_full[idx] = corr_pval
    else:
        corrected_full = np.full_like(pvalues, np.nan, dtype=np.float64)  # All values are NaN

    return corrected_full


def generate_corrected_pvalues_download(correction_method, all_p_values, pvalue_index_info):
    """
    Corrects p-values for specified comparisons across metabolites,
    compiling the results into a single DataFrame.

    Parameters:
    ----------
    correction_method : str
        The method used for p-value correction (e.g., 'bonferroni', 'fdr_bh').
    all_p_values : list
        List of all p-values calculated from the two-sided t-tests.
    pvalue_index_info : list
        List of tuples containing index information for placing p-values back correctly.

    Returns:
    -------
    pandas.DataFrame
        A DataFrame with one column per comparison, containing the corrected p-values.
    """
    # Get the p-value correction method label name
    pvalue_correction_label = get_pvalue_label_from_value(correction_method)
    
    # Initialize the corrected results DataFrame
    unique_compounds = list(set([info[0] for info in pvalue_index_info]))
    corrected_results_df = pd.DataFrame({'Compound': unique_compounds})

    # Correction of p-values if required
    if correction_method != 'none':
        valid_pvalues = [p for p in all_p_values if not np.isnan(p) and p <= 1]
        corrected_pvalues = apply_pvalue_correction_download(valid_pvalues, correction_method) if valid_pvalues else []

        # Create a DataFrame to hold corrected p-values
        comparison_columns = list(set([info[1].replace('p | ', '') for info in pvalue_index_info]))
        for col in comparison_columns:
            qvalue_col_name = f'q | {col} ({pvalue_correction_label})'
            corrected_results_df[qvalue_col_name] = np.nan

        correction_map = dict(zip([pvalue_index_info[i] for i in range(len(all_p_values)) if all_p_values[i] in valid_pvalues], corrected_pvalues))
        for index, (compound_key, col) in enumerate(pvalue_index_info):
            original_col_name = col.replace('p | ', '')  # Remove 'p | ' from column name
            qvalue_col_name = f'q | {original_col_name} ({pvalue_correction_label})'
            corrected_pvalue = correction_map.get((compound_key, col), np.nan)
            corrected_results_df.loc[corrected_results_df['Compound'] == compound_key, qvalue_col_name] = corrected_pvalue

    return corrected_results_df


def sort_pvalue_df_cols(df_pvalues, df_qvalues):
    # Ensure both DataFrames are sorted by the same key
    df_pvalues = df_pvalues.sort_values(by='Compound').reset_index(drop=True)
    df_qvalues = df_qvalues.sort_values(by='Compound').reset_index(drop=True)

    # Merge the DataFrames on 'Compound'
    df_merged = pd.merge(df_pvalues, df_qvalues, on='Compound')

    # Extract p-value and q-value columns
    p_columns = [col for col in df_pvalues.columns if col != 'Compound']
    q_columns = [col for col in df_qvalues.columns if col != 'Compound']

    # Create a mapping of comparison names to p and q columns
    comparison_pairs = {}
    for p_col in p_columns:
        comparison_name = p_col.split(' | ')[1]
        q_col = f'q | {comparison_name}'
        matching_q_col = next((col for col in q_columns if col.startswith(q_col)), None)
        if matching_q_col:
            comparison_pairs[comparison_name] = {
                'p_col': p_col,
                'q_col': matching_q_col
            }

    # Reorder columns to interleave p and q values
    ordered_columns = ['Compound']
    for comparison, cols in comparison_pairs.items():
        ordered_columns.append(cols['p_col'])
        ordered_columns.append(cols['q_col'])

    df_merged = df_merged[ordered_columns]

    return df_merged