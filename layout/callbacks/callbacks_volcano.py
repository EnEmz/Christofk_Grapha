# callbacks_volcano.py

import pandas as pd
import numpy as np
import io
import json
import plotly.utils
import plotly.graph_objects as go 
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import dcc, no_update, callback_context

from app import app
from layout.toast import generate_toast
from layout.utilities_layout import generate_available_dropdown_options
from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, ttest_volcano, assign_color, generate_volcano_plot, calculate_offsets_for_volcano_annotations

@app.callback(
[
    Output('volcano-control-group-dropdown', 'options'),
    Output('volcano-condition-group-dropdown', 'options')
],
[
    Input('store-data-order', 'data'),
    Input('volcano-control-group-dropdown', 'value'),
    Input('volcano-condition-group-dropdown', 'value')
]
)
def update_volcano_dropdown_options(grouped_samples, volcano_control_group, volcano_condition_group):
    '''
    Updates the dropdown options for the volcano plot based on the selected group values and available data.
    
    Parameters:
    ----------
    grouped_samples : dict
        Dictionary containing grouped sample data.
        
    volcano_control_group : str
        The selected value in the volcano control group dropdown.
        
    volcano_condition_group : str
        The selected value in the volcano condition group dropdown.
        
    Returns:
    -------
    tuple
        Tuple containing lists of updated dropdown options for volcano control and condition groups.
    '''

    ctx = callback_context  # Getting context to identify which input triggered the callback
    
    # Return a placeholder option if no grouped sample data is available
    if grouped_samples is None or not grouped_samples or all(len(group) == 0 for group in grouped_samples.values()):
        placeholder_option = [{'label': 'Group Sample Replicates First...', 'value': 'placeholder', 'disabled': True}]
        return placeholder_option, placeholder_option
    
    # Initialize dropdown options to empty lists
    volcano_control_options, volcano_condition_options = [], []
    
    if ctx.triggered:  # If the callback was triggered by user input
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        unique_labels_for_dropdown = [key for key in grouped_samples.keys()]  # Maintain the order of grouped samples

        if trigger_id == 'store-data-order':
            # Use the order from grouped_samples to update all dropdowns
            volcano_control_options = [{'label': key, 'value': key} for key in unique_labels_for_dropdown]
            volcano_condition_options = volcano_control_options.copy()  # Clone the control options for condition dropdown
        else:
            # Only update the dropdown that didn't trigger the callback
            if trigger_id == 'volcano-control-group-dropdown':
                # Disable the selected control group in condition dropdown
                volcano_condition_options = generate_available_dropdown_options(volcano_control_group, unique_labels_for_dropdown)
                # volcano_control_options should be initialized with the updated data
                volcano_control_options = [{'label': key, 'value': key} for key in unique_labels_for_dropdown]
            elif trigger_id == 'volcano-condition-group-dropdown':
                # Disable the selected condition group in control dropdown
                volcano_control_options = generate_available_dropdown_options(volcano_condition_group, unique_labels_for_dropdown)
                # volcano_condition_options should be initialized with the updated data
                volcano_condition_options = [{'label': key, 'value': key} for key in unique_labels_for_dropdown]
            else:
                # If neither of the specific volcano dropdowns triggered the callback, 
                # then all dropdowns should be updated normally without disabling any options
                volcano_control_options = [{'label': key, 'value': key} for key in unique_labels_for_dropdown]
                volcano_condition_options = volcano_control_options.copy()  # Clone the control options for condition dropdown
    else:
        # No trigger means this is the initial load, use default sample order
        volcano_control_options = [{'label': key, 'value': key} for key in grouped_samples.keys()]
        volcano_condition_options = volcano_control_options.copy()  # Clone the control options for condition dropdown

    return (volcano_control_options,
            volcano_condition_options)
            
            

@app.callback(
[
    Output('volcano-plot-container', 'children'),
    Output('store-volcano-plot', 'data'),
    Output('toast-container', 'children', allow_duplicate=True)
],
[
    Input('generate-volcano-plot', 'n_clicks'),
    Input('volcano-search-dropdown', 'value')
],
[
    State('store-data-pool', 'data'),
    State('store-met-classes', 'data'),
    State('store-data-normalization', 'data'),
    State('store-met-groups', 'data'),
    State('volcano-control-group-dropdown', 'value'),
    State('volcano-condition-group-dropdown', 'value'),
    State('store-volcano-settings', 'data')
],
    prevent_initial_call = True
)
def display_volcano_plot(n_clicks, search_value, pool_data, met_classes, met_normalization, met_groups, ctrl_group, cond_group, settings):
    '''
    Generates and displays the volcano plot based on the user inputs and selected parameters.
    
    Parameters:
    ----------
    n_clicks : int
        Number of times the generate-volcano-plot button is clicked.
        
    search_value : str
        Metabolite name to highlight in the volcano plot.
        
    pool_data : json
        JSON formatted string containing the pool data.
        
    met_classes : dict
        Dictionary containing selected metabolite classes.
        
    met_normalization : dict
        Dictionary containing selected metabolites for normalization.
        
    met_groups : dict
        Dictionary containing grouped metabolite sample data.
        
    ctrl_group : str
        Control group selected by the user.
        
    cond_group : str
        Condition group selected by the user.
        
    settings : dict
        Settings to customize the generated volcano plot.
        
    Returns:
    -------
    tuple
        Tuple containing the dash html component of the plot and JSON formatted plot data.
    '''
    
    # Getting context to identify which input triggered the callback
    ctx = callback_context
    
    # Initialize the plotly go.Figure object for later
    fig = go.Figure()
    
    # Identify which input triggered the callback
    if not ctx.triggered:
        return no_update, no_update, no_update
    else:
        triggered_id  = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Execute the function only if generate-metabolomics button was clicked
    if triggered_id == 'volcano-search-dropdown' or (triggered_id == 'generate-volcano-plot' and n_clicks > 0):
        if pool_data is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Upload a valid metabolomics file.")
            
        # Check if the user has selected a control group for the heatmap        
        if ctrl_group is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Select a control group for the volcano plot.")
            
        # Check if the user has selected a control group for the heatmap        
        if cond_group is None:
            return no_update, no_update, generate_toast("error", 
                                                        "Error", 
                                                        "Select a condition group for the heatmap.")
            
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
        

        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')
        df_pool = df_pool.replace(0, 1000)  # Replacing 0 values
        
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        normalization_list = met_normalization['selected_values']
        selected_met_classes = met_classes['selected_values']
        
        # Normalizing and grouping the data
        df_pool_normalized = normalize_met_pool_data(df_pool, grouped_samples, normalization_list)
        df_pool_normalized_grouped = group_met_pool_data(df_pool_normalized, selected_met_classes)
        df_pool_normalized_grouped.drop('pathway_class', axis=1, inplace=True)
        
        # Creating a new dataframe to keep the data for volcano plot
        df_volcano = pd.DataFrame(columns=['MetNames', 'value_ctrl', 'value_cond', 'log2FC', 'p-value'])
        df_volcano['MetNames'] = df_pool_normalized_grouped['Compound']
        
        ctrl_cols = grouped_samples[ctrl_group]  # Directly accessing the control group columns using the group name
        cond_cols = grouped_samples[cond_group]  # Directly accessing the condition group columns using the group name
        
        # Data Preparation
        df_volcano['value_ctrl'] = df_pool_normalized_grouped[ctrl_cols].mean(axis=1)
        df_volcano['value_cond'] = df_pool_normalized_grouped[cond_cols].mean(axis=1)
        
        # Calculating the p-value between average values of control and condition groups from the ttest_volcano function
        df_volcano['p-value'] = df_pool_normalized_grouped.apply(ttest_volcano, axis=1, ctrl_cols=ctrl_cols, cond_cols=cond_cols)
        
        # Calculating log2FC and -log10(p-value)
        df_volcano['log2FC'] = np.log2(df_volcano['value_cond'] / df_volcano['value_ctrl'])
        df_volcano['logp-value'] = -np.log10(df_volcano['p-value'])
        
        # Defining cutoffs and assigning colors from the assign_color function
        FC_cutoff = settings['fc_value']
        third_pvalue_cutoff = 3
        second_pvalue_cutoff = 2
        first_pvalue_cutoff = 1.3
        
        # Assigning the color based on selected fold-change and p-value cutoff values
        df_volcano['color'] = df_volcano.apply(assign_color, 
                                      axis=1, 
                                      args=(FC_cutoff, 
                                            third_pvalue_cutoff, 
                                            second_pvalue_cutoff, 
                                            first_pvalue_cutoff,
                                            settings))
        
        # Generating the volcano plot
        fig = generate_volcano_plot(df_volcano, FC_cutoff, third_pvalue_cutoff, second_pvalue_cutoff, first_pvalue_cutoff, settings, search_value)
        
        
        # Convert plotly figure for storage in dcc.Store
        fig_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        
        filename = 'volcano_' + ctrl_group + '_' + cond_group
        
        # If a new volcano plot is being generated, clear previously clicked datapoints    
        return [dcc.Graph(
                    id='volcano-plot', 
                    figure=fig, 
                    className='graph-container',
                    config={
                        'toImageButtonOptions': {
                            'format': 'svg',
                            'filename': filename,
                            'height': None,
                            'width': None,
                        }
                    }
                )], fig_json, no_update
    
    else:
        return no_update, no_update, no_update
    
    
@app.callback(
    Output('volcano-plot', 'figure'),
[
    Input('store-volcano-clicked-datapoints', 'data'),
    Input('store-volcano-plot', 'data')
],
    State('store-volcano-settings', 'data'),
)
def update_volcano_plot_on_click(stored_points, stored_volcano_fig, settings):
    '''
    Update the volcano plot by adding annotations when data points are clicked.
    
    Parameters:
    ----------
    stored_points : list
        A list of dictionaries containing information of the clicked data points (x, y, and metabolite name).
        
    stored_volcano_fig : json
        A JSON representation of the existing volcano plot figure.
        
    Returns:
    -------
    plotly.graph_objs._figure.Figure
        An updated plotly Figure object with new annotations added based on the clicked points.
    '''
    
    ctx = callback_context
    
    # Identify which input triggered the callback
    if not ctx.triggered:
        return no_update
    else:
        triggered_id  = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if not stored_volcano_fig:
         raise PreventUpdate  # Prevent updating the figure if there is no stored figure data
    
    fig = go.Figure(json.loads(stored_volcano_fig))  # Load the existing figure from JSON
    
    # Clear existing annotations to avoid duplicates
    fig.update_layout(annotations=[])
    
    # Loop through the stored points and add annotations
    for point in stored_points:
        x = point['x']
        y = point['y']
        met_name = point['met_name']
        
        # Calculate the offsets for all points
        # offsets = calculate_offsets_for_volcano_annotations(point, stored_points)
        
        if x > 0: 
            ax=30 
        else: 
            ax=-30
            
        if y > 1.3: 
            ay=-30 
        else: 
            ay=30
        
        # Adding annotations to the figure
        fig.add_annotation(
            text=met_name,  # Metabolite name as the annotation text
            x=x,
            y=y,
            showarrow=True,  # Show arrows pointing to the annotated points
            ax=ax,
            ay=ay,
            standoff=8,  # Distance between the point and the start of the arrow
            arrowhead=1,
            arrowwidth=1,
            arrowsize=1,
            arrowcolor="#636363",
            font=dict(
                family=settings['font_selector'],
                size=settings['font_size'],               
                color="rgba(0,0,0,1)"  # Font color
            )
        )
    
    return fig  # Return the updated figure


@app.callback(
    Output('store-volcano-clicked-datapoints', 'data'),
[
    Input('generate-volcano-plot', 'n_clicks'),
    Input('volcano-plot', 'clickData'),
    Input('volcano-click-significant-points', 'n_clicks')
],
[
    State('store-volcano-clicked-datapoints', 'data'),
    State('store-volcano-plot', 'data'),
    State('store-volcano-settings', 'data')
]
)
def update_stored_on_click_datapoints(new_plot_clicks, clickData, sig_clicks, stored_points, stored_volcano_fig, settings):
    '''
    Update the stored data points for clicked data points in the volcano plot.

    Parameters:
    ----------
    new_plot_clicks: int
        The number of times the generate new volcano plot button was clicked
    clickData : dict
        Information of the point clicked by the user on the volcano plot.
    sig_clicks : int
        The number of times the significant points button has been clicked.
    stored_points : list
        A list of dictionaries containing information on the currently stored data points.
    stored_volcano_fig : json
        A JSON representation of the current state of the volcano plot figure.

    Returns:
    -------
    list
        An updated list of dictionaries with the stored data points reflecting new clicks,
        with the addition of significant points when requested by the user interaction.
    '''
    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate

    # Check if the figure data exists and has the necessary format
    if not stored_volcano_fig or 'data' not in stored_volcano_fig:
        raise PreventUpdate

    if stored_points is None:
        stored_points = []
    
    fig_data = json.loads(stored_volcano_fig)  # Parse the JSON to get a dictionary
    
    # Retrieve settings data for significance criteria
    FC_cutoff = settings.get('fc_value', 1)
    pvalue = settings.get('p_value', 0.05)
    pvalue_threshold = -np.log10(pvalue)
    
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'generate-volcano-plot':
        return []
    
    new_stored_points = stored_points.copy()  # Start with a copy of the current stored points
    
    # If the button for marking significant points is clicked
    if triggered_id == 'volcano-click-significant-points':
        # Find all significant points based on criteria
        significant_points = []
        for trace in fig_data['data']:
            for i, x in enumerate(trace['x']):
                if abs(x) >= FC_cutoff and trace['y'][i] >= pvalue_threshold:
                    significant_points.append({'x': x, 'y': trace['y'][i], 'met_name': trace['customdata'][i]})

        # Check if any significant points are not already marked
        unmarked_significant_points = [pt for pt in significant_points if pt not in stored_points]
        
        # If there are unmarked significant points, add them
        if unmarked_significant_points:
            stored_points.extend(unmarked_significant_points)
        else:  # If all significant points are marked, unmark them
            stored_points = [pt for pt in stored_points if pt not in significant_points]

        return stored_points

    # If a point on the plot is clicked
    if triggered_id == 'volcano-plot' and clickData:
        # Extract the clicked point's data
        new_point = { 'x': clickData['points'][0]['x'],
                      'y': clickData['points'][0]['y'],
                      'met_name': clickData['points'][0]['customdata'] }
        # Toggle the clicked point
        if new_point in stored_points:
            stored_points.remove(new_point)  # If it's already there, remove it
        else:
            stored_points.append(new_point)  # If not, add it

    return stored_points


@app.callback(
    Output('volcano-search-dropdown', 'options'),
    Input('store-volcano-plot', 'data')
)
def update_volcano_search_dropdown_options(stored_plot_json):
    '''
    Update the dropdown options in the volcano plot search dropdown based on the
    metabolites present in the stored volcano plot data.
    
    Parameters:
    ----------
    stored_plot_json : json
        JSON representation of the stored volcano plot figure.
        
    Returns:
    -------
    list
        A list of dictionaries, each containing a label and value pair representing
        a dropdown option.
    '''
    
    if stored_plot_json:
        # Convert the JSON string back to a plotly figure
        stored_fig = plotly.io.from_json(stored_plot_json)
        
        # Assuming that metabolite names are stored as point labels or some other trace attribute
        metabolite_names = []
        for trace in stored_fig.data:
            # Check if the trace has a text attribute, which holds the names of the metabolites
            if hasattr(trace, 'text'):
                # If text attribute is present, extend the metabolite names list with the names in this trace
                metabolite_names.extend(trace.text)
                
        metabolite_names = list(set(metabolite_names))  # Removing duplicates
        metabolite_names = sorted(metabolite_names, key=lambda s: s.lower())  # Sorting alphabetically, case-insensitive
        
        # Creating dropdown options as a list of dictionaries
        dropdown_options = [{'label': met_name, 'value': met_name} for met_name in metabolite_names]
        
        return dropdown_options  # Return the created dropdown options
    else:
        return []  # Return empty options if there is no data

