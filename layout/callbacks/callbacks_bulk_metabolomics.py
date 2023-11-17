# callbacks_bulk_metabolomics

import io
import pandas as pd
import numpy as np
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import html, dcc, no_update, callback_context

from app import app
from layout.toast import generate_toast
from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, generate_single_met_iso_figure, add_p_value_annotations_iso, generate_single_met_pool_figure, add_p_value_annotations_pool


@app.callback(
[
    Output('metabolomics-plot-container', 'children'),
    Output('toast-container', 'children', allow_duplicate=True)
],
    Input('generate-metabolomics', 'n_clicks'),
[
    State('store-data-pool', 'data'),
    State('store-data-iso', 'data'),
    State('store-met-classes', 'data'),
    State('store-data-normalization', 'data'),
    State('store-data-order', 'data'),
    State('store-p-value-metabolomics', 'data'),
    State('store-settings-metabolomics', 'data')
],
    prevent_initial_call=True
)
def display_met_data(n_clicks, pool_data, iso_data, met_classes, met_normalization, met_groups, pvalue_info, settings):
    """
    Generates and displays metabolomics data visualizations based on various user inputs and selections.
    
    Parameters:
    - n_clicks (int): Number of times the generate-metabolomics button has been clicked.
    - pool_data (json): JSON data from the pooled metabolite data.
    - iso_data (json): JSON data from the isotopologue data.
    - met_classes (dict): User-selected metabolite classes.
    - met_normalization (dict): User-selected normalization variables.
    - met_groups (dict): User-defined sample groups.
    - pvalue_info (dict): P-value settings and configurations.
    - settings (dict): Additional settings for the visualizations.
    
    Returns:
    - html.Div: A div containing the generated visualizations.
    - no_update: No update for the 'intermediate-toast-content-2' data, or a toast message if needed.
    """
    
    ctx = callback_context
    
    # Identify which input triggered the callback
    if not ctx.triggered:
        button_id = 'No clicks yet'
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Execute the function only if the generate-metabolomics button was clicked
    if button_id == 'generate-metabolomics' and n_clicks > 0:
        # Validation: Check if necessary user inputs are provided
        # Each validation step returns a toast message if the validation fails

        # Validate the presence of pool data
        if pool_data is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Upload a valid metabolomics file.")
        
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')
        
        
        
        # Initialize bool variable to check if isotopologue data is present
        df_iso = None
        
        # Reas isotopologue data if available
        if iso_data is not None:
            iso_json_file = io.StringIO(iso_data)
            df_iso = pd.read_json(iso_json_file, orient='split')
            
            iso_present = True
        else:
            iso_present = False
        
        if iso_present and (df_iso['Compound'].isin(['group']).any()):
            df_iso = df_iso[~df_iso['Compound'].isin(['group'])]
            df_iso = df_iso.reset_index(drop=True)    
        
        # Check if the user has selected any metabolite classes  and if not return an error toast
        if not met_classes or met_classes['selected_values'] is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected metabolite classes. Refer to 'Select Metabolite Classes to be Displayed'.")
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        # Check if the user has selected the normalization variables and if not return an error toast
        if not met_normalization:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected normalization variables for the data (possible to have none). Refer to 'Change Normalization Variables'.")
        
        # Filter met_groups to include only items where the value is not None from the Dynamic Input of the user
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        
        normalization_list = met_normalization['selected_values']
        selected_met_classes = met_classes['selected_values']
        
        df_pool_normalized = normalize_met_pool_data(df_pool, grouped_samples, normalization_list)
        df_pool_normalized_grouped = group_met_pool_data(df_pool_normalized, selected_met_classes)
        
        df_pool_normalized_groupby = df_pool_normalized_grouped.groupby('pathway_class', sort=False)
               
        figures_mets = []
        # Iterate over each group of pathway_class
        for pathway, group_df in df_pool_normalized_groupby:
            
            # Append button and an empty container for graphs
            figures_mets.append(html.Div([
                html.H3(pathway, className='met-class-style')
            ]))
            
            # Iterate over each row in the grouped_df and generate the graphs
            for index, row in group_df.iterrows():
                # Add metabolite name to when a new row is read from the metabolite pool df
                met_name = row['Compound']
                figures_mets.append(html.H5(met_name, className='met-name-style'))
                
                # Create a new dbc Row for each metabolite
                dbc_row = dbc.Row(children=[])  
                
                # FOR ISO DATA
                # Get the same metabolite isotopologue data if iso_present is True
                if iso_present is True:
                    df_met_iso = df_iso[df_iso['Compound'] == met_name]
                    
                    figure_met_iso = generate_single_met_iso_figure(df_met_iso, grouped_samples, settings)
                    
                    # Add p-value components to the graph if the user stored comparison
                    if pvalue_info is not None:

                        pvalue_comparisons = pvalue_info['combinations']
                        pvalue_numerical = pvalue_info['numerical_bool']
                        figure_met_iso = add_p_value_annotations_iso(figure_met_iso, df_met_iso, grouped_samples, pvalue_comparisons, pvalue_numerical, settings)
                    
                    iso_filename = 'iso_' + str(met_name)
                    
                    dbc_row.children.append(dbc.Col(
                                                dcc.Graph(
                                                    figure=figure_met_iso,
                                                    config={
                                                    'toImageButtonOptions': {
                                                        'format': 'svg',
                                                        'filename': iso_filename,
                                                        'height': None,
                                                        'width': None,
                                                    }
                                                }), 
                                                className='bulk-met-graph-col'))
                
                
                df_met_pool = pd.DataFrame([row])
                figure_met_pool = generate_single_met_pool_figure(df_met_pool, grouped_samples, settings)
                
                # Add p-value components to the graph if the user stored comparison
                if pvalue_info is not None:
                    
                    pvalue_comparisons = pvalue_info['combinations']
                    pvalue_numerical = pvalue_info['numerical_bool']
                    figure_met_pool = add_p_value_annotations_pool(figure_met_pool, pvalue_comparisons, pvalue_numerical, settings)

                pool_filename = 'pool_' + str(met_name)
                
                # Add the pool data graph as a dbc Col to the dbc Row
                dbc_row.children.append(dbc.Col(
                                            dcc.Graph(
                                                figure=figure_met_pool,
                                                config={
                                                'toImageButtonOptions': {
                                                    'format': 'svg',
                                                    'filename': pool_filename,
                                                    'height': None,
                                                    'width': None,
                                                }
                                            }), className='bulk-met-graph-col'))

                # Add the completed dbc Row to your list
                figures_mets.append(dbc_row)

        # Continue as before with dbc_rows_list ...
        dbc_rows_list = []

        for element in figures_mets:
            if isinstance(element, dbc.Row):
                dbc_rows_list.append(element)
            else:
                # For the headers (, pathway_class), adjust this as needed for desired styling
                dbc_rows_list.append(dbc.Row(dbc.Col(element, style={'marginBottom': 20, 'marginTop': 20, 'textAlign': 'center'})),)

        return html.Div(dbc_rows_list), no_update
    

        
         
        
    else:
        return no_update
    

