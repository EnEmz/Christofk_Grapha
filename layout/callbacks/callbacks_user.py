# callbacks_user.py

import io
import pandas as pd
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from dash import html, dcc, no_update, callback_context
import json

from app import app
from layout.config import normalization_preselected


# Met classes callback functions
@app.callback(
    Output('store-met-classes', 'data'),
    Input('update-classes', 'n_clicks'),
    State('met-class-checklist', 'value')
)
def store_met_classes(n_clicks, selected_values):
    """
    Store the selected metabolite classes when the update button is clicked.
    
    Parameters:
    n_clicks (int): Number of button clicks, used to trigger the callback.
    selected_values (list): The values selected in the checklist.
    
    Returns:
    dict or no_update: A dictionary containing the selected values, 
                            None if no values are selected,
                            or no_update if the callback was not triggered by the update button.
    """
    
    # Get the context to identify which Input triggered the callback
    ctx = callback_context    

    # Check if the callback was not triggered externally (e.g., on app load)
    if not ctx.triggered:
        return no_update
    
    # Extract the ID of the triggered component
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]  

    # Check if the update button was the component that triggered the callback
    if button_id == 'update-classes':
        if selected_values:
            return {'selected_values': selected_values}  # Return the selected values as a dictionary
        else:
            return no_update  # Return None if no values are selected
    
    # Prevent update if the function reaches this point without returning
    return no_update 


@app.callback(
    Output("met-class-checklist", "value"),
[
    Input("clear-classes", "n_clicks"),
    Input("select-all-classes", "n_clicks")
],
[
    State("met-class-checklist", "value"),
    State("met-class-checklist", "options")
]
)
def clear_select_all_met_classes(clear_clicks, select_clicks, selected_values, all_options):
    """
    Toggle the selected metabolite classes in the checklist based on "clear" or "select all" buttons being clicked.
    
    Parameters:
    clear_clicks (int): The number of times the "Clear" button has been clicked.
    select_clicks (int): The number of times the "Select All" button has been clicked.
    selected_values (list): The current selected values in the checklist.
    all_options (list): All options available in the checklist.
    
    Returns:
    list: An empty list if the "clear" button was clicked, otherwise a list of all classes if "select all" was clicked,
          or the current selected values if none were clicked.
    """
    
    # Get the context to identify which Input triggered the callback
    ctx = callback_context  
    
    
    
    # If no buttons were clicked, keep the current values
    if not ctx.triggered:
        return no_update

    # Get the button ID that was clicked
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Based on the button clicked, clear selections or select all options
    if button_id == 'clear-classes':
        return []  # Return an empty list to clear selections
    elif button_id == 'select-all-classes':
        # Return a list of all option values to select all
        return [option['value'] for option in all_options]

    # If neither button was clicked, do not update the selections
    return selected_values


# Normalization callback functions
@app.callback(
    Output('normalization-container', 'children'),
    Input('store-data-pool', 'data')
)
def generate_normalization_dropdown(pool_data):
    """
    Generate a dropdown for normalization options based on uploaded pool data.
    
    Parameters:
    pool_data (json): JSON-formatted string containing the pool data.
    
    Returns:
    html.Div: A container with a Dropdown and optionally a placeholder message.
    """
    # Determine whether to disable the dropdown based on the presence of pool_data
    disabled = not pool_data
    
    # Placeholder message displayed when no data is uploaded
    placeholder_message = html.Div(
        'Please upload a metabolomics data file to populate the normalization options.',
        className='modal-placeholder-message'
    ) if disabled else None  # Shown only if dropdown is disabled
    
    options = []  # List to store the dropdown options
    preselected_options = []  # List to store options that should be preselected
    
    if pool_data:  # Check if pool_data is available
        strings_to_check = normalization_preselected  # Keywords to identify relevant options
        
        # Read the pool data into a pandas DataFrame
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')
        
        # Loop through each keyword and each compound to identify matching options
        for string in strings_to_check:
            for compound in df_pool['Compound'].values:
                if string in compound:
                    # Add matching compounds as options and preselect them
                    options.append({'label': compound, 'value': compound})
                    preselected_options.append(compound)
    
    # Create a Dropdown component with the identified options and settings
    dropdown = dcc.Dropdown(
        id='normalization-dropdown-selector',
        options=options,
        value=preselected_options,  # Set initial value as the preselected options
        multi=True,
        disabled=disabled  # Control the dropdown's disabled state based on pool_data
    )
    
    # Return a container Div with the Dropdown and optionally the placeholder message
    return [html.Div([placeholder_message, dropdown])]



@app.callback(
    Output('store-data-normalization', 'data'),
    Input('update-normalization', 'n_clicks'),
    State('normalization-dropdown-selector', 'value'),
    prevent_initial_call=True
)
def store_selected_normalization(n_clicks, selected_values):
    """
    Store the selected normalization values when the update button is clicked.
    
    Parameters:
    n_clicks (int): Number of button clicks. Used to trigger the callback.
    selected_values (list): The selected values from the dropdown.
    
    Returns:
    dict: A dictionary containing the selected values, or None if no values are selected.
    """
    
    # Check if no values are selected in the dropdown
    if selected_values is None:
        return no_update  # Return None if no values are selected
    
    # Return the selected values as a dictionary
    return {'selected_values': selected_values}


# Sample group selection callback functions
@app.callback(
    Output('group-input-container', 'children'),
    Input('store-data-pool', 'data')
)
def display_met_groups(pool_data):
    """
    Display and possibly change metabolite groups based on uploaded metabolomics data file.
    
    Parameters:
    pool_data (json): Stored data of uploaded metabolomics file.
    
    Returns:
    list: A list of HTML Div components containing labels and inputs for metabolic groups.
    """
    # Check if there's any data uploaded
    if not pool_data:
        # Return a placeholder message if there's no uploaded data
        return html.Div(
            "Please upload a metabolomics data file to display metabolic groups.",
            className='modal-placeholder-message'
        )
    
    # Read the pool data into a DataFrame
    pool_json_file = io.StringIO(pool_data)
    df_pool = pd.read_json(pool_json_file, orient='split')
    
    # Extract sample names from the DataFrame columns
    sample_names = df_pool.columns.tolist()[1:]
    
    # Create and return a list of HTML components for each sample/metabolite group
    return [
        html.Div([
            # Display the sample/metabolite group name as a label
            html.Label(var_name, className='met-groups-label'),
            # Create a text input for each sample/metabolite group
            dcc.Input(
                id={'type': 'dynamic-input-met-groups', 'index': var_name},
                type='text',
                value='',
                maxLength=14,
                className='met-groups-input'
            ),
        ], className='met-groups-div') for var_name in sample_names
    ]

@app.callback(
    Output('store-met-groups', 'data'),
    Input('update-groups', 'n_clicks'),
[
    State({'type': 'dynamic-input-met-groups', 'index': ALL}, 'id'),
    State({'type': 'dynamic-input-met-groups', 'index': ALL}, 'value')
],
    prevent_initial_call=True
)
def store_met_groups(n_clicks, input_ids, input_values):
    """
    Store the metabolite group variables in dcc.Store after the "update-groups" button is pressed.
    
    Parameters:
    n_clicks (int): The number of times the "update-groups" button has been clicked.
    input_ids (list): A list of dictionaries containing the IDs of the dynamic inputs.
    input_values (list): A list of values entered in the dynamic inputs.
    
    Returns:
    dict or None: A dictionary of grouped values or None if no valid values are provided.
    """
    # Get the context to identify which input has triggered the callback
    ctx = callback_context  
    
    # If no input has triggered the callback, do nothing
    if not ctx.triggered:  
        return no_update
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]  # Extract the ID of the triggering input
        
    if button_id == 'update-groups':  # If the triggering input is the "update-groups" button
        
        # If all values are None or empty, return None
        if all(value is None or value == '' for value in input_values):
            return no_update
        
        # Create a dictionary where keys are the 'index' of the inputs and values are their values
        grouped_values = {}
        for input_id, value in zip(input_ids, input_values):
            if value is not None and value != '':
                sample_name = input_id['index']
                grouped_values.setdefault(value, []).append(sample_name)  # Group the values based on the input values

        return grouped_values  # Return the dictionary of grouped values
    
    else:
        return no_update  # If another input triggered the callback, do nothing


# Sample group data order callback functions
@app.callback(
[
    Output('data-order-grid', 'columnDefs'),
    Output('data-order-grid', 'rowData'),
    Output('data-order-placeholder-message', 'style')
],
    Input('store-met-groups', 'data')
)
def generate_data_order_selection(met_groups):
    """
    Generate columns, row data, and control the visibility of a placeholder message in a data order grid.

    Parameters:
    met_groups (dict): Dictionary containing metabolite groups as keys and sample names as values.

    Returns:
    tuple: Contains column definitions, row data, and style for controlling the visibility of a placeholder message.
    """

    if met_groups is None or not met_groups:  # Check if the input data is empty or None
        # If there's no data, no updates are made to the grid columns and rows, and the placeholder message is made visible
        return no_update, no_update, {}

    else:
        # Filter out invalid groups (empty group names or sample lists)
        valid_groups = {group: samples for group, samples in met_groups.items() if group and samples}

        # Create column definitions for the dash_ag_grid
        columns = [
            {
                'headerName': group,  # Set the column header as the group name
                'field': group,  # Set the field name as the group name
                'enableRowGroup': True,  # Enable row grouping feature
                'flex': 1  # Set the column width to be flexible
            }
            for group in valid_groups.keys()]  # Iterate over each valid group

        # Create row data for the dash_ag_grid
        row_data = []
        max_samples = max(len(samples) for samples in valid_groups.values())  # Find the maximum sample count among groups
        for i in range(max_samples):  # Iterate based on the maximum sample count
            row = {}
            for group, samples in valid_groups.items():  # Iterate over each valid group and its samples
                row[group] = samples[i] if i < len(samples) else ""  # Populate rows with sample data or leave them empty
            row_data.append(row)  # Append each row to the row_data list

        # Hide the placeholder message by applying a CSS style when the grid is displayed
        return columns, row_data, {'display': 'none'}


@app.callback(
        Output('store-data-order', 'data'),
    [
        Input('update-data-order', 'n_clicks'), 
        Input('store-met-groups', 'data') 
    ],  
    [
        State('data-order-grid', 'columnState'),  
        State('data-order-grid', 'rowData')   
    ],  
    prevent_initial_update=True
)
def store_data_order_selection(n_clicks, met_groups, column_state, data):
    """
    Store and manage the order of data based on user interactions.

    Parameters:
    - n_clicks (int): Number of button clicks.
    - met_groups (dict): Dictionary containing metabolite groups.
    - column_state (list): A list containing the state of the grid columns.
    - data (list): A list containing the current data in the grid.

    Returns:
    dict: Updated order of the data, or no_update.
    """
    # Get context to identify which Input triggered the callback
    ctx = callback_context  
    
    # If no Input has triggered the callback, return None
    if not ctx.triggered:  
        return no_update
    else:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]  # Identify the ID of the triggered Input

    if trigger_id == 'store-met-groups' and met_groups is not None:  # If triggered by met_groups data update
        # Use the met_groups data directly
        return met_groups

    elif trigger_id == 'update-data-order' and data is not None and column_state is not None:  # If triggered by button click
        # Transform the grid data into a dictionary structure
        transformed_data = {}
        for row in data:  # Iterate over each row in the data
            for group, sample in row.items():  # Iterate over each cell in the row
                if sample:
                    transformed_data.setdefault(group, []).append(sample)  # Group samples by their columns/groups
        
        # Reorder the transformed data based on the order of columns in column_state
        ordered_column_ids = [col['colId'] for col in column_state]  # Get ordered list of column IDs
        reordered_data = {col_id: transformed_data[col_id] 
                          for col_id in ordered_column_ids if col_id in transformed_data}  # Reorder the data
        
        return reordered_data  # Return reordered data
    
    else:
        return no_update  # If conditions are not met, return no update


@app.callback(
[
    Output('p-value-data-order-metabolomics', 'children'),
    Output('p-value-data-order-isotopologue-distribution', 'children'),
    Output('metabolomics-pool-dynamic-checkbox-input', 'children'),
],
    Input('store-data-order', 'data')
)
def display_sample_group_order(stored_group_order):
    """
    Display sample groups in p-value settings modals and manage color inputs for each group.
    
    This function creates display elements showing the ordering of sample groups and color selection
    inputs based on the provided group ordering data. The group information is utilized in different
    parts of the application, specifically in p-value settings modals and for color customization in
    metabolomics pool data settings modal.
    
    Parameters:
    - stored_group_order (dict): A dictionary containing ordered groups of sample replicates.
    
    Returns:
    - tuple: Tuple containing HTML Divs with sample group order information and color selection inputs.
    """
    
    # Message to display when no group order information is available
    disclaimer_message = html.Div(
                            'Please group sample replicates to have data ordering enabled. Refer to "Group Sample Replicates for Data Analysis',
                            className='modal-placeholder-message')
    
    if stored_group_order is None:
        return disclaimer_message, disclaimer_message, disclaimer_message
    
    # Creating display elements to show the current order of groups
    header_row = dbc.Row(dbc.Col(html.Div('Current order of groups:')))
    sample_group_cols = [dbc.Col(html.Div(group, className='sample-group-dropdown-label')) for group in stored_group_order.keys()]
    sample_groups_row = dbc.Row(
                            sample_group_cols,
                            justify='center',
                            align='center'
                        )
    combined_div = html.Div([header_row, sample_groups_row])
    
    # Creating color selection inputs for each group in the metabolomics pool data
    color_input_cols = []
    for index, group in enumerate(stored_group_order.keys()):
        color_input = dbc.Input(
            id={'type': 'dynamic-metabolomics-group-color-input', 'index': group},
            type='color',
            value='#bdbdbd',  # Default color value
            style={'margin': '10px'}
        )
        group_col = dbc.Row([
            dbc.Col(
                html.Label(f'Color for {group}:', style={'margin': '10px'})
            ),
            dbc.Col(
                color_input
            )
        ])
        color_input_cols.append(group_col)
    
    color_selection_row = dbc.Row(color_input_cols)
    
    # Returning the created HTML elements to be displayed in the respective parts of the application
    return combined_div, combined_div, color_selection_row


@app.callback(
    Output('p-value-metabolomics-dropdown-container', 'children'),
[
    Input('add-pvalue-metabolomics-dropdown', 'n_clicks'),
    Input('clear-p-value-metabolomics', 'n_clicks')
],
[
    State('store-data-order', 'data'),
    State('p-value-metabolomics-dropdown-container', 'children')
]
)
def manage_pvalue_dropdown_metabolomics(add_clicks, clear_clicks, stored_group_order, children):
    """
    Manage the dynamic addition and clearing of dropdowns for p-value comparisons for metabolomics data
    in the p-value comparisons modal for bulk metabolomics.
    
    This function handles the addition of new dropdowns for selecting sample groups to compare 
    when the "add" button is clicked, and clears all dropdowns when the "clear" button is clicked.
    
    Parameters:
    - add_clicks (int): Number of times the add button has been clicked.
    - clear_clicks (int): Number of times the clear button has been clicked.
    - stored_group_order (dict): Stored ordered groups of sample replicates.
    - children (list): Existing children components within the dropdown container.
    
    Returns:
    - list: Updated children components within the dropdown container.
    """
    
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'clear-p-value-metabolomics' and clear_clicks:
        # If the clear button was clicked, remove all dropdowns
        return []

    elif button_id == 'add-pvalue-metabolomics-dropdown' and add_clicks:
        if stored_group_order is None:
            return no_update
        
        # Creating dropdown options from the stored group order data
        sample_groups_dropdown = [{'label': group, 'value': group} for group in stored_group_order.keys()] if stored_group_order else []
        
        # Adding a new dropdown row for each button click
        new_element_id = len(children)
        new_dropdown_row = html.Div([
            dbc.Row([
                dbc.Col(html.Div(html.Label(f'Comparison #{new_element_id + 1}:'), style={'textAlign': 'center'}), width=2),
                dbc.Col(html.Div(dcc.Dropdown(
                    id={
                        'type': 'dynamic-dropdown-p-value-metabolomics',
                        'index': new_element_id
                    },
                    options=sample_groups_dropdown,
                ), style={'padding': '5px', 'margin': '5px'})),
                dbc.Col(html.Div(html.Label('to'), style={'textAlign': 'center'}), width=1),
                dbc.Col(html.Div(dcc.Dropdown(
                    id={
                        'type': 'dynamic-dropdown2-p-value-metabolomics',
                        'index': new_element_id
                    },
                    options=sample_groups_dropdown,
                ), style={'padding': '5px', 'margin': '5px'})),
            ],
            justify='center',
            align='center'
            ),
        ])

        children.append(new_dropdown_row)
        return children

    return no_update


@app.callback(
    Output('store-p-value-metabolomics', 'data'),
    Input('update-p-value-metabolomics', 'n_clicks'),
[
    State({'type': 'dynamic-dropdown-p-value-metabolomics', 'index': ALL}, 'value'),
    State({'type': 'dynamic-dropdown2-p-value-metabolomics', 'index': ALL}, 'value'),
    State('numerical-p-value-checkbox', 'value'),
    State('store-data-order', 'data')
],
    prevent_initial_call=True
)
def store_p_value_metabolomics(n_clicks, dropdown_values, dropdown2_values, numerical_pvalue, stored_group_order):
    """
    Store the selected p-value comparisons and numerical p-value checkbox state for metabolomics data.
    
    This function gets the selected groups for p-value comparisons from the dropdowns,
    the checkbox state for numerical p-values, and stores them for later use in 
    add_p_value_annotations function. It ensures that no mirror combinations are stored, 
    and only unique combinations of groups are kept.
    
    Parameters:
    - n_clicks (int): Number of times the update button has been clicked.
    - dropdown_values (list): Selected values from the first group of dropdowns.
    - dropdown2_values (list): Selected values from the second group of dropdowns.
    - numerical_pvalue (int, 1 if checked and 0 if not): State of the numerical p-value checkbox.
    - stored_group_order (dict): Stored ordered groups of sample replicates.
    
    Returns:
    - dict: A dictionary containing the combinations of group indices for p-value comparisons and the numerical p-value checkbox state.
    """
    
    if n_clicks > 0 and stored_group_order:
        
        # Verify that no selected dropdown value is None
        if None in dropdown_values or None in dropdown2_values:
            return no_update
        
        group_order = list(stored_group_order.keys())
        
        # Extract and store unique combinations of selected groups for comparisons
        seen_combinations = set()
        combined_values = []
        for group1, group2 in zip(dropdown_values, dropdown2_values):
            # Sort indices to avoid duplicated mirror combinations
            combination = sorted([group_order.index(group1), group_order.index(group2)])
            combination_tuple = tuple(combination)
            
            if combination_tuple not in seen_combinations:
                seen_combinations.add(combination_tuple)
                combined_values.append(combination)
        
        # Check the state of the numerical p-value checkbox
        numerical_pvalue_bool = bool(numerical_pvalue)
        
        # Store and return the unique group combinations and checkbox state
        return {"combinations": combined_values, "numerical_bool": numerical_pvalue_bool}

    # If no update action is performed or no group order data is stored, return None
    else:
        return no_update


@app.callback(
    Output('p-value-isotopologue-distribution-dropdown-container', 'children'),
[
    Input('add-pvalue-isotopologue-distribution-dropdown', 'n_clicks'),
    Input('clear-p-value-isotopologue-distribution', 'n_clicks')
],
[
    State('store-data-order', 'data'),
    State('p-value-isotopologue-distribution-dropdown-container', 'children')
]
)
def manage_pvalue_dropdown_isotopologue_distribution(add_clicks, clear_clicks, stored_group_order, children):
    """
    Manage the dynamic addition and clearing of dropdowns for p-value comparisons for metabolomics data
    in the p-value comparisons modal for bulk metabolomics.
    
    This function handles the addition of new dropdowns for selecting sample groups to compare 
    when the "add" button is clicked, and clears all dropdowns when the "clear" button is clicked.
    
    Parameters:
    - add_clicks (int): Number of times the add button has been clicked.
    - clear_clicks (int): Number of times the clear button has been clicked.
    - stored_group_order (dict): Stored ordered groups of sample replicates.
    - children (list): Existing children components within the dropdown container.
    
    Returns:
    - list: Updated children components within the dropdown container.
    """
    
    ctx = callback_context
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'clear-p-value-isotopologue-distribution' and clear_clicks:
        # If the clear button was clicked, remove all dropdowns
        return []

    elif button_id == 'add-pvalue-isotopologue-distribution-dropdown' and add_clicks:
        if stored_group_order is None:
            return no_update
        
        # Creating dropdown options from the stored group order data
        sample_groups_dropdown = [{'label': group, 'value': group} for group in stored_group_order.keys()] if stored_group_order else []
        
        # Adding a new dropdown row for each button click
        new_element_id = len(children)
        new_dropdown_row = html.Div([
            dbc.Row([
                dbc.Col(html.Div(html.Label(f'Comparison #{new_element_id + 1}:'), style={'textAlign': 'center'}), width=2),
                dbc.Col(html.Div(dcc.Dropdown(
                    id={
                        'type': 'dynamic-dropdown-p-value-isotopologue-distribution',
                        'index': new_element_id
                    },
                    options=sample_groups_dropdown,
                ), style={'padding': '5px', 'margin': '5px'})),
                dbc.Col(html.Div(html.Label('to'), style={'textAlign': 'center'}), width=1),
                dbc.Col(html.Div(dcc.Dropdown(
                    id={
                        'type': 'dynamic-dropdown2-p-value-isotopologue-distribution',
                        'index': new_element_id
                    },
                    options=sample_groups_dropdown,
                ), style={'padding': '5px', 'margin': '5px'})),
            ],
            justify='center',
            align='center'
            ),
        ])

        children.append(new_dropdown_row)
        return children

    return no_update


@app.callback(
    Output('store-p-value-isotopologue-distribution', 'data'),
    Input('update-p-value-isotopologue-distribution', 'n_clicks'),
[
    State({'type': 'dynamic-dropdown-p-value-isotopologue-distribution', 'index': ALL}, 'value'),
    State({'type': 'dynamic-dropdown2-p-value-isotopologue-distribution', 'index': ALL}, 'value'),
    State('numerical-p-value-checkbox-isotopologue-distribution', 'value'),
    State('store-data-order', 'data')
],
    prevent_initial_call=True
)
def store_p_value_isotopologue_distribution(n_clicks, dropdown_values, dropdown2_values, numerical_pvalue, stored_group_order):
    """
    Store the selected p-value comparisons and numerical p-value checkbox state for metabolomics data.
    
    This function gets the selected groups for p-value comparisons from the dropdowns,
    the checkbox state for numerical p-values, and stores them for later use in 
    add_p_value_annotations function. It ensures that no mirror combinations are stored, 
    and only unique combinations of groups are kept.
    
    Parameters:
    - n_clicks (int): Number of times the update button has been clicked.
    - dropdown_values (list): Selected values from the first group of dropdowns.
    - dropdown2_values (list): Selected values from the second group of dropdowns.
    - numerical_pvalue (int, 1 if checked and 0 if not): State of the numerical p-value checkbox.
    - stored_group_order (dict): Stored ordered groups of sample replicates.
    
    Returns:
    - dict: A dictionary containing the combinations of group indices for p-value comparisons and the numerical p-value checkbox state.
    """
    
    if n_clicks > 0 and stored_group_order:
        
        # Verify that no selected dropdown value is None
        if None in dropdown_values or None in dropdown2_values:
            return no_update
        
        group_order = list(stored_group_order.keys())
        
        # Extract and store unique combinations of selected groups for comparisons
        seen_combinations = set()
        combined_values = []
        for group1, group2 in zip(dropdown_values, dropdown2_values):
            # Sort indices to avoid duplicated mirror combinations
            combination = sorted([group_order.index(group1), group_order.index(group2)])
            combination_tuple = tuple(combination)
            
            if combination_tuple not in seen_combinations:
                seen_combinations.add(combination_tuple)
                combined_values.append(combination)
        
        # Check the state of the numerical p-value checkbox
        numerical_pvalue_bool = bool(numerical_pvalue)
        
        # Store and return the unique group combinations and checkbox state
        return {"combinations": combined_values, "numerical_bool": numerical_pvalue_bool}

    # If no update action is performed or no group order data is stored, return None
    else:
        return no_update



@app.callback(
    Output('store-settings-metabolomics', 'data'),
[
    Input('update-settings-metabolomics', 'n_clicks'),
    Input('store-data-order', 'data')
],
[
    State('metabolomics-pool-height', 'value'),
    State('metabolomics-pool-width', 'value'),
    State('metabolomics-font-selector', 'value'),
    State('metabolomics-font-size', 'value'),
    State('metabolomics-pool-boxgap', 'value'),
    State('metabolomics-pool-boxwidth', 'value'),
    State('metabolomics-pool-datapoints-visible', 'value'),
    State('metabolomics-pool-datapoint-size', 'value'),
    State('metabolomics-pool-datapoint-color', 'value'),
    State('metabolomics-pool-same-color-for-groups', 'value'),
    State('metabolomics-pool-data-color', 'value'),
    State({'type': 'dynamic-metabolomics-group-color-input', 'index': ALL}, 'id'),
    State({'type': 'dynamic-metabolomics-group-color-input', 'index': ALL}, 'value')
]
)
def store_settings_metabolomics(n_clicks, 
                                stored_data_order, 
                                height, 
                                width, 
                                font_style, 
                                font_size, 
                                boxgap, 
                                boxwidth,
                                pool_datapoints_visible,
                                pool_datapoint_size,
                                pool_datapoint_color,
                                pool_group_same_color,
                                pool_group_color,
                                pool_color_group_names,
                                pool_color_values):
    
    if stored_data_order is not None and (n_clicks is None or n_clicks == 0):
        # Store the initial settings
        initial_settings = {
            'height': height,
            'width': width,
            'font_selector': font_style if font_style else 'Arial',
            'font_size': font_size,
            'boxgap': boxgap,
            'boxwidth': boxwidth,
            'pool_datapoints_visible': True if pool_datapoints_visible == [1] else False,
            'pool_datapoint_size': pool_datapoint_size,
            'pool_datapoint_color': pool_datapoint_color,
            'pool_group_same_color': True if pool_group_same_color == [1] else False,
            'pool_group_color': pool_group_color,
            'pool_ind_group_colors': None,
            
        }
        
        return initial_settings
        
    elif n_clicks > 0:  # Update button has been clicked
        
        # Generate a dictionary of individualy selected colors
        pool_ind_group_colors = {id['index']: color for id, color in zip(pool_color_group_names, pool_color_values)}
        
        # Update the settings with the current values
        new_settings = {
            'height': height,
            'width': width,
            'font_selector': font_style,
            'font_size': font_size,
            'boxgap': boxgap,
            'boxwidth': boxwidth,
            'pool_datapoints_visible': True if pool_datapoints_visible == [1] else False,
            'pool_datapoint_size': pool_datapoint_size,
            'pool_datapoint_color': pool_datapoint_color,
            'pool_group_same_color': True if pool_group_same_color == [1] else False,
            'pool_group_color': pool_group_color,
            'pool_ind_group_colors': pool_ind_group_colors
        }
        
        return new_settings
        
    # If no conditions are met, don’t update the stored data (return None or the current data)
    return no_update


@app.callback(
    Output('store-volcano-settings', 'data'),
[
    Input('update-settings-volcano', 'n_clicks'),
    Input('store-data-order', 'data')
],
[
    State('volcano-plot-height', 'value'),
    State('volcano-plot-width', 'value'),
    State('volcano-plot-font-selector', 'value'),
    State('volcano-plot-font-size', 'value'),
    State('volcano-plot-datapoint-size', 'value'),
    State('volcano-plot-datapoint-color', 'value'),
    State('volcano-plot-fc-cutoff-visible', 'value'),
    State('volcano-plot-fc-value-input', 'value'),
    State('volcano-plot-pvalue-cutoff-visible', 'value'),
    State('volcano-plot-pvalue-cutoff-text-visible', 'value'),
    State('volcano-plot-color-inc-1', 'value'),
    State('volcano-plot-color-inc-2', 'value'),
    State('volcano-plot-color-inc-3', 'value'),
    State('volcano-plot-color-dec-1', 'value'),
    State('volcano-plot-color-dec-2', 'value'),
    State('volcano-plot-color-dec-3', 'value')
]
)
def store_mettings_volcano(n_clicks,
                           store_data_order,
                           height, 
                           width, 
                           font_selector, 
                           font_size,
                           datapoint_size, 
                           datapoint_color, 
                           fc_visible, 
                           fc_value,
                           p_value_visible,
                           p_value_text_visible,
                           color_inc_1,
                           color_inc_2,
                           color_inc_3,
                           color_dec_1,
                           color_dec_2,
                           color_dec_3):
    
    # If store-data-order is updated, store the current state values (used as placeholders)
    if store_data_order is not None:
        initial_settings = {
            'height': height,
            'width': width,
            'font_selector': font_selector,
            'font_size': font_size,
            'datapoint_size': datapoint_size,
            'datapoint_color': datapoint_color,
            'fc_visible': True if fc_visible == [1] else False,
            'fc_value': fc_value,
            'p_value_visible': True if p_value_visible == [1] else False,
            'p_value_text_visible': True if p_value_text_visible == [1] else False,
            'color_inc_1': color_inc_1,
            'color_inc_2': color_inc_2,
            'color_inc_3': color_inc_3,
            'color_dec_1': color_dec_1,
            'color_dec_2': color_dec_2,
            'color_dec_3': color_dec_3,

        }
        
        return initial_settings
    
    # If the update button has been clicked, store the current settings
    elif n_clicks > 0:
        new_settings = {
            'height': height,
            'width': width,
            'font_selector': font_selector,
            'font_size': font_size,
            'datapoint_size': datapoint_size,
            'datapoint_color': datapoint_color,
            'fc_visible': True if fc_visible == [1] else False,
            'fc_value': fc_value,
            'p_value_visible': True if p_value_visible == [1] else False,
            'p_value_text_visible': True if p_value_text_visible == [1] else False,
            'color_inc_1': color_inc_1,
            'color_inc_2': color_inc_2,
            'color_inc_3': color_inc_3,
            'color_dec_1': color_dec_1,
            'color_dec_2': color_dec_2,
            'color_dec_3': color_dec_3,

        }
        
        return new_settings
    
    # If no conditions are met, don’t update the stored settings (return None or current data)
    return no_update


@app.callback(
    Output('store-bulk-heatmap-settings', 'data'),
[
    Input('update-settings-bulk-heatmap', 'n_clicks'),
    Input('store-data-order', 'data')
],
[
    State('bulk-heatmap-height-modifier', 'value'),
    State('bulk-heatmap-width-modifier', 'value'),
    State('bulk-heatmap-font-selector', 'value'),
    State('bulk-heatmap-font-size', 'value'),
    State('bulk-heatmap-dec-val-color', 'value'),
    State('bulk-heatmap-unch-val-color', 'value'),
    State('bulk-heatmap-inc-val-color', 'value'),
    State('bulk-pool-heatmap-sig-dots-present', 'value'),
    State('bulk-pool-heatmap-first-gap-present', 'value'),
    State('bulk-pool-heatmap-group-gaps-present', 'value')
]
)
def store_settings_bulk_heatmap(n_clicks,
                                store_data_order,
                                height_modifier, 
                                width_modifier, 
                                font_selector, 
                                font_size,
                                decreased_color,
                                unchanged_color,
                                increased_color,
                                sig_dots_present,
                                first_gap_present,
                                group_gaps_present):

    # If store-data-order is updated, store the current state values (used as placeholders)
    if store_data_order is not None:
        initial_settings = {
            'height_modifier': height_modifier,
            'width_modifier': width_modifier,
            'font_selector': font_selector,
            'font_size': font_size,
            'decreased_color': decreased_color,
            'unchanged_color': unchanged_color,
            'increased_color': increased_color,
            'sig_dots_present': True if sig_dots_present == [1] else False,
            'first_gap_present': True if first_gap_present == [1] else False,
            'group_gaps_present': True if group_gaps_present == [1] else False
        }
        
        return initial_settings

    # If the update button has been clicked, store the current settings
    elif n_clicks > 0:
        new_settings = {
            'height_modifier': height_modifier,
            'width_modifier': width_modifier,
            'font_selector': font_selector,
            'font_size': font_size,
            'decreased_color': decreased_color,
            'unchanged_color': unchanged_color,
            'increased_color': increased_color,
            'sig_dots_present': True if sig_dots_present == [1] else False,
            'first_gap_present': True if first_gap_present == [1] else False,
            'group_gaps_present': True if group_gaps_present == [1] else False
        }
        
        return new_settings
    
    # If no conditions are met, don’t update the stored settings (return None or current data)
    return no_update


@app.callback(
    Output('store-bulk-isotopologue-heatmap-settings', 'data'),
[
    Input('update-settings-bulk-isotopologue-heatmap', 'n_clicks'),
    Input('store-data-order', 'data')
],
[
    State('bulk-isotopologue-heatmap-height-modifier', 'value'),
    State('bulk-isotopologue-heatmap-width-modifier', 'value'),
    State('bulk-isotopologue-heatmap-font-selector', 'value'),
    State('bulk-isotopologue-heatmap-font-size', 'value'),
    State('bulk-isotopologue-heatmap-unch-val-color', 'value'),
    State('bulk-isotopologue-heatmap-inc-val-color', 'value'),
    State('bulk-isotopologue-heatmap-sig-dots-present', 'value'),
    State('bulk-isotopologue-heatmap-first-gap-present', 'value'),
    State('bulk-isotopologue-heatmap-group-gaps-present', 'value')
]
)
def store_settings_bulk_isotopologue_heatmap(n_clicks,
                                store_data_order,
                                height_modifier, 
                                width_modifier, 
                                font_selector, 
                                font_size,
                                unchanged_color,
                                increased_color,
                                sig_dots_present,
                                first_gap_present,
                                group_gaps_present):

    # If store-data-order is updated, store the current state values (used as placeholders)
    if store_data_order is not None:
        initial_settings = {
            'height_modifier': height_modifier,
            'width_modifier': width_modifier,
            'font_selector': font_selector,
            'font_size': font_size,
            'unchanged_color': unchanged_color,
            'increased_color': increased_color,
            'sig_dots_present': True if sig_dots_present == [1] else False,
            'first_gap_present': True if first_gap_present == [1] else False,
            'group_gaps_present': True if group_gaps_present == [1] else False
        }
        
        return initial_settings

    # If the update button has been clicked, store the current settings
    elif n_clicks > 0:
        new_settings = {
            'height_modifier': height_modifier,
            'width_modifier': width_modifier,
            'font_selector': font_selector,
            'font_size': font_size,
            'unchanged_color': unchanged_color,
            'increased_color': increased_color,
            'sig_dots_present': True if sig_dots_present == [1] else False,
            'first_gap_present': True if first_gap_present == [1] else False,
            'group_gaps_present': True if group_gaps_present == [1] else False
        }
        
        return new_settings
    
    # If no conditions are met, don’t update the stored settings (return None or current data)
    return no_update


@app.callback(
    Output('store-custom-heatmap-settings', 'data'),
[
    Input('update-settings-custom-heatmap', 'n_clicks'),
    Input('store-data-order', 'data')
],
[
    State('custom-heatmap-height-modifier', 'value'),
    State('custom-heatmap-width-modifier', 'value'),
    State('custom-heatmap-font-selector', 'value'),
    State('custom-heatmap-font-size', 'value'),
    State('custom-heatmap-dec-val-color', 'value'),
    State('custom-heatmap-unch-val-color', 'value'),
    State('custom-heatmap-inc-val-color', 'value'),
    State('custom-heatmap-sig-dots-present', 'value'),
    State('custom-heatmap-first-gap-present', 'value'),
    State('custom-heatmap-group-gaps-present', 'value')
]
)
def store_settings_custom_heatmap(n_clicks,
                                store_data_order,
                                height_modifier, 
                                width_modifier, 
                                font_selector, 
                                font_size,
                                decreased_color,
                                unchanged_color,
                                increased_color,
                                sig_dots_present,
                                first_gap_present,
                                group_gaps_present):

    # If store-data-order is updated, store the current state values (used as placeholders)
    if store_data_order is not None:
        initial_settings = {
            'height_modifier': height_modifier,
            'width_modifier': width_modifier,
            'font_selector': font_selector,
            'font_size': font_size,
            'decreased_color': decreased_color,
            'unchanged_color': unchanged_color,
            'increased_color': increased_color,
            'sig_dots_present': True if sig_dots_present == [1] else False,
            'first_gap_present': True if first_gap_present == [1] else False,
            'group_gaps_present': True if group_gaps_present == [1] else False
        }
        
        
        
        return initial_settings

    # If the update button has been clicked, store the current settings
    elif n_clicks > 0:
        new_settings = {
            'height_modifier': height_modifier,
            'width_modifier': width_modifier,
            'font_selector': font_selector,
            'font_size': font_size,
            'decreased_color': decreased_color,
            'unchanged_color': unchanged_color,
            'increased_color': increased_color,
            'sig_dots_present': True if sig_dots_present == [1] else False,
            'first_gap_present': True if first_gap_present == [1] else False,
            'group_gaps_present': True if group_gaps_present == [1] else False
        }
                
        return new_settings
    
    # If no conditions are met, don’t update the stored settings (return None or current data)
    return no_update


@app.callback(
    Output('store-settings-isotopologue-distribution', 'data'),
[
    Input('update-settings-isotopologue-distribution', 'n_clicks'),
    Input('store-data-order', 'data')
],
[
    State('isotopologue-distribution-height', 'value'),
    State('isotopologue-distribution-width', 'value'),
    State('isotopologue-distribution-font-selector', 'value'),
    State('isotopologue-distribution-font-size', 'value'),
    State('isotopologue-distribution-bargap', 'value'),
    State('isotopologue-distribution-barwidth', 'value'),
]
)
def store_settings_isotopologue_distribution(n_clicks, 
                                stored_data_order,
                                height, 
                                width, 
                                font_style, 
                                font_size, 
                                bargap, 
                                barwidth):
    
    if stored_data_order is not None and (n_clicks is None or n_clicks == 0):
        # Store the initial settings
        initial_settings = {
            'height': height,
            'width': width,
            'font_selector': font_style if font_style else 'Arial',
            'font_size': font_size,
            'bargap': bargap,
            'barwidth': barwidth
        }
        
        return initial_settings
        
    elif n_clicks > 0:  # Update button has been clicked
        
        # Update the settings with the current values
        new_settings = {
            'height': height,
            'width': width,
            'font_selector': font_style,
            'font_size': font_size,
            'bargap': bargap,
            'barwidth': barwidth
        }

        return new_settings
        
    # If no conditions are met, don’t update the stored data (return None or the current data)
    return no_update


@app.callback(
[
    Output('normalization-display-container-bulk-heatmap', 'children'),
    Output('normalization-display-container-custom-heatmap', 'children'),
    Output('normalization-display-container-bulk-metabolomics', 'children'),
    Output('normalization-display-container-volcano', 'children')
],
[
    Input('generate-bulk-heatmap-plot', 'n_clicks'),
    Input('generate-custom-heatmap-plot', 'n_clicks'),
    Input('generate-metabolomics', 'n_clicks'),
    Input('generate-volcano-plot', 'n_clicks')
],
    State('store-data-normalization', 'data'),
    prevent_initial_call = True
)
def display_selected_normalization(bulk_heatmap, custom_heatmap, bulk_metabolomics, volcano, met_normalization):
    
    
    ctx = callback_context
    
    if not ctx.triggered:
        raise PreventUpdate
    
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if met_normalization is None:
            raise PreventUpdate
        
        normalization_list = met_normalization['selected_values']
        
        if normalization_list == []:
            normalization_display = "No selected normalization variables!"
            
        else:
            normalization_display = "Data normalized by: " + ', '.join(normalization_list)
        
        # Define an empty default display for all outputs
        default_display = html.Div()
        # Create a display message wrapped in a Div
        display_message = html.Div(normalization_display)

        # Based on which button was clicked, return the message for the corresponding Div
        if button_id == 'generate-bulk-heatmap-plot':
            return display_message, default_display, default_display, default_display
        elif button_id == 'generate-custom-heatmap-plot':
            return default_display, display_message, default_display, default_display
        elif button_id == 'generate-metabolomics':
            return default_display, default_display, display_message, default_display
        elif button_id == 'generate-volcano-plot':
            return default_display, default_display, default_display, display_message
        else:
            # If for some reason, the button_id doesn't match, raise PreventUpdate to avoid updating
            raise PreventUpdate