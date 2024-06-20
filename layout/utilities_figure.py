# utilities_figure.py

import plotly.graph_objects as go 
import numpy as np
import pandas as pd
from scipy import stats
from scipy.stats import linregress
from statsmodels.stats.multitest import multipletests

import os
from datetime import datetime
import time

from layout.config import iso_color_palette
from layout.config import df_met_group_list


def generate_single_met_pool_figure(df_metabolite, grouped_samples, settings):
    """
    Generates a Plotly figure for displaying pool sizes of a specific metabolite.

    The function takes a pandas DataFrame representing a metabolite row, where the 
    first column must be metabolite names, and creates a box plot visualization with 
    customization options based on the user's settings.

    Parameters:
    - df_metabolite (DataFrame): DataFrame containing metabolite data.
    - grouped_samples (dict): Dictionary containing grouped sample data.
    - settings (dict): User-defined settings for customizing the appearance of the plot.

    Returns:
    - plotly.graph_objs._figure.Figure: A Plotly figure object ready to be displayed.
    """
    
    data = []  # Container for the plot data
    
    factor_mult = 1000  # Multiplication factor for y-values
    
    # Loop through each sample group, creating box plots for each
    for sample_group, cols_in_group in grouped_samples.items():
        
        sample_group_cols = np.where(np.isin(df_metabolite.columns, cols_in_group))[0]
        
        # Scaling y-values
        y_values = df_metabolite.iloc[0, sample_group_cols] * factor_mult
        
        # Counting zero values
        zero_values_count = (y_values == 0).sum()
        
        # Creating hover text for each box plot
        hover_text = df_metabolite.columns[sample_group_cols].to_list()
        not_detected_annotation = f"<br>{zero_values_count} nd" if zero_values_count > 0 else ""
        
        # Setting box color based on user settings
        box_color = settings['pool_group_color'] if settings['pool_group_same_color'] else settings['pool_ind_group_colors'].get(sample_group, 'grey')
        
        # Appending box plot configurations to the data list
        data.append(go.Box(
            y=y_values, 
            name=sample_group + not_detected_annotation, 
            line=dict(color=box_color),
            marker=dict(
                color=settings['pool_datapoint_color'],
                size=settings['pool_datapoint_size']
            ),
            boxpoints='all' if settings['pool_datapoints_visible'] else False,
            width=settings['boxwidth'],
            jitter=settings['boxgap'],
            pointpos=0.0,
            text=hover_text,  
            hoverinfo='text',
            hoverlabel=dict(
                font_size=settings['font_size'],
                font_family=settings['font_selector']
            ),
            boxmean=True
        ))
    
    # Creating a Plotly figure
    fig = go.Figure(data=data)
    fig.update_layout(
        yaxis_title_text='Peak Area',
        yaxis_title_font=dict(
            family=settings['font_selector'],
            size=settings['font_size']
        ),
        yaxis=dict(
            zeroline=True,
            gridwidth=1,
            zerolinewidth=1,
            exponentformat='e',
            showexponent='all',
            tickfont=dict(
                family=settings['font_selector'],
                size=settings['font_size']
            )
        ),
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=settings['width'],
        height=settings['height']
    )
    
    # Updating font settings for x-axis
    fig.update_xaxes(
        tickfont=dict(
            family=settings['font_selector'],
            size=settings['font_size']
        ),
        range=[-0.5, len(grouped_samples) - 0.5]
    )
    
    return fig


def update_metabolomics_figure_layout(fig, array_columns, settings):
    '''
    Adjusts the layout of a Plotly figure for metabolomics data to accommodate p-value annotation
    by increasing the plot's height and top margin.

    Parameters:
    ----------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure to be adjusted.
    array_columns : list of lists or np.array
        Specifies which column pairs have been used for comparison in the annotation.
    settings : dict
        Plot settings which should include 'height' to be used as a baseline for layout adjustments.

    Returns:
    -------
    tuple
        A tuple (adjusted_interline, adjusted_text_offset) representing the interline spacing and
        text offset for annotations after layout adjustments.
    '''
    
    # Based around default height being 400
    normalizing_factor = settings['height'] / 400
    
    # The values that work for height=400 to display p value annotations
    # Calculate the number of comparisons and the additional space required
    num_comparisons = len(array_columns)
    additional_space = num_comparisons * 30 
    interline = 0.075 
    text_offset = 0.06
    
    # Adjusted constant values based on selected height by a normalizing factor
    if normalizing_factor > 1.5:
        adjusted_additional_space = num_comparisons * 27 * (normalizing_factor / 2)
        adjusted_interline = interline / normalizing_factor
        adjusted_text_offset = text_offset / normalizing_factor
    
    else:
        adjusted_additional_space = additional_space
        adjusted_interline = interline
        adjusted_text_offset = text_offset
    
    # If height or top margin are None, assign them a value
    current_height = fig.layout.height
    current_margin_t = fig.layout.margin.t or 0  # assuming 0 as a default top margin value
    
    # Update the figure layout (height and margins)
    fig.update_layout(
        height=current_height + adjusted_additional_space,
        margin=dict(t=current_margin_t + adjusted_additional_space)
    )
    # Adjust the domain to maintain data's vertical space after plot height increase
    fig.update_yaxes(domain=[0, 0.99])  
    
    return adjusted_interline, adjusted_text_offset


def calculate_metabolomics_pvalue_and_display(y0_data, y1_data, column_pair, met_name, corrected_pvalues, numerical_present, label=None):
    '''
    Calculates the p-value of the two sets of observations and determines the appropriate
    annotation symbol to display on the plot. Handles edge cases such as zero variance or insufficient data.

    Parameters:
    ----------
    y0_data : array_like
        Observations for the first group or condition.
    y1_data : array_like
        Observations for the second group or condition.
    numerical_present : bool
        If True, returns a string with the actual p-value rounded to four decimal places
        or "< 0.0001" if the p-value is smaller than 0.0001. Otherwise, it returns a string
        of asterisks representing the significance level or 'ns' for not significant.

    Returns:
    -------
    str
        A string representing the p-value annotation.
    '''

    # Convert pandas Series to numpy arrays to avoid index issues if necessary
    if isinstance(y0_data, pd.Series):
        y0_data = y0_data.values
    if isinstance(y1_data, pd.Series):
        y1_data = y1_data.values

    # Filter out zero values
    filtered_y0_data = y0_data[y0_data != 0]
    filtered_y1_data = y1_data[y1_data != 0]

    # Handle cases with insufficient data with less than 2 datapoints in either group
    if len(filtered_y0_data) < 2 or len(filtered_y1_data) < 2:
        return "ins data"
    
    # Check for data variance in the same group
    if np.var(y0_data) == 0 or np.var(y1_data) == 0:
        return "zero var"
    
    # Check if all datapoints between the groups are the same
    if np.all(y0_data == y1_data):
        return "identical"
    
    # Perform t-test
    pvalue = perform_two_sided_ttest(filtered_y0_data, filtered_y1_data)
    
    uncorrected_symbol = get_significance_symbol(pvalue, numerical_present, label='p')

    # Fetch corrected p-value and generate symbol
    if corrected_pvalues is not None and not corrected_pvalues.empty:
        # Ensure you are fetching the value using both 'met_name' and 'label' as indices
        if label is not None:
            try:
                corrected_pvalue = corrected_pvalues.at[(met_name, label), str(column_pair)]
                corrected_symbol = get_significance_symbol(corrected_pvalue, numerical_present, label='q')
                return f"{uncorrected_symbol} | {corrected_symbol}"
            except KeyError:
                return uncorrected_symbol  # Return uncorrected symbol if no corrected p-value exists
        else:
            corrected_pvalue = corrected_pvalues.at[met_name, str(column_pair)]
            corrected_symbol = get_significance_symbol(corrected_pvalue, numerical_present, label='q')
            return f"{uncorrected_symbol} | {corrected_symbol}"
    else:
        return uncorrected_symbol  # Handling cases where the corrected p-values DataFrame does not exist or is empty


def get_significance_symbol(pvalue, numerical_present, label=None):
    '''
    Determines the appropriate annotation symbol based on the provided p-value.

    Parameters:
    ----------
    pvalue : float
        The p-value to evaluate for significance.
    numerical_present : bool
        If True, returns a string with the actual p-value rounded to four decimal places
        or "< 0.0001" if the p-value is smaller than 0.0001.
    label : str, optional
        Label to prefix the p-value with (e.g., 'p' for uncorrected or 'q' for corrected p-values).

    Returns:
    -------
    str
        A string representing the significance level based on the p-value, or the p-value itself if numerical_present is True.
    '''
    if pvalue is None or np.isnan(pvalue):
        return 'nd'  # Not determined or data not available

    # Determine the symbol or numeric representation based on the p-value
    if pvalue < 0.001:
        symbol = '***'
    elif pvalue < 0.01:
        symbol = '**'
    elif pvalue < 0.05:
        symbol = '*'
    else:
        symbol = 'ns'

    # If numerical representation is requested and the p-value is above a certain threshold
    if numerical_present:
        if pvalue >= 0.0001:
            symbol = f"{label} = {pvalue:.4f}" if label else f"p = {pvalue:.4f}"
        else:
            symbol = f"{label} < 0.0001" if label else "p < 0.0001"

    return symbol


# Adapted from https://stackoverflow.com/questions/67505252/plotly-box-p-value-significant-annotation
def add_pvalue_shapes_and_annotations(fig, index, column_pair, symbol, settings, y_range, adjusted_text_offset, color='black'):
    '''
    Adds line shapes and text annotations for displaying p-values on a given Plotly figure.

    Parameters:
    ----------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure to which the annotations are to be added.
    index : int
        The index of the current p-value annotation in the list of annotations.
    column_pair : list or array
        A pair of column indices that correspond to the comparison being annotated.
    symbol : str
        The symbol or text that represents the p-value or its significance level.
    settings : dict
        A dictionary with settings for the font of the annotation text.
    y_range : numpy.ndarray
        A 2D array specifying the y-coordinate range for each p-value annotation line.
    adjusted_text_offset : float
        The calculated offset to apply to the y-coordinate for text annotations.
    color : str
        The color for the annotation lines and text.

    Returns:
    -------
    None
    '''
    
    # Adding line shapes for p-value annotations
    for column in column_pair:
        fig.add_shape(type="line",
            xref="x", yref="paper",
            x0=column, y0=y_range[index][0], 
            x1=column, y1=y_range[index][1],
            line=dict(color=color, width=0.7))
        
    fig.add_shape(type="line",
        xref="x", yref="paper",
        x0=column_pair[0], y0=y_range[index][1], 
        x1=column_pair[1], y1=y_range[index][1],
        line=dict(color=color, width=0.7))
    
    # Adding text annotations for p-values
    fig.add_annotation(dict(
        font=dict(
            color=color,
            family=settings['font_selector'],
            size=settings['font_size']
        ),
        x=(column_pair[0] + column_pair[1]) / 2,
        y=y_range[index][1] + adjusted_text_offset,
        showarrow=False,
        text=symbol,
        textangle=0,
        xref="x",
        yref="paper"
    ))


def add_p_value_annotations_pool(fig, met_name, array_columns, numerical_present, corrected_pvalues, settings, color='black'):
    ''' 
    Adds p-value annotations to the metabolomics pool data represented as a box plot
    within a given Plotly figure. It adjusts the plot's height based on the number of
    p-value annotations to ensure clear visibility.

    Parameters:
    ----------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure that holds the box plot.
    array_columns : list of lists or np.array
        An array specifying pairs of column indices to be compared for p-values.
    numerical_present : bool
        Whether to show the numerical p-value on the plot.
    pvalue_correction : str
        User selected string of pvalue corrections to be used in the metabolomics pool figure.
    settings : dict
        A dictionary to configure plot attributes like font style and size.
        Must contain 'height' for space calculations.
    color : str, optional
        The color of the annotation lines and text, defaults to 'black'.

    Returns:
    -------
    plotly.graph_objs._figure.Figure
        The modified figure with p-value annotations added.
    '''
    
    # Adjust the height of the plot for the amount of pvalue annotations and get the adjusted 
    # vlues for the pvalue display
    adjusted_interline, adjusted_text_offset = update_metabolomics_figure_layout(fig, array_columns, settings)

    # Specify in what y_range to plot for each pair of columns
    y_range = np.zeros([len(array_columns), 2])
    for i in range(len(array_columns)):
        y_range[i] = [1.01 + (i * adjusted_interline if i > 0 else 0),
                      1.02 + i * adjusted_interline]

    # Print the p-values
    for index, column_pair in enumerate(array_columns):
        # Read the data from the figure
        y0_data = np.array(fig.data[column_pair[0]]['y']).astype(float)
        y1_data = np.array(fig.data[column_pair[1]]['y']).astype(float)
        
        # Get the pvalue annotation symbol from calculate_pvalue_and_symbol function
        symbol = calculate_metabolomics_pvalue_and_display(y0_data, y1_data, column_pair, met_name, corrected_pvalues, numerical_present)
        
        add_pvalue_shapes_and_annotations(fig, index, column_pair, symbol, settings, y_range, adjusted_text_offset, color='black')
    
    return fig


def generate_single_met_iso_figure(df_metabolite, grouped_samples, settings):
    ''' 
    Generates a stacked bar plot for metabolite isotopologues across different sample groups with error bars and hover texts.
    
    Parameters:
    ----------
    df_metabolite : pandas.DataFrame
        DataFrame containing metabolite data, including 'C_Label' column for isotopologue labeling.
    grouped_samples : dict
        Dictionary mapping sample groups to columns in the DataFrame.
    settings : dict
        A dictionary containing plot settings such as 'boxwidth', 'boxgap', 'height', 'width', 'font', and 'font_size'.
        
    Returns:
    -------
    plotly.graph_objs._figure.Figure
        A figure object containing the generated bar plot.
    '''
    
    fig = go.Figure()
    
    # Initialize num_not_detected with zeros for each sample group
    num_not_detected = {sample_group: 0 for sample_group in grouped_samples}

    # Iterate over each sample group to count non-detected samples by column
    for sample_group, cols_in_group in grouped_samples.items():
        # Check each column in the current group
        for col in cols_in_group:
            # If all values in the column are zero, increment the count for this group
            if (df_metabolite[col].sum() == 0):
                num_not_detected[sample_group] += 1
    
    # Iterating over unique labels in the DataFrame to generate bar plots for each.
    for label in df_metabolite['C_Label'].unique():
        y_values, y_errors, hover_texts, x_values = [], [], [], []
        
        
        
        # Iterating over grouped samples to calculate means, errors and generate hover texts.
        for sample_group, cols_in_group in grouped_samples.items():
            data_for_label = df_metabolite[df_metabolite['C_Label'] == label][cols_in_group]
            
            mean_for_label = data_for_label.mean(axis=1).mean()
            std_for_label = data_for_label.std(axis=1).mean()
            
            # Generating hover text for each bar in the plot.
            hover_data = data_for_label.stack().reset_index()
            hover_texts.append(
                "<br>".join([f"M{label}, {row['level_1']}: {row[0]:.3f}" for _, row in hover_data.iterrows()]) +
                f"<br>Average: {mean_for_label:.3f} ± {std_for_label:.3f}"
            )
            
            y_values.append(mean_for_label)
            y_errors.append(std_for_label)
            
            # Append sample group to x_values, include the number of not detected samples if any
            if num_not_detected[sample_group] > 0:
                x_value = f"{sample_group}<br>{num_not_detected[sample_group]} nd"
            else:
                x_value = sample_group
            
            x_values.append(x_value)
        
        # Adding each isotopologue as a separate trace in the bar plot.
        fig.add_trace(go.Bar(
            x=x_values,
            y=y_values,
            width=settings['boxwidth'],
            name=f'M{int(label)}',
            marker_color=iso_color_palette[int(label)],  # Using a predefined color palette.
            error_y=dict(type='data', array=y_errors, visible=True),
            hoverinfo="text+name",
            hovertext=hover_texts,
            hovertemplate="%{hovertext}<extra></extra>",
            hoverlabel=dict(font_size=settings['font_size'],
                        font_family=settings['font_selector']
                        )
        ))
    
    # Updating the figure layout.
    fig.update_layout(
        barmode='stack',
        bargap=settings['boxgap'],
        height=settings['height'],
        width=settings['width'],
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    # Updating y-axis properties.
    fig.update_yaxes(
        title_text='% Composition of Pool Data',
        range=[0, 1],
        title_font=dict(family=settings['font_selector'], size=settings['font_size']),
        tickfont=dict(family=settings['font_selector'], size=settings['font_size'])
    )
    
    # Updating x-axis properties.
    fig.update_xaxes(
        tickfont=dict(family=settings['font_selector'], size=settings['font_size'])
    )
    
    return fig


def add_p_value_annotations_iso(fig, df_metabolite, met_name, grouped_samples, array_columns, numerical_present, corrected_pvalues, settings, color='black'):
    ''' 
    Adds p-value annotations to the metabolomics isotopologue stacked bar plot based on comparisons
    between specified groups. It adjusts the height of the plot dynamically to accommodate the
    annotations.

    Parameters:
    ----------
    fig : plotly.graph_objs._figure.Figure
        The Plotly figure object that holds the stacked bar plot.
    df_metabolite : pandas.DataFrame
        A DataFrame containing the metabolite name data and isotopologue labeling.
    grouped_samples : dict
        A dictionary mapping group names to lists of sample names within those groups.
    array_columns : list of lists or np.array
        An array specifying pairs of column indices to be compared for p-values.
        Each sub-array or sub-list contains two indices to be compared.
    numerical_present : bool
        Whether to display the actual numerical value of the p-value.
    settings : dict
        A dictionary with plot settings such as 'height', 'width', 'font', 'font_size'.
        It must contain 'height' to calculate space for annotations.
    color : str, optional
        The color used for annotation text. Defaults to 'black'.

    Returns:
    -------
    plotly.graph_objs._figure.Figure
        The modified figure with p-value annotations added.
    '''
    
    # Adjust the height of the plot for the amount of pvalue annotations and get the adjusted 
    # vlues for the pvalue display
    adjusted_interline, adjusted_text_offset = update_metabolomics_figure_layout(fig, array_columns, settings)
  
    
    # Specify in what y_range to plot for each pair of columns
    y_range = np.zeros([len(array_columns), 2])
    for i in range(len(array_columns)):
        y_range[i] = [1.01 + (i * adjusted_interline if i > 0 else 0),
                      1.02 + i * adjusted_interline]

    # Get data where the C_label is not 0
    df_metabolite_label = df_metabolite[df_metabolite['C_Label'] != 0]
    
    # Enumerate through the p_value comparisons submitted by the user
    for index, column_pair in enumerate(array_columns):
        
        group_list = list(grouped_samples.keys())

        # Access the group names using the indices provided by column_pair
        group1_key = group_list[column_pair[0]]
        group2_key = group_list[column_pair[1]]

        # Now use the keys to get the sample names from the grouped_samples dictionary
        group1_sample_names = grouped_samples[group1_key]
        group2_sample_names = grouped_samples[group2_key]
        
        # Sum the column values for each group to get arrays for the t-test
        y0_data = df_metabolite_label[group1_sample_names].sum(axis=0)
        y1_data = df_metabolite_label[group2_sample_names].sum(axis=0)
        
        # Get the pvalue annotation symbol from calculate_pvalue_and_symbol function
        symbol = calculate_metabolomics_pvalue_and_display(y0_data, y1_data, column_pair, met_name, corrected_pvalues, numerical_present)

        add_pvalue_shapes_and_annotations(fig, index, column_pair, symbol, settings, y_range, adjusted_text_offset, color)
    
    return fig


def generate_corrected_pvalues(df, grouped_samples, comparisons, correction_method, graph=None):
    """
    Calculates and corrects p-values for specified comparisons across metabolites, 
    compiling the results into a single DataFrame, ignoring zero values.

    Parameters:
    ----------
    df : pandas.DataFrame
        DataFrame containing the metabolite data with sample values.
    grouped_samples : dict
        Dictionary grouping the columns of samples under specific conditions or treatments.
    comparisons : list of tuples
        List of tuple pairs indicating the indices of groups in 'grouped_samples' to be compared.
    correction_method : str
        The method used for p-value correction (e.g., 'bonferroni', 'fdr_bh').

    Returns:
    -------
    pandas.DataFrame
        A DataFrame with one column per comparison, containing the corrected p-values, and retains specified columns with metabolite information.
    """

    # Convert numeric columns in the dataframe to numeric type
    numeric_columns = [col for group in grouped_samples.values() for col in group]
    df[numeric_columns] = df[numeric_columns].apply(pd.to_numeric, errors='coerce')

    # Handle potential duplicates
    if 'C_Label' not in df.columns:
        if df['Compound'].duplicated().any():
            df.drop_duplicates(subset='Compound', keep='first', inplace=True)

    # Summarize and prepare results DataFrame based on graph type
    if graph == 'iso':
        summed_temp_df = df[df['C_Label'] != 0].groupby(['Compound', 'C_Label']).sum(min_count=1).reset_index()
        summed_df = summed_temp_df.groupby('Compound').sum().reset_index()
        summed_df.set_index('Compound', inplace=True)
        results_df = pd.DataFrame(index=summed_df.index)

    elif graph == 'isodistribution':
        summed_df = df.set_index(['Compound', 'C_Label'])
        results_df = pd.DataFrame(index=summed_df.index.unique())

    else:
        summed_df = df.set_index('Compound')
        results_df = pd.DataFrame(index=summed_df.index.unique())

    all_p_values = []  # List to store all p-values from all comparisons
    pvalue_indices = []  # List to store index information for placing p-values back correctly

    keys_list = list(grouped_samples.keys())

    for comp_pair in comparisons:
        column_name = str(comp_pair)
        p_values = []

        for idx, group_data in summed_df.iterrows():
            compound_key = idx  # compound_key is set directly from the index
            group1_columns = grouped_samples[keys_list[comp_pair[0]]]
            group2_columns = grouped_samples[keys_list[comp_pair[1]]]

            try:
                data_group1 = pd.to_numeric(group_data[group1_columns].replace(0, np.nan).dropna(), errors='coerce')
                data_group2 = pd.to_numeric(group_data[group2_columns].replace(0, np.nan).dropna(), errors='coerce')

            except KeyError as e:
                print(f"KeyError: {e}")
                continue

            if data_group1.empty or data_group2.empty:
                pvalue = np.nan
            else:
                pvalue = perform_two_sided_ttest(data_group1, data_group2)

            p_values.append(pvalue)
            all_p_values.append(pvalue)
            pvalue_indices.append((compound_key, column_name))

        results_df[column_name] = p_values  # Store uncorrected p-values temporarily

    # Correction of p-values
    valid_pvalues = [p for p in all_p_values if not np.isnan(p) and p <= 1]

    corrected_pvalues = apply_pvalue_correction(valid_pvalues, correction_method) if valid_pvalues else []

    correction_map = dict(zip([pvalue_indices[i] for i in range(len(all_p_values)) if all_p_values[i] in valid_pvalues], corrected_pvalues))
    for index, (compound_key, col) in enumerate(pvalue_indices):
        corrected_pvalue = correction_map.get((compound_key, col), np.nan)
        results_df.loc[compound_key, col] = corrected_pvalue

    return results_df


def perform_two_sided_ttest(group_1, group_2, variance_threshold=1e-8):
    # Convert to numpy arrays to ignore any index-related issues
    group_1 = np.array(group_1)
    group_2 = np.array(group_2)

    # Perform t-test if conditions are met
    if len(group_1) > 1 and len(group_2) > 1 and np.var(group_1) > variance_threshold and np.var(group_2) > variance_threshold:
        pvalue = stats.ttest_ind(group_1, 
                                 group_2, 
                                 equal_var=False, 
                                 nan_policy='omit', 
                                 alternative='two-sided')[1]
        
        return pvalue
    else:
        return np.nan
    




def apply_pvalue_correction(pvalues, correction_method):
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


def normalize_met_pool_data(df_pool, grouped_samples, normalization_list):
    '''
    Normalizes a DataFrame of pool metabolomics data based on selected sample group values 
    and metabolite classes.
    
    Parameters:
    ----------
    df_pool : pandas.DataFrame
        A DataFrame containing metabolite pool data, with the 'Compound' column specifying the metabolite names.
    grouped_samples : dict or str
        Dictionary grouping sample columns, or 'all' to include all sample columns.
    normalization_list : list
        List of metabolites used for the normalization process.
        
    Returns:
    -------
    pandas.DataFrame
        A DataFrame containing normalized pool data.
    '''
    
    # Extract the metabolite names column
    pool_met_name_column = df_pool.iloc[:, 0]
    
    # If grouped_samples is 'all', include all sample columns except the first one
    if grouped_samples == 'all':
        all_samples = df_pool.columns[1:]
    else:
        # Flatten grouped_samples to get a list of all relevant sample columns
        all_samples = [sample for group_samples in grouped_samples.values() for sample in group_samples]
    
    # Filter the DataFrame to include only the relevant sample columns
    df_pool_filter = df_pool[all_samples]
    
    # Concatenate the metabolite names column back to the filtered DataFrame
    df_pool_filtered = pd.concat([pool_met_name_column, df_pool_filter], axis=1)
    
    # Extract rows corresponding to metabolites in the normalization_list
    df_pool_normalization = df_pool_filtered[df_pool_filtered['Compound'].isin(normalization_list)]
    
    # Calculate the normalization factors by taking the product of values in normalization rows
    df_pool_norm_series = df_pool_normalization.set_index('Compound').prod().to_list()
    
    # Normalize the DataFrame using the calculated normalization factors
    df_pool_normalized = df_pool_filtered.set_index("Compound").div(df_pool_norm_series)
    df_pool_normalized = df_pool_normalized.reset_index(drop=False)
    
    # Remove rows corresponding to the metabolites used for normalization
    df_pool_normalized = df_pool_normalized[~df_pool_normalized['Compound'].isin(normalization_list)]
    df_pool_normalized = df_pool_normalized.reset_index(drop=True)
    
    return df_pool_normalized


def group_met_pool_data(df, selected_met_classes):
    '''
    Groups and filters normalized metabolite pool data based on selected metabolite classes.
    
    Parameters:
    ----------
    df_pool_normalized : pandas.DataFrame
        A DataFrame containing normalized metabolite pool data.
        
    selected_met_classes : list
        A list of selected metabolite classes to be included in the output DataFrame.
        
    Returns:
    -------
    pandas.DataFrame
        A DataFrame containing the filtered and grouped normalized metabolite pool data.
    '''
    
    # Filter the metabolite groups based on the selected metabolite classes
    df_met_group_select = df_met_group_list[df_met_group_list['pathway_class'].isin(selected_met_classes)]
    
    # Merge the selected metabolite groups with the normalized pool data
    df_filtered = df_met_group_select.merge(df, left_on='analyte_name', right_on='Compound', how='inner')
    
    # Drop the redundant 'analyte_name' column
    df_filtered.drop('analyte_name', axis=1, inplace=True)
    
    return df_filtered


def compile_met_pool_ratio_data(df_pool_normalized_grouped, ratio_list):
    '''
    Compiles a metabolite pool ratio dataframe from selected metabolite ratio list by the user.
    Should be used with a df that comes after using group_met_pool_data() function.
    
    
    Paramaters:
    ----------
    df_pool_normalized_grouped : pandas.DataFrame
        A DataFrame containing normalized and grouped metabolomics pool data.
        
        ratio_list : list
            A list of dictionaries for selecting numerators and denominators for metabolite ratios
            based on the user selection.
    
    Returns:
    -------
    pandas.Dataframe
        A DataFrame containing metabolite ratio data for all sample replicates for the metabolite 
        ratios that the user has selected. Has included 'pathway_class' column and this df can be 
        concatenated with the df that comes after group_met_pool_data.
    '''

    df_ratios = pd.DataFrame()
    
    for ratio in ratio_list:
        numerator = ratio['numerator']
        denominator = ratio['denominator']
        
        # Check presence
        if numerator in df_pool_normalized_grouped['Compound'].values and denominator in df_pool_normalized_grouped['Compound'].values:
            
            # Extract values
            num_values = df_pool_normalized_grouped.loc[df_pool_normalized_grouped['Compound'] == numerator, df_pool_normalized_grouped.columns[1:]].values
            denom_values = df_pool_normalized_grouped.loc[df_pool_normalized_grouped['Compound'] == denominator, df_pool_normalized_grouped.columns[1:]].values
            
            # Ensure single row extraction
            if num_values.shape[0] == 1 and denom_values.shape[0] == 1:

                 # Avoid division by zero by setting ratios to 0 where denominator is 0
                ratio_values = np.where(denom_values != 0, num_values / denom_values, 0)
                
                # Create temp DataFrame
                temp_df = pd.DataFrame(ratio_values, columns=df_pool_normalized_grouped.columns[1:])
                temp_df['Compound'] = f"{numerator} / {denominator}"
                temp_df['pathway_class'] = 'metabolite ratios'
                temp_df = temp_df[['pathway_class', 'Compound'] + list(df_pool_normalized_grouped.columns[1:])]
                
                # Append to main DataFrame
                df_ratios = pd.concat([df_ratios, temp_df])
    
    df_ratios = df_ratios.reset_index(drop=True)
    
    return df_ratios
    
    

def generate_volcano_plot(df_volcano, FC_cutoff, third_pvalue_cutoff, second_pvalue_cutoff, first_pvalue_cutoff, settings, search_value=None):
    """
    Generate an interactive volcano plot using Plotly.

    This function creates a scatter plot to visualize metabolomics data. The plot displays log2 fold change 
    on the x-axis and -log10 p-value on the y-axis. It includes customizable visual aspects such as data point size, 
    background color, and font settings. It also features the ability to highlight a selected metabolite and 
    add horizontal and vertical lines to mark significant thresholds.

    Parameters:
    - df_volcano (DataFrame): A pandas DataFrame containing the columns 'log2FC', 'logp-value', 'color', and 'MetNames'.
    - FC_cutoff (float): The fold change cutoff for significance, used to draw vertical lines on the plot.
    - third_pvalue_cutoff (float): The -log10 p-value cutoff for *** significance level.
    - second_pvalue_cutoff (float): The -log10 p-value cutoff for ** significance level.
    - first_pvalue_cutoff (float): The -log10 p-value cutoff for * significance level.
    - settings (dict): A dictionary containing plot settings such as datapoint size, background color, font settings, etc.
    - search_value (str, optional): The name of a metabolite to highlight. If provided, the function highlights this metabolite.

    Returns:
    - fig (go.Figure): A Plotly graph object figure containing the volcano plot.
    """
    
    fig = go.Figure()
    
    # Defining plot and axis titles
    x_axis_title = "log2 fold change" 
    y_axis_title = "-log10 pvalue"
    dp_size = settings['datapoint_size']
    
    # Adding the main scatter plot
    fig.add_trace(
        go.Scattergl(
            x=df_volcano['log2FC'],
            y=df_volcano['logp-value'],
            mode='markers',
            marker={
                'color': df_volcano['color'],
                'size': dp_size,
            },
            text=df_volcano['MetNames'],  # Hover text
            hoverinfo='text',
            customdata=df_volcano['MetNames'],  # Custom data to access when a point is clicked
        )
    )
    
    if search_value:
        # Highlight the selected metabolite
        selected_data = df_volcano[df_volcano['MetNames'] == search_value]
        if not selected_data.empty:
            fig.add_trace(
                go.Scattergl(
                    x=selected_data['log2FC'],
                    y=selected_data['logp-value'],
                    mode='markers+text',
                    marker=dict(color='black', size=10),  # increased size and changed color
                    text=selected_data['MetNames'],  # Hover text
                    hoverinfo='text',
                    textposition='top right',
                    customdata=selected_data['MetNames'],  # Custom data for the selected point
                )
            )
    
    # Updating layout and adding lines
    fig.update_layout(
        xaxis_title=x_axis_title,
        yaxis_title=y_axis_title,
        paper_bgcolor='white',
        plot_bgcolor='white',
        showlegend=False,
        height=settings['height'],
        width=settings['width'],
        xaxis=dict(
            title_font=dict(  # Sets the font for the x-axis title
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            ),
        tickfont=dict(  # Sets the font for the x-axis ticks
            family=settings['font_selector'],
            size=settings['font_size'],
            color='black'
        )
        ),
        yaxis=dict(
            title_font=dict(  # Sets the font for the y-axis title
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            ),
            tickfont=dict(  # Sets the font for the y-axis ticks
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            )
        ),
    )

    if settings['fc_visible'] == True:
        fig.add_vline(x=FC_cutoff, line_width=1.5, line_dash='dash', line_color='rgba(150,150,150,0.5)')
        fig.add_vline(x=-FC_cutoff, line_width=1.5, line_dash='dash', line_color='rgba(150,150,150,0.5)')

    if settings['p_value_visible'] == True:
        fig.add_hline(y=first_pvalue_cutoff, 
                    annotation_text="* pvalue < 0.05" if settings.get('p_value_text_visible', False) else '', 
                    annotation_position="top right",
                    line_width=1.5, line_dash='dash', 
                    line_color='rgba(150,150,150,0.5)',
                    annotation_font=dict(size=settings['font_size'], family=settings['font_selector']))
        fig.add_hline(y=second_pvalue_cutoff, 
                    annotation_text="* pvalue < 0.01" if settings.get('p_value_text_visible', False) else '',
                    annotation_position="top right",
                    line_width=1.5, line_dash='dash', 
                    line_color='rgba(150,150,150,0.5)',
                    annotation_font=dict(size=settings['font_size'], family=settings['font_selector']))
        fig.add_hline(y=third_pvalue_cutoff, 
                    annotation_text="*** pvalue < 0.001" if settings.get('p_value_text_visible', False) else '',
                    annotation_position="top right",
                    line_width=1.5, 
                    line_dash='dash', 
                    line_color='rgba(150,150,150,0.5)',
                    annotation_font=dict(size=settings['font_size'], family=settings['font_selector']))
    
    return fig


def ttest_volcano(row, ctrl_cols, cond_cols):
    '''
    Conducts an independent two-sided t-test on the control and condition values 
    of a specific metabolite to determine the p-value. 
    
    Parameters:
    ----------
    row : pd.Series
        A row of the dataframe, which includes the values for a specific metabolite.
        
    ctrl_cols : list
        List of column indices or names corresponding to the control group in the row.
        
    cond_cols : list
        List of column indices or names corresponding to the condition group in the row.
        
    Returns:
    -------
    float or np.nan
        The p-value resulting from the t-test if the test is valid; np.nan otherwise.
    '''
    
    # Convert values to numeric, ignoring non-numeric values (errors='coerce'), 
    # and then dropping any resulting NaN values
    ctrl_values = pd.to_numeric(row[ctrl_cols], errors='coerce').dropna() 
    cond_values = pd.to_numeric(row[cond_cols], errors='coerce').dropna()
    
    # Perform an independent two-sided t-test, assuming equal variance,
    # between the control and condition groups
    filtered_ctrl_values = ctrl_values[ctrl_values != 0]
    filtered_cond_values = cond_values[cond_values != 0]

    pvalue = perform_two_sided_ttest(filtered_ctrl_values, filtered_cond_values)
    
    return pvalue


def assign_color(row, FC_cutoff, third_pvalue_cutoff, second_pvalue_cutoff, first_pvalue_cutoff, settings):
    '''
    Assigns a color to a metabolite based on its log2 fold change (log2FC) and 
    the negative logarithm of its p-value (logp-value) according to specified cutoffs.
    
    Parameters:
    ----------
    row : pd.Series
        A row of the dataframe containing the 'logp-value' and 'log2FC' values for a specific metabolite.
        
    FC_cutoff : float
        The fold change cutoff value used for color assignment.
        
    third_pvalue_cutoff, second_pvalue_cutoff, first_pvalue_cutoff : float
        The p-value cutoffs used for color assignment.
        
    Returns:
    -------
    str
        A color code corresponding to the classification of the metabolite based on its values.
    '''
    
    plot_pvalue = row['logp-value']
    plot_FC = row['log2FC']
    
    # Read the color for not significant points from the settings
    ns_color = settings['datapoint_color']
    
    # Color assignment based on log2FC and p-value cutoffs
    if plot_FC > FC_cutoff:
        if plot_pvalue > third_pvalue_cutoff:
            return settings['color_inc_3']
        elif plot_pvalue <= third_pvalue_cutoff and plot_pvalue > second_pvalue_cutoff:
            return settings['color_inc_2']
        elif plot_pvalue <= second_pvalue_cutoff and plot_pvalue > first_pvalue_cutoff:
            return settings['color_inc_1']
        else:
            return ns_color
        
    elif plot_FC < -FC_cutoff:
        if plot_pvalue > third_pvalue_cutoff:
            return settings['color_dec_3']
        elif plot_pvalue <= third_pvalue_cutoff and plot_pvalue > second_pvalue_cutoff:
            return settings['color_dec_2']
        elif plot_pvalue <= second_pvalue_cutoff and plot_pvalue > first_pvalue_cutoff:
            return settings['color_dec_1']
        else:
            return ns_color
        
    else:
        return ns_color


def log2_transform(df, excluded_columns=['Compound', 'pathway_class']):
    '''
    Apply a log2 transformation to the values in the dataframe, excluding specified columns.
    
    Parameters:
    ----------
    df : pandas.DataFrame
        The dataframe to be transformed.
    excluded_columns : list of str, optional
        Columns to be excluded from transformation (default is ['Compound', 'pathway_class']).
        
    Returns:
    -------
    pandas.DataFrame
        A new dataframe with log2-transformed values.
    '''
    
    # Creating a copy of the input dataframe to avoid modifying the original dataframe
    transformed_df = df.copy()
    
    # Iterating over each column in the dataframe
    for column in transformed_df.columns:
        
        # Applying log2 transformation to columns that are not in the excluded_columns list
        if column not in excluded_columns:
            
            # Applying log2 transformation to each value in the column
            # np.log2(x) is used for the transformation, and a check is added to avoid log2(0)
            transformed_df[column] = transformed_df[column].apply(lambda x: np.log2(x) if x != 0 else 0)
            
    # Returning the dataframe with transformed values
    return transformed_df


def transform_log2_and_adjust_control_data(df, grouped_samples, ctrl_group):
    """
    Process and adjust the control data from a dataframe by performing log2 transformation and 
    calculating the mean of control samples without including zero values in the calculation.
    The log2-transformed control means are then subtracted from corresponding log2-transformed sample data,
    ensuring that original zero values in the dataset are retained as zero after the operation.

    Parameters:
    ----------
    df : DataFrame
        The input dataframe containing sample measurements alongside compound and pathway class information.
    grouped_samples : dict
        A dictionary mapping each group name to a list of column names corresponding to sample data.
    ctrl_group : str
        The key in 'grouped_samples' that corresponds to the control group columns.

    Returns:
    -------
    DataFrame
        A new DataFrame in which the log2-transformed control averages have been subtracted from the 
        corresponding sample data, with the exception that original zeros remain unchanged. Columns 
        exclusive to control group data and metadata (like 'Compound' and 'pathway_class') are excluded 
        from transformation and subtraction, and the 'ctrl_avg' column used for adjustment is dropped 
        from the resulting DataFrame.
    
    Notes:
    -----
    - The control average ('ctrl_avg') is calculated by replacing zero values with NaN to prevent them 
      from affecting the mean. After mean calculation, NaNs are transformed to zeros using log2 transformation.
    - Subtraction of control averages from sample data is performed only if the original sample value 
      before transformation was non-zero to preserve the biological relevance of zero values indicating 
      non-detection or absence of a compound.
    - The function uses a predefined 'log2_transform' function to apply log2 transformation to DataFrame 
      values, excluding specified columns.
    """
        
    ctrl_cols = grouped_samples[ctrl_group]
    
    df_ctrl_avg = pd.DataFrame(index=df.index)
    df_ctrl_avg['Compound'] = df['Compound']

    ctrl_avg_values = df[ctrl_cols].replace(0, np.nan).mean(axis=1, skipna=True)
    ctrl_avg_values = ctrl_avg_values.fillna(0)
    
    df_ctrl_avg['ctrl_avg'] = ctrl_avg_values

    df_ctrl_avg_log2 = log2_transform(df_ctrl_avg).drop_duplicates()
    df_log2_transformed = log2_transform(df)
    
    df_log2_transformed = df_log2_transformed.merge(df_ctrl_avg_log2, on='Compound', how='left')
    
    columns_to_subtract = [col for col in df_log2_transformed.columns if col not in ['Compound', 'pathway_class', 'ctrl_avg']]
    
    # Subtract the control averages from the data columns
    for column in columns_to_subtract:
           # Use numpy.where to vectorize the condition: subtract only if original value is not zero
            df_log2_transformed[column] = np.where(df_log2_transformed[column] != 0,
                                           df_log2_transformed[column] - df_log2_transformed['ctrl_avg'],
                                           0)
    
    # Drop 'ctrl_avg' as it's not needed anymore
    df_log2_transformed.drop(columns=['ctrl_avg'], inplace=True)
    
    return df_log2_transformed


def generate_individual_heatmap(pathway_df, grouped_samples, settings, group_significance, ctrl_cols, non_heatmap_columns=['Compound', 'pathway_class'], data_type='pool'):
    """
    Generate a heatmap for a set of metabolites in different groups of samples.
    
    Parameters:
    - pathway_df (DataFrame): The dataframe containing the metabolite data.
    - grouped_samples (dict): A dictionary containing sample grouping.
    - group_significance (list): list of group comparisons that have pvalue < 0.05
    - ctrl_cols (list): control columns in the pathway_df that was selected for the heatmap
    - non_heatmap_columns (list, optional): Columns not to be included in the heatmap.
    
    Returns:
    - Figure: A Plotly Figure object containing the generated heatmap.
    """

    def find_group(sample_name, groups):
        """
        Identify the group of a sample.
        
        Parameters:
        - sample_name (str): The name of the sample.
        - groups (dict): A dictionary containing sample grouping.
        
        Returns:
        - str: The group name where the sample is found, otherwise None.
        """
        for group, samples in groups.items():
            if sample_name in samples:
                return group
        return None
    
    # Dropping non heatmap columns and copying data to new DataFrame
    heatmap_data = pathway_df.drop(columns=non_heatmap_columns).copy()
    y_labels = pathway_df['Compound']
    
    # Getting the maximum absolute value for color scaling
    max_val = heatmap_data.abs().max().max()
    
    if data_type == 'pool':
        colorscale = [[0, settings['decreased_color']],
                      [0.5, settings['unchanged_color']],
                      [1, settings['increased_color']]]
        
    if data_type == 'iso':
        colorscale = [[0, settings['unchanged_color']],
                      [1, settings['increased_color']]]
        
    # Creating new DataFrames for the heatmap and hover text
    plot_heatmap_data = pd.DataFrame(index=heatmap_data.index)
    hovertext = pd.DataFrame(index=heatmap_data.index)  
    
    if settings['first_gap_present'] == True:
        plot_heatmap_data['gap_start'] = np.nan  # Adding a starting gap column with NaN values
        hovertext['gap_start'] = ''
    
    prev_group = None
    for column in heatmap_data.columns:
        current_group = find_group(column, grouped_samples)
        
        if settings['group_gaps_present'] == True:
            # Insert a gap column when group changes
            if current_group != prev_group and prev_group is not None:
                gap_column_name = f'gap_{prev_group}'
                plot_heatmap_data[gap_column_name] = np.nan
                hovertext[gap_column_name] = ''
        
        # Insert the actual data
        plot_heatmap_data[column] = heatmap_data[column]
        hovertext[column] = heatmap_data[column]
        
        prev_group = current_group
    
    # Adding the data to the Plotly figure
    heatmap = go.Figure()
    heatmap.add_trace(go.Heatmap(z=plot_heatmap_data.values,
                                 hovertext=hovertext,
                                 y=y_labels,
                                 x=plot_heatmap_data.columns,
                                 colorscale=colorscale,
                                 showscale=True,
                                 zmin=-max_val,
                                 zmax=max_val,
                                 colorbar=dict(
                                     len=0.7,
                                     thickness=5
                                 )
                                 ))
    
    # Checking if settings were updated or not
    extra_height = 200
    cell_height = 30 * settings['height_modifier']
    heatmap_height = len(y_labels) * cell_height 
    height = heatmap_height + extra_height
    
    width_per_group = 75 * settings['width_modifier']
    width = len(heatmap_data.columns) * width_per_group 
    
    include_first_gap = settings['first_gap_present']
    include_group_gaps = settings['group_gaps_present']
    gap_width = 1  # Assuming each gap is 1 unit wide
    
    # Calculate middle points of each sample group in the heatmap
    middle_points = calculate_heatmap_group_middle_points(grouped_samples, include_first_gap, include_group_gaps, gap_width)
    
    # Adjust tickvals and ticktext based on middle_points
    tickvals = list(middle_points.values())
    ticktext = [f"<br>{group}" for group in middle_points.keys()]

    # If the ending gap is also present, adjust accordingly
    # if settings['ending_gap_present']:  # Assuming this is another setting you might have
    #     tickvals.append(max(tickvals) + gap_width)
    #     ticktext.append('gap_end')
    
    # Updating the x-axis with settings
    heatmap.update_xaxes(
        tickvals=tickvals,
        ticktext=ticktext,
        title_standoff=100,
        tickfont=dict(
            family=settings['font_selector'],
            size=settings['font_size'],
            color='black'   
        )
    )
    
    # Updating the y-axis with settings
    heatmap.update_yaxes(
        tickvals=list(range(len(y_labels))),
        ticktext=y_labels,
        autorange="reversed",
        title_standoff=30,
        tickfont=dict(
            family=settings['font_selector'],
            size=settings['font_size'],
            color='black'   
        )
    )
    
    # Layout updates for the heatmap figure
    heatmap.update_layout(height=height,
                          width=width,
                          plot_bgcolor='white',
                          margin=dict(l=200,
                                      r=10),
                          yaxis=dict(
                              domain=[0, 1]  
                          )
                        )
    
    heatmap.update_layout(
        hoverlabel=dict(font_size=settings['font_size'],
                        font_family=settings['font_selector']
                        ))
    
    if settings['sig_dots_present'] == True:
        if group_significance is not None:
            heatmap = add_heatmap_significance_annotations(heatmap, y_labels, group_significance, settings)
    
    add_nd_annotations_and_update_values(heatmap, ctrl_cols)
        
    update_colorscale(heatmap, colorscale, data_type)
    
    return heatmap


def calculate_heatmap_group_middle_points(grouped_samples, include_first_gap, include_group_gaps, gap_width):
    """
    Calculate the middle points of sample groups for a heatmap.

    This function computes the middle points of each group in a set of grouped samples, typically used 
    for aligning labels or annotations in a heatmap. It accounts for gaps between groups and optionally 
    an initial gap before the first group.

    Parameters:
    - grouped_samples (dict): A dictionary where keys are group names and values are lists of sample columns belonging to each group.
    - include_first_gap (bool): If True, includes a gap before the first group.
    - include_group_gaps (bool): If True, includes gaps between each group of samples.
    - gap_width (int): The width of the gaps between groups (and before the first group if include_first_gap is True).

    Returns:
    - middle_points (dict): A dictionary where keys are the group names and values are the calculated middle points of each group.
    """
  
    middle_points = {}
    current_position = 0

    if include_first_gap:
        current_position += gap_width  # Account for the first gap column

    for group, columns in grouped_samples.items():
        group_start = current_position
        group_end = group_start + len(columns) - 1

        group_middle = (group_start + group_end) / 2
        middle_points[group] = group_middle

        current_position = group_end + 1
        if include_group_gaps:
            current_position += gap_width  # Account for gap columns between sample groups

    return middle_points


def update_colorscale(heatmap_fig, colorscale, data_type):
    """
    Updates the colorscale of a heatmap figure. Adjusts the color scaling to be symmetrical around zero for 'pool' data type,
    and unsymmetrical for 'iso' data type. It finds the maximum (and minimum, if needed) values within the 'z' data of the
    heatmap, ignoring NaN values, to set the 'zmin' and 'zmax' for the figure accordingly.

    Parameters:
        heatmap_fig (go.Figure): The heatmap figure object to update.
        colorscale (str or list): The colorscale to be applied to the heatmap. This can be a predefined colorscale 
                                  name, or a list of colors defining the scale.
        data_type (str): Type of data that is displayed in the heatmap, 'pool' or 'iso'.
    Returns:
        None: The function updates the heatmap figure in place and does not return any value.
    """
    # Find the min and max z values, ignoring NaN values
    z_data = np.array(heatmap_fig.data[0].z)
    non_nan_z_values = z_data[~np.isnan(z_data)]

    if data_type == 'pool':
        # Find the max absolute value for the color scaling to be symmetrical around zero
        max_val = np.max(np.abs(non_nan_z_values))
        zmin = -max_val
        zmax = max_val
    elif data_type == 'iso':
        # Use the actual min and max for unsymmetrical color scaling
        zmin = 0
        zmax = 1
    
    # Update the traces with the new scale
    heatmap_fig.update_traces(zmin=zmin, zmax=zmax, colorscale=colorscale)


def add_nd_annotations_and_update_values(heatmap_fig, ctrl_cols):
    """
    Annotates heatmap cells with 'nd' (no data) for zero values and updates the heatmap 'z' values based on 
    control columns. If all control column values for a row are zero, all corresponding cells in that row are 
    set to zero and annotated with red '0'. It also tracks cells that have been annotated to prevent duplicate 
    annotations.

    Parameters:
        heatmap_fig (go.Figure): The heatmap figure object to update with annotations and value changes.
        ctrl_cols (list): A list of column names that are considered control columns, used to determine if a 
                          row's values should be updated based on these control values.

    Returns:
        None: The function updates the heatmap figure in place with new annotations and modified 'z' data 
              and does not return any value.
    """
    z_data = np.array(heatmap_fig.data[0].z)  # The 'z' values as an array for processing
    x_data = list(heatmap_fig.data[0].x)  # The 'x' values as a list
    y_data = heatmap_fig.data[0].y  # The 'y' values

    # Create a set to track 'nd' annotated cells by their (row, column) index
    nd_annotated_cells = set()

    # Determine the indices for the control columns
    ctrl_col_indices = [x_data.index(col) for col in ctrl_cols if col in x_data]

    # First pass to annotate 'nd' for zero values, ignoring NaNs
    for y_index, y_val in enumerate(y_data):
        for x_index, x_val in enumerate(x_data):
            value = z_data[y_index][x_index]
            if value == 0:  # Annotate only exact zeros, skip NaNs and gaps
                heatmap_fig.add_annotation(
                    text='nd',
                    x=x_val,
                    y=y_val,
                    xref='x1',
                    yref='y1',
                    showarrow=False,
                    font=dict(size=10, color='black'),
                    bgcolor='white'
                )
                # Add the cell to the 'nd' annotated set
                nd_annotated_cells.add((y_index, x_index))

    # Check if the user has submitted ctrl_cols (bulk isotopologue heatmap does not need it)
    if ctrl_cols != []:
        # Second pass to set zeros based on control columns being all zero
        for y_index, y_val in enumerate(y_data):
            # Extract control column values for the current row, skipping NaNs
            control_values = [z_data[y_index][ctrl_col_index] for ctrl_col_index in ctrl_col_indices if not np.isnan(z_data[y_index][ctrl_col_index])]
            # If control values are all zero and the list is not empty (which means control columns had valid numbers and not just NaNs)
            if control_values and all(val == 0 for val in control_values):
                # Update the row's 'z' values to zero where 'nd' is not annotated, skipping NaNs and gaps
                for x_index, x_val in enumerate(x_data):
                    if (y_index, x_index) not in nd_annotated_cells and not np.isnan(z_data[y_index][x_index]):
                        # Set the value to zero
                        z_data[y_index][x_index] = 0
                        # Add a unique red '0' annotation
                        heatmap_fig.add_annotation(
                            text='0',
                            x=x_val,
                            y=y_val,
                            xref='x1',
                            yref='y1',
                            showarrow=False,
                            font=dict(size=10, color='red'),
                            bgcolor='white'
                        )

    # Update the figure with the modified 'z' data
    heatmap_fig.data[0].z = z_data.tolist()


def add_heatmap_significance_annotations(heatmap_fig, y_labels, group_significance, settings, gap_col_name='gap_start'):
    """
    Add red dot annotations in the 'gap_start' column of a Plotly heatmap for significant molecules.
    This function is adjusted to check if the molecule from group_significance exists on heatmap's y-axis.
    Parameters:
    - heatmap_fig (go.Figure): The Plotly heatmap figure object.
    - y_labels (pd.Series): A pandas Series with the y-axis labels of the heatmap.
    - group_significance (dict): A dictionary where keys are molecule names and values are tuples
      indicating significant comparisons for the corresponding molecule.
    - gap_col_name (str): The name of the gap column where annotations should be placed.
    """
    
    def filter_group_significance(y_labels, group_significance):
        """
        Filter the group_significance dictionary to only include keys that are present in the y_labels.

        Parameters:
        - y_labels (pd.Series or list): The available y-axis labels in the heatmap section.
        - group_significance (dict): The full dictionary of group significance results.

        Returns:
        - dict: A filtered group_significance dictionary.
        """
        # Ensure y_labels is a set for O(1) lookups
        y_label_set = set(y_labels)

        # Filter the group_significance dictionary
        filtered_significance = {mol: pairs for mol, pairs in group_significance.items() if mol in y_label_set}

        return filtered_significance


    y_labels = y_labels.reset_index(drop=True)
    
    # Get the list of all current x-axis categories in the heatmap (which includes gap columns)
    x_categories = list(heatmap_fig.data[0].x)

    # Find the index for the gap_start column in the x-axis categories
    if gap_col_name in x_categories:
        gap_start_index = x_categories.index(gap_col_name)
    else:
        return heatmap_fig

    filtered_group_significance = filter_group_significance(y_labels, group_significance)

    # Iterate over the group significance dictionary to create annotations
    for molecule, group_pairs in filtered_group_significance.items():
        # Check if the molecule is in the y_labels
        if molecule in y_labels.values:
            molecule_index = y_labels[y_labels == molecule].index[0]

            # Create hovertext displaying all group pairs for the molecule
            hovertexts = f"Significant differences for {molecule}:<br>" + "<br>".join([f"{pair[0]} vs {pair[1]}" for pair in group_pairs])

            # Add annotation directly to the figure with styling
            heatmap_fig.add_annotation(
                x=gap_start_index,
                y=molecule_index,
                text="●",
                showarrow=False,
                xref="x",
                yref="y",
                xanchor="center",
                yanchor="middle",
                font=dict(size=20, 
                          color='red'),
                hovertext=hovertexts,
                hoverlabel=dict(font_size=settings['font_size'], 
                                font_family=settings['font_selector'])
            )

    return heatmap_fig


def generate_group_significance(df_pool, grouped_samples):
    """
    Analyzes a DataFrame for statistically significant differences between groups of samples. 
    It performs pairwise t-tests between all unique pairs of groups for each compound, excluding pairs 
    where data is insufficient or missing. Significance is determined based on a p-value threshold of 0.05.

    Parameters:
        df_pool (pd.DataFrame): A DataFrame containing compound data with samples as columns and compounds as rows.
                                The 'pathway_class' column, if present, will be dropped.
        grouped_samples (dict): A dictionary mapping group names to column names in `df_pool`. Each group is 
                                associated with a list of sample column names that belong to that group.

    Returns:
        dict: A dictionary with compounds as keys, each key containing a list of tuples. Each tuple represents 
              a pair of group names for which the difference in means of compound levels is statistically significant.

    The function first sanitizes the input data by converting sample values to numeric, handling NaNs, and removing 
    the 'pathway_class' column if present. It then computes the t-test for each compound across all pairs of groups 
    and stores the results for pairs with p-values below the significance threshold, ensuring that no duplicate 
    group comparisons are recorded.
    """
    significant_results = {}  # Dictionary to store results

    # Check if 'pathway_class' column exists and drop it
    if 'pathway_class' in df_pool.columns:
        df_pool = df_pool.drop(columns=['pathway_class'])
    
    # Create all unique pairs for comparison by sorting to ensure uniqueness
    unique_pairs = [(group1, group2) for i, group1 in enumerate(grouped_samples.keys()) 
                    for group2 in list(grouped_samples.keys())[i+1:]]

    # Iterate over each compound
    for index, row in df_pool.iterrows():
        compound = row['Compound']
        for (group1, group2) in unique_pairs:
            # Extract the data and ensure it's numeric and NaNs are handled
            data1 = pd.to_numeric(row[grouped_samples[group1]], errors='coerce').dropna()
            data2 = pd.to_numeric(row[grouped_samples[group2]], errors='coerce').dropna()

            filtered_data1 = data1[data1 != 0]
            filtered_data2 = data2[data2 != 0]

            pvalue = perform_two_sided_ttest(filtered_data1, filtered_data2)

            # If p-value < 0.05, store it, ensuring that duplicates are not added
            if pvalue < 0.05:
                # Sort the group names to maintain consistency
                sorted_groups = tuple(sorted([group1, group2]))
                
                # Update the significant_results dictionary
                if compound not in significant_results:
                    significant_results[compound] = [sorted_groups]
                else:
                    if sorted_groups not in significant_results[compound]:  # Check for duplicates
                        significant_results[compound].append(sorted_groups)
    
    return significant_results


def calculate_offsets_for_volcano_annotations(new_point, stored_points, standoff=4, font_size=12, max_trials=100):
    """
    Calculate the annotation position offsets for a new point on a volcano plot to avoid overlapping other annotations.
    
    :param new_point: A dict with 'x' and 'y' keys for the new point coordinates.
    :param stored_points: A list of dicts with 'x' and 'y' keys for existing annotated points.
    :param standoff: The standoff distance between the point and the text box, in axis units.
    :param font_size: The assumed height of the font for the text box in pixels (since actual size in axis units is unknown).
    :param max_trials: The maximum number of different angles to try before giving up.
    :return: A tuple (ax, ay) representing the offsets in the x and y directions for the end of the annotation arrow.
    """

    # Conversion factor from font size in pixels to axis units, this would need adjustment based on your axis scaling
    pixels_to_units = 0.02  # This is a placeholder; you'd adjust this based on your axis scale settings

    # Calculate the radial distance from the point to the start of the text box, which will be used as the radius in the spiral search
    radius = standoff / pixels_to_units + font_size

    # Initialize the best offset to the default values
    best_ax, best_ay = 30, 30
    found_spot = False

    # Search for offsets in a spiral pattern to avoid overlaps
    for trial in range(max_trials):
        # Increase the spiral radius with each trial
        radius += font_size * pixels_to_units * trial / max_trials
        # Calculate the trial angle using a golden angle approximation for a uniform distribution of points
        angle = trial * 137.508  # degrees
        # Convert angle to radians for trigonometric functions
        angle_rad = np.radians(angle)
        # Calculate offsets based on the angle and radius
        ax_trial = radius * np.cos(angle_rad)
        ay_trial = radius * np.sin(angle_rad)

        # Check for overlap with existing annotations
        overlap = any(
            np.hypot(existing_point['x'] - (new_point['x'] + ax_trial), existing_point['y'] - (new_point['y'] + ay_trial))
            < standoff for existing_point in stored_points
        )

        if not overlap:
            best_ax = ax_trial
            best_ay = ay_trial
            found_spot = True
            break

    # If no spot is found after max_trials, you can choose to return some default or raise an error
    if not found_spot:
        # Here, you might want to either use a default value or handle it as an error.
        # For now, we'll set it to some default offset values
        best_ax, best_ay = 30, 30  # Default offset when no non-overlapping position is found

    return best_ax, best_ay


def generate_isotopologue_distribution_figure(df_iso_met, grouped_samples, settings):
    """
    Generate a bar chart figure representing isotopologue distribution for metabolite data.

    This function creates a grouped bar chart to display the distribution of isotopologues across different 
    sample groups. Each isotopologue's average percentage composition within each sample group is plotted as 
    a bar, with error bars representing standard deviation. The function also skips isotopologues that have 
    zero values across all sample groups.

    Parameters:
    - df_iso_met (DataFrame): A pandas DataFrame containing isotopologue data with columns 'C_Label' and sample identifiers.
    - grouped_samples (dict): A dictionary where keys are group names and values are lists of sample columns belonging to each group.
    - settings (dict): A dictionary containing plot settings such as bar width, bar gap, plot dimensions, etc.

    Returns:
    - fig (go.Figure): A Plotly graph object figure containing the isotopologue distribution bar chart.
    """
    
    fig = go.Figure()  # Create a new plotly figure
    
    encountered_groups = set()  # Keep track of processed sample groups to manage legend entries

    # Iterate through every isotopologue for the metabolite data
    for label in df_iso_met['C_Label'].unique():
        # Check if all values are zero across all sample groups for this C_Label
        all_zero = True
        for sample_group, cols_in_group in grouped_samples.items():
            data_for_label = df_iso_met[df_iso_met['C_Label'] == label][cols_in_group]
            mean_for_label = data_for_label.mean(axis=1).mean()
            
            if mean_for_label != 0:  # If any mean is non-zero, set all_zero to False and exit loop
                all_zero = False
                break
        
        if all_zero:
            continue  # Skip the rest of the code in this iteration and move to the next label
        
        # Proceed to plotting if not all values are zero
        for sample_group_index, (sample_group, cols_in_group) in enumerate(grouped_samples.items()):
            color = iso_color_palette[sample_group_index % len(iso_color_palette)]
             
            data_for_label = df_iso_met[df_iso_met['C_Label'] == label][cols_in_group]
            
            # Calculate mean and std deviation across the group columns
            mean_for_label = data_for_label.mean(axis=1).mean()
            std_for_label = data_for_label.std(axis=1).mean()
            
            # Offset calculation
            offset = ((sample_group_index - len(grouped_samples) / 2) * (settings['barwidth'] + settings['bargap']) + 0.05)
            
            # Determine whether to show this trace in the legend
            show_in_legend = sample_group not in encountered_groups
            encountered_groups.add(sample_group)
            
            hover_data = data_for_label.stack().reset_index()  # Using stack() to get each sample's data
            hover_text_list = [f"M{label}, {row['level_1']}: {row[0]:.3f}" for _, row in hover_data.iterrows()]
            hover_text = "<br>".join(hover_text_list)
            hover_text += f"<br>Average: {mean_for_label:.3f} ± {std_for_label:.3f}"  # Add mean and error

            # Adding trace to the figure
            fig.add_trace(go.Bar(
                name=sample_group if show_in_legend else None,
                x=[f'<br>M{label}'],
                offset=offset,
                y=[mean_for_label],
                error_y=dict(type='data', array=[std_for_label], visible=True),
                marker_color=color,
                width=settings['barwidth'],
                showlegend=show_in_legend,
                hoverinfo='text',
                hovertext=hover_text
            ))
            
    # Updating layout of the Plotly graph
    fig.update_layout(
        barmode='group',
        bargap=settings['bargap'],
        xaxis_title='Isotopologue',
        yaxis_title='% Composition of Pool Data',
        height = settings['height'],
        width = settings['width'],
        plot_bgcolor='white',
        paper_bgcolor='white'
    )
    
    fig.update_yaxes(range=[0,1])
    
    return fig


def add_p_value_annotations_iso_distribution(fig, df_iso_met, met_name, grouped_samples, array_columns, numerical_present, corrected_pvalues, settings, color='black'):
    """
    Add p-value annotations to an isotopologue distribution figure.

    This function annotates a Plotly figure representing isotopologue distribution with p-values. It compares 
    isotopologue data between different sample groups and adds statistical significance annotations. The function 
    filters out rows where all values are zero, calculates p-values for pairs of sample groups, and adds 
    corresponding annotations to the figure.

    Parameters:
    - fig (go.Figure): The Plotly graph object figure to which the annotations will be added.
    - df_iso_met (DataFrame): A pandas DataFrame containing isotopologue data with columns 'C_Label' and sample identifiers.
    - grouped_samples (dict): A dictionary where keys are group names and values are lists of sample columns belonging to each group.
    - array_columns (list of tuples): List of tuples where each tuple contains indices of two groups to be compared for p-value calculation.
    - numerical_present (bool): Indicator of whether numerical data is present.
    - settings (dict): A dictionary containing plot settings such as annotation positions, text offset, etc.
    - color (str, optional): Color of the p-value annotation text. Default is 'black'.

    Returns:
    - fig (go.Figure): The modified Plotly graph object figure with added p-value annotations.
    """
        
    # Get all columns from grouped_samples
    all_grouped_columns = [col for group in grouped_samples.values() for col in group]
    # Filter out rows where all values are zero in grouped_samples columns
    df_iso_met = df_iso_met.loc[~(df_iso_met[all_grouped_columns] == 0).all(axis=1)]
    
    # Adjust the height of the plot for the amount of pvalue annotations and get the adjusted 
    # values for the pvalue display
    adjusted_interline, adjusted_text_offset = update_metabolomics_figure_layout(fig, array_columns, settings)
    
    # Specify in what y_range to plot for each pair of columns
    y_range = np.zeros([len(array_columns), 2])
    for i in range(len(array_columns)):
        y_range[i] = [1.01 + (i * adjusted_interline if i > 0 else 0), 1.02 + i * adjusted_interline]

    # Identify unique group labels (like 'M0', 'M1', etc.)
    group_labels = df_iso_met['C_Label'].unique()

    for label in group_labels:
        # Calculate the index of the current label
        label_index = np.where(group_labels == label)[0][0]
        # Filter DataFrame for the current label
        df_label = df_iso_met[df_iso_met['C_Label'] == label]

        for index, column_pair in enumerate(array_columns):
            group_list = list(grouped_samples.keys())

            # Access the group names using the indices provided by column_pair
            group1_key = group_list[column_pair[0]]
            group2_key = group_list[column_pair[1]]

            # Now use the keys to get the sample names from the grouped_samples dictionary
            group1_sample_names = grouped_samples[group1_key]
            group2_sample_names = grouped_samples[group2_key]
            
            # Extract the relevant columns for each group
            y0_data = df_label[group1_sample_names].fillna(0)
            y1_data = df_label[group2_sample_names].fillna(0)
            
            y0_data = y0_data.iloc[0]
            y1_data = y1_data.iloc[0]

            # Convert data to numeric and calculate p-value annotation
            y0_data = pd.to_numeric(y0_data, errors='coerce')
            y1_data = pd.to_numeric(y1_data, errors='coerce')
            symbol = calculate_metabolomics_pvalue_and_display(y0_data, y1_data, column_pair, met_name, corrected_pvalues, numerical_present, label)

            # Add p-value shapes and annotations
            # Calculate the x-coordinates based on the label's position in the plot
            x_coord1 = calculate_x_coordinate_for_label(label_index, group1_key, grouped_samples, settings)
            x_coord2 = calculate_x_coordinate_for_label(label_index, group2_key, grouped_samples, settings)
            add_pvalue_shapes_and_annotations(fig, index, [x_coord1, x_coord2], symbol, settings, y_range, adjusted_text_offset, color)

    return fig
        
        
def calculate_x_coordinate_for_label(label_index, group_key, grouped_samples, settings):
    """
    Calculate the x-coordinate for a specific bar in a grouped bar plot.

    Parameters:
    label_index (int): The index of the label (e.g., 0 for "M0", 1 for "M1", etc.)
    group_key (str): The key of the sample group.
    grouped_samples (dict): Dictionary of grouped samples.
    settings (dict): Dictionary containing 'barwidth' and 'bargap' settings.

    Returns:
    float: The calculated x-coordinate for the bar.
    """
    # Convert the group key to a numeric index
    group_index = list(grouped_samples.keys()).index(group_key)
    total_groups = len(grouped_samples)

    # Base x-coordinate for the label (assuming each label is 1 unit apart)
    base_x = label_index

    # Calculate the center position of the group within the label
    # Adjust the offset calculation to place the annotation in the middle of the bar
    bar_width_half = settings['barwidth'] / 2
    group_center_offset = ((group_index - total_groups / 2) * (settings['barwidth'] + settings['bargap']) + bar_width_half + 0.05)
    
    return base_x + group_center_offset


def generate_single_lingress_plot(df_met_data, df_var_data, settings):
    """
    Generates a linear regression plot for a given metabolite against an external variable using Plotly Graph Objects.
    
    Parameters:
    df_met_data : pd.DataFrame
        DataFrame containing metabolomics data with one of the columns being the metabolite of interest.
    df_var_data : pd.DataFrame
        DataFrame containing the external variable data with one of the columns being the variable of interest.
    settings : dict
        Settings for the plot, such as 'barwidth' and 'bargap'.

    Returns:
    go.Figure
        A Plotly Graph Object figure of the linear regression plot.
    dict
        Dictionary containing regression statistics (slope, intercept, r_value, p_value, std_err).
    """
    
    # Extract column names for hover text
    sample_names = df_var_data.columns[1:]
    
    # Extract the metabolite and variable names
    met_name = df_met_data['Compound'].iloc[0]
    var_name = df_var_data['Variable'].iloc[0]
    
    # Extract the relevant data only
    met_values = df_met_data.iloc[0, 2:].astype(float)
    var_values = df_var_data.iloc[0, 1:].astype(float)
    
    # Filter out NaN values and ensure equal lengths
    valid_indices = (~var_values.isna()) & (~met_values.isna())
    var_values_filtered = var_values[valid_indices]
    met_values_filtered = met_values[valid_indices]

    # Adjusting the sample_names to match the filtered data
    sample_names_filtered = sample_names[valid_indices]

    # Determine hover text for each data point
    hover_texts = [sample_name for sample_name in sample_names_filtered]
    
    # Perform linear regression
    slope, intercept, r_value, p_value, std_err = linregress(var_values_filtered, met_values_filtered)
    
    # Determine min and max values for x and y axes
    y_min, y_max = met_values_filtered.min(), met_values_filtered.max()
    y_mid = (y_min + y_max) / 2

    # Create a scatter plot with a regression line
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=var_values_filtered, 
        y=met_values_filtered, 
        mode='markers', 
        name='Data',
        marker=dict(
            size=settings['datapoint_size'],
            color=settings['datapoint_color']
        ),
        text=hover_texts,
        hoverinfo='text'
    ))
    fig.add_trace(go.Scatter(
        x=var_values_filtered, 
        y=intercept + slope * var_values_filtered, 
        mode='lines', 
        name='Fit',
        line=dict(
            width=settings['line_thickness'],
            color=settings['line_color']
        ),
        opacity=settings['line_opacity']
    ))
    
    fig.update_layout(
        xaxis_title=var_name,
        yaxis_title=met_name,
        autosize=False,
        showlegend=False,
        plot_bgcolor='white',
        paper_bgcolor='white',
        width=settings['width'],
        height=settings['height'],
        xaxis=dict(
            title_font=dict(  # Sets the font for the x-axis title
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            ),
            tickfont=dict(  # Sets the font for the x-axis ticks
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            )
        ),
        yaxis=dict(
            title_font=dict(  # Sets the font for the y-axis title
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            ),
            tickfont=dict(  # Sets the font for the y-axis ticks
                family=settings['font_selector'],
                size=settings['font_size'],
                color='black'
            ),
            tickmode='array',
            tickvals=[y_min, y_mid, y_max],
            ticktext=[f'{y_min:.1e}', f'{y_mid:.1e}', f'{y_max:.1e}']
        ),
    )
    
    # Add annotation for stats if required
    if settings.get('show_stats', False):
        stats_text = (
            f"Slope: {slope:.3f} ± {std_err:.3f}<br>"
            f"R²: {r_value**2:.3f}<br>"
            f"P-value: {p_value:.3g}"
        )
        fig.add_annotation(
            x=0.5, y=1.05,  # Position the annotation at the top center
            xref="paper", yref="paper",
            text=stats_text,
            showarrow=False,
            font=dict(
                family=settings['font_selector'],
                size=settings['font_size'],
                color="black"
            ),
            align="center",
            bgcolor="white"
        )

    # Regression statistics
    stats = {
        'slope': slope,
        'intercept': intercept,
        'r_value': r_value,
        'p_value': p_value,
        'std_err': std_err,
        'r_squared': r_value**2
    }

    return fig, stats


def filter_and_order_isotopologue_data_by_met_class(df_iso, met_classes, df_class=df_met_group_list):
    """
    Filter and order df_iso based on met_classes using the df_class for mapping.

    Parameters:
    ----------
    df_iso : pandas.DataFrame
        The isotopologue data DataFrame.
    met_classes : list
        List of user-selected metabolite classes.
    df_class : pandas.DataFrame
        DataFrame containing pathway class and analyte name mapping.

    Returns:
    -------
    pandas.DataFrame
        The filtered and ordered DataFrame.
    pandas.DataFrame
        DataFrame containing compounds and their pathway classes.
    """
    
    # Filter the df_class to include only the selected classes
    filtered_df_class = df_class[df_class['pathway_class'].isin(met_classes)]
    
    # Merge the df_iso with the filtered df_class to filter and retain order
    merged_df = pd.merge(filtered_df_class, df_iso, left_on='analyte_name', right_on='Compound', how='inner')
    
    # Sort the merged DataFrame based on the order of met_classes
    merged_df['class_order'] = merged_df['pathway_class'].apply(lambda x: met_classes.index(x))
    sorted_df = merged_df.sort_values(by=['class_order', 'analyte_name']).drop(columns=['class_order'])
    
    # Select only the columns present in df_iso for the final output
    final_df = sorted_df[df_iso.columns]
    
    # Create a DataFrame with compound metadata
    compound_metadata_df = merged_df[['Compound', 'pathway_class']].drop_duplicates().reset_index(drop=True)
    
    return final_df, compound_metadata_df