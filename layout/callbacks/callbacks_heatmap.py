# callbacks_heatmap.py

import plotly.utils
import io
import pandas as pd
import json
from plotly.graph_objects import Figure
from dash.dependencies import Input, Output, State
from dash import html, dcc, callback_context, no_update

from app import app
from layout.toast import generate_toast
from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, generate_group_significance, transform_log2_and_adjust_control_data, generate_individual_heatmap, compile_met_pool_ratio_data

@app.callback(
[
    Output('bulk-heatmap-control-group-dropdown', 'options'),
    Output('custom-heatmap-control-group-dropdown', 'options')
],
    Input('store-data-order', 'data')
)
def update_heatmap_dropdown_options(grouped_samples):
    '''
    Updates the dropdown options for the heatmap plots based on available grouped sample data.
    
    Parameters:
    ----------
    grouped_samples : dict
        Dictionary containing grouped sample data from stored order.
        
    Returns:
    -------
    tuple
        Tuple containing lists of updated dropdown options for both custom and bulk heatmap control groups.
    '''
    
    ctx = callback_context

    # Return a placeholder option if no grouped sample data is available
    if grouped_samples is None or not grouped_samples or all(len(group) == 0 for group in grouped_samples.values()):
        placeholder_option = [{'label': 'Group Sample Replicates First...', 'value': 'placeholder', 'disabled': True}]
        return placeholder_option, placeholder_option
    
    if ctx.triggered:  # If the callback was triggered by user input
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'store-data-order':
            
            # Update options for heatmaps with unique_group_values, which now reflect the latest order from grouped_samples
            heatmap_control_options = [{'label': key, 'value': key} for key in grouped_samples.keys()]  # All options available for heatmaps

            return (heatmap_control_options,
                    heatmap_control_options)
        
        else:
            no_update
    else:
        no_update


@app.callback(
[
    Output('bulk-heatmap-plot-container', 'children'),
    Output('store-bulk-heatmap-plot', 'data'),
    Output('toast-container', 'children', allow_duplicate=True)
],
    Input('generate-bulk-heatmap-plot', 'n_clicks'),
[
    State('store-data-pool', 'data'),
    State('store-met-classes', 'data'),
    State('store-data-normalization', 'data'),
    State('store-data-order', 'data'),
    State('bulk-heatmap-control-group-dropdown', 'value'),
    State('store-bulk-heatmap-settings', 'data'),
    State('store-metabolite-ratios', 'data')
],
    prevent_initial_call=True
)
def display_bulk_heatmap_plot(n_clicks, pool_data, met_classes, met_normalization, met_groups, ctrl_group, settings, met_ratio_selection):
    '''
    Display the heatmap plot based on user-selected parameters and provided data. 
    The function also stores a JSON representation of the plot for later use.
    
    Parameters:
    ----------
    n_clicks : int
        Number of times the 'Generate Heatmap Plot' button is clicked.
    pool_data : dict
        Data from the data pool.
    met_classes : dict
        Selected metabolic classes for the bulk heatmap.
    met_normalization : dict
        Selected normalization methods.
    met_groups : dict
        Grouping of data.
    ctrl_group : str
        Selected control group for the bulk heatmap.
    settings: dict
        Selected or placeholder settings for the bulk heatmap
    met_ratio_selection : list
        List of dictionaries for user selected metabolite ratios
        
    Returns:
    -------
    list
        A list of HTML Divs containing heatmap plots.
    json
        JSON representation of the created heatmap plots.
    '''
    
    ctx = callback_context
    
    # Initialize the plotly go.Figure object for later
    fig = Figure()
    
    # Identify which input triggered the callback
    if not ctx.triggered:
        triggered_id  = 'No clicks yet'
    else:
        triggered_id  = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Execute the function only if the generate-metabolomics button was clicked
    if triggered_id  == 'generate-bulk-heatmap-plot' and n_clicks > 0:
        if pool_data is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Upload a valid metabolomics file.")
            
        # Check if the user has selected a control group for the heatmap        
        if ctrl_group is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Select a control group for the heatmap.")

        # Check if the user has selected any metabolite classes  and if not return an error toast
        if not met_classes or met_classes['selected_values'] is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Not selected metabolite classes. Refer to 'Select Metabolite Classes to be Displayed'.")
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        # Check if the user has selected the normalization variables and if not return an error toast
        if not met_normalization:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Not selected normalization variables for the data (possible to have none). Refer to 'Change Normalization Variables'.")
        


        # Reading and processing the data
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')

        # Further data processing steps involving grouping, normalization, and log2 transformation
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        normalization_list = met_normalization['selected_values']
        selected_met_classes = met_classes['selected_values']
        
        # Control columns based on user selection
        ctrl_cols = grouped_samples[ctrl_group]
        
        # Applying various data processing steps on the dataframe
        df_pool_normalized = normalize_met_pool_data(df_pool, grouped_samples, normalization_list)
        df_pool_normalized_grouped = group_met_pool_data(df_pool_normalized, selected_met_classes)
        
        # If metabolite ratios are in the selected sample class, then the metabolite ratio dataframe is
        # compiled and added to the end of the pool data dataframe
        if 'metabolite ratios' in selected_met_classes:
            df_ratio = compile_met_pool_ratio_data(df_pool_normalized, met_ratio_selection)
            df_pool_normalized_grouped = pd.concat([df_pool_normalized_grouped, df_ratio])
        
        group_significance = generate_group_significance(df_pool_normalized_grouped, grouped_samples)

        # Process control group data by calculating non-zero averages and adjust other values accordingly
        df_heatmap_ready = transform_log2_and_adjust_control_data(df_pool_normalized_grouped, grouped_samples, ctrl_group)
        
        heatmap_list = []
        
        for pathway_name, pathway_df in df_heatmap_ready.groupby('pathway_class', sort=False):
            heatmap_list.append(html.Div([
                html.H3(pathway_name, className='met-class-style')
            ]))
            
            heatmap = generate_individual_heatmap(pathway_df, grouped_samples, settings, group_significance, ctrl_cols)
            if heatmap:
                
                filename = 'heatmap' + '_' + str(pathway_name)
                
                heatmap_list.append(
                    dcc.Graph(figure=heatmap,
                    className='graph-container',
                    config={
                        'toImageButtonOptions': {
                            'format': 'svg',
                            'filename': filename,
                            'height': None,
                            'width': None,
                        }
                    }
                ))
                
            else:
                print(f"An issue occurred while generating the heatmap for pathway: {pathway_name}")
            
        
        figures_json = json.dumps(heatmap_list, cls=plotly.utils.PlotlyJSONEncoder)
        
        if heatmap_list:
            return heatmap_list, figures_json, no_update
        else:
            return no_update, no_update, no_update

    return no_update, no_update, no_update


@app.callback(
[
    Output('bulk-isotopologue-heatmap-plot-container', 'children'),
    Output('store-bulk-isotopologue-heatmap-plot', 'data'),
    Output('toast-container', 'children', allow_duplicate=True)
],
    Input('generate-bulk-isotopologue-heatmap-plot', 'n_clicks'),
[
    State('store-data-iso', 'data'),
    State('store-met-classes', 'data'),
    State('store-data-order', 'data'),
    State('store-bulk-isotopologue-heatmap-settings', 'data')
],
    prevent_initial_call = True
)
def display_bulk_isotopologue_heatmap_plot(n_clicks, iso_data, met_classes, met_groups, settings):
    '''
    Display the heatmap plot of isotopologue data if it is available in the uploaded data
    based on user-selected parameters and provided data. 
    The function also stores a JSON representation of the plot for later use.
    
    Parameters:
    ----------
    n_clicks : int
        Number of times the 'Generate Heatmap Plot' button is clicked.
    iso_data : dict
        Isotopologue data from uploaded file.
    met_classes : dict
        Selected metabolic classes for the bulk heatmap.
    met_groups : dict
        Grouping of data.
    settings: dict
        Selected or placeholder settings for the bulk heatmap
        
    Returns:
    -------
    list
        A list of HTML Divs containing heatmap plots.
    json
        JSON representation of the created heatmap plots.
    '''
    
    ctx = callback_context
    
    # Initialize the plotly go.Figure object for later
    fig = Figure()
    
    # Identify which input triggered the callback
    if not ctx.triggered:
        triggered_id  = 'No clicks yet'
    else:
        triggered_id  = ctx.triggered[0]['prop_id'].split('.')[0]
        
         # Execute the function only if the generate-bulk-isotopologue-heatmap button was clicked
        if triggered_id  == 'generate-bulk-isotopologue-heatmap-plot' and n_clicks > 0:
            
            if iso_data is None:
                return no_update, no_update, generate_toast("error", 
                                                            "Error", 
                                                            "No uploaded isopotologue (labelling) data detected.")
    
            # Check if the user has selected any metabolite classes  and if not return an error toast
            if not met_classes or met_classes['selected_values'] is None:
                return no_update, no_update, generate_toast("error", 
                                                            "Error", 
                                                            "Not selected metabolite classes. Refer to 'Select Metabolite Classes to be Displayed'.")
        
            # Check if the user has entered any sample groups  and if not return an error toast
            if not met_groups:
                return no_update, no_update, generate_toast("error", 
                                                            "Error", 
                                                            "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")


            # Reading and processing the data
            iso_json_file = io.StringIO(iso_data)
            df_iso = pd.read_json(iso_json_file, orient='split')
            
            # Further data processing steps involving grouping, normalization, and log2 transformation
            grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
            selected_met_classes = met_classes['selected_values']
            
            # Flatten grouped_samples to get a list of all relevant sample columns and filter the iso df
            # Extract the metabolite names column
            iso_main_cols = df_iso.iloc[:, 0:2]
            all_samples = [sample for group_samples in grouped_samples.values() for sample in group_samples]
            df_iso_filter = df_iso[all_samples]
            
            # Concatenate the metabolite names column back to the filtered DataFrame
            df_pool_filtered = pd.concat([iso_main_cols, df_iso_filter], axis=1)
            
            # Filter to get data where the C_label is not 0
            df_iso_label = df_pool_filtered[df_pool_filtered['C_Label'] != 0]

            # Set 'Compound' as index and sum values, then reset index.
            # Note that you should sum across the rows (axis=1) for each unique 'Compound', which is now your index.
            df_iso_label_sum = df_iso_label.groupby('Compound').sum()

            df_iso_label_sum = df_iso_label_sum.drop(columns=['C_Label'])
            df_iso_label_sum.reset_index(inplace=True)

            df_iso_label_sum_grouped = group_met_pool_data(df_iso_label_sum, selected_met_classes)
        
            group_significance = generate_group_significance(df_iso_label_sum_grouped, grouped_samples)

            heatmap_list = []
            


            for pathway_name, pathway_df in df_iso_label_sum_grouped.groupby('pathway_class', sort=False):
                heatmap_list.append(html.Div([
                    html.H3(pathway_name, className='met-class-style')
                ]))
                
                heatmap = generate_individual_heatmap(pathway_df, grouped_samples, settings, group_significance, [], data_type='iso')
                if heatmap:
                    
                    filename = 'heatmap' + '_' + str(pathway_name)
                    
                    heatmap_list.append(
                        dcc.Graph(figure=heatmap,
                        className='graph-container',
                        config={
                            'toImageButtonOptions': {
                                'format': 'svg',
                                'filename': filename,
                                'height': None,
                                'width': None,
                            }
                        }
                    ))
                    
                else:
                    print(f"An issue occurred while generating the heatmap for pathway: {pathway_name}")
        
            figures_json = json.dumps(heatmap_list, cls=plotly.utils.PlotlyJSONEncoder)
        
            if heatmap_list:
                return heatmap_list, figures_json, no_update
        
            else:
                return no_update, no_update, no_update

    return no_update, no_update, no_update
            
            


@app.callback(
[
    Output('custom-heatmap-plot-container', 'children'),
    Output('store-custom-heatmap-plot', 'data'),
    Output('toast-container', 'children', allow_duplicate=True)
],
    Input('generate-custom-heatmap-plot', 'n_clicks'),
[
    State('store-data-pool', 'data'),
    State('store-data-normalization', 'data'),
    State('store-data-order', 'data'),
    State('custom-heatmap-control-group-dropdown', 'value'),
    State('custom-heatmap-dropdown-list', 'value'),
    State('store-custom-heatmap-settings', 'data')
],
    prevent_initial_call=True
)
def display_custom_heatmap_plot(n_clicks, pool_data, met_normalization, met_groups, ctrl_group, custom_met_list, settings):
    '''
    Generate and display a custom heatmap plot based on user-selected metabolites and groups.
    The function also stores a JSON representation of the plot for later use.

    Parameters:
    ----------
    n_clicks : int
        Number of times the 'Generate Heatmap Plot' button is clicked.
    pool_data : JSON
        Stored metabolomics pool data.
    met_normalization : dict
        Selected normalization methods for the heatmap.
    met_groups : dict
        Grouping of samples for the heatmap.
    ctrl_group : str
        Selected control group for comparison.
    custom_met_list : list
        List of selected metabolites for the custom heatmap.
    settings : dict
        Selected or placeholder settings for the custom heatmap

    Returns:
    -------
    list
        A list of HTML Divs containing custom heatmap plots.
    json
        JSON representation of the created custom heatmap plots.
    '''
    
    # Get context to identify the triggering input
    ctx = callback_context
    
    # Determine the ID of the triggering input
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None
    
    # Execute the function only if the generate button is clicked and necessary data is available
    if triggered_id == 'generate-custom-heatmap-plot':
        # Check if there is any uploaded valid metabolomics data        
        if pool_data is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Upload a valid metabolomics file.")
            
        # Check if the user has selected a control group for the heatmap        
        if ctrl_group is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Select a control group for the heatmap.")
            
        # Check if the user has entered any sample groups  and if not return an error toast    
        if custom_met_list is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Enter at least one metabolite to the custom heatmap list.")  
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        # Check if the user has selected the normalization variables and if not return an error toast
        if not met_normalization:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Not selected normalization variables for the data (possible to have none). Refer to 'Change Normalization Variables'.")
        
        # Load and preprocess the data based on the provided states
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        normalization_list = met_normalization['selected_values']
        ctrl_cols = grouped_samples[ctrl_group]
        
        # Normalize and preprocess the data for heatmap generation
        df_pool_normalized = normalize_met_pool_data(df_pool, grouped_samples, normalization_list)
        df_pool_normalized['pathway_class'] = 'Custom-Heatmap'  # Assign a custom class for selected metabolites
        
        # Create a new column 'Custom-Heatmap' and configure it to be as the first column in the dataframe
        df_pool_normalized['pathway_class'] = 'Custom-Heatmap'
        columns_order = ['pathway_class'] + [col for col in df_pool_normalized if col != 'pathway_class']
        df_pool_normalized = df_pool_normalized[columns_order]
        
        df_heatmap_custom_met_list = df_pool_normalized[df_pool_normalized['Compound'].isin(custom_met_list)]
        df_heatmap_custom_met_list.set_index('Compound', inplace=True)
        df_heatmap_custom_met_list = df_heatmap_custom_met_list.loc[custom_met_list]
        df_heatmap_custom_met_list.reset_index(inplace=True)
        
        df_heatmap_ready = transform_log2_and_adjust_control_data(df_heatmap_custom_met_list, grouped_samples, ctrl_group)
        
        # Create a heatmap list object and append a custom header for the custom heatmap
        heatmap_list = []
        
        heatmap_list.append(html.Div([
                html.H3("Custom Heatmap", className='met-class-style')
            ]))
        # Generate a heatmap 
        heatmap = generate_individual_heatmap(df_heatmap_ready, grouped_samples, settings, None, ctrl_cols)
        if heatmap:
            heatmap_list.append(
                dcc.Graph(figure=heatmap,
                className='graph-container',
                config={
                    'toImageButtonOptions': {
                        'format': 'svg',
                        'filename': 'custom_heatmap',
                        'height': None,
                        'width': None,
                    }
                }
            ))
        
        # Convert heatmap figure to json for storage
        figures_json = json.dumps(heatmap_list, cls=plotly.utils.PlotlyJSONEncoder)
        
        # Return the generated heatmap elements and the stored JSON data
        return heatmap_list, figures_json, no_update
    
    # Prevent update if the generate button isn't clicked
    return no_update, no_update, no_update
        

@app.callback(
    Output('custom-heatmap-dropdown-list', 'options'),
    Input('store-data-pool', 'data'),
)
def update_custom_heatmap_metabolite_list_options(pool_data):
    '''
    Update the options in the metabolite dropdown list for the custom heatmap plot.
    This function is activated when new data is available in the 'store-data-pool'. It processes 
    the pool data to extract and sort unique metabolite compounds, and then updates the dropdown 
    options to enable user selection of metabolites for the heatmap display.

    Parameters:
    ----------
    pool_data : json
        JSON-formatted string containing the metabolite pool data DataFrame.

    Returns:
    -------
    list
        A list of dictionaries with label-value pairs for the dropdown options, 
        representing the metabolites available for selection in the heatmap.
    '''
    
    if pool_data is None:
        # If there's no data, returning an empty options list
        return []
    else:
        # Converting the JSON string back to a DataFrame
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')
        
        # Getting unique compounds from the DataFrame and sorting them in a case-insensitive manner
        unique_compounds = sorted(df_pool['Compound'].unique(), key=lambda x: x.lower())
        
        # Creating a list of option dictionaries to be used in the dropdown component
        options = [{'label': compound, 'value': compound} for compound in unique_compounds]
        
        return options
    
    
