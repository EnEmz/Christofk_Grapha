import pandas as pd
import io
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from dash import html, dcc, no_update, callback_context
import base64

from app import app
from layout.config import normalization_preselected, df_met_group_list
from layout.toast import generate_toast
from layout.utilities_download import get_download_df_normalized_pool, get_download_df_iso, get_download_df_lingress
from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, compile_met_pool_ratio_data

# Generate checkboxes for pool, normalization and lingress data
@app.callback(
    Output('download-container-data-type', 'children'),
    Input('open-download-data', 'n_clicks'),
[
    State('store-data-pool', 'data'),
    State('store-data-iso', 'data'),
    State('store-data-lingress', 'data')
]
)
def generate_download_container_data_type(n_clicks, pool_data, iso_data, lin_data):
    """
    Generates checkboxes for selecting data types for download in the modal.

    Parameters:
    ----------
    n_clicks : int
        Number of times the modal open button has been clicked.
    pool_data : json
        JSON-formatted string containing the pool data DataFrame.
    iso_data : json
        JSON-formatted string containing the isotopologue data DataFrame.
    lin_data : json
        JSON-formatted string containing the lingress data DataFrame.

    Returns:
    -------
    dbc.Row
        A Row component containing checkboxes for each data type.
    """
    
    if n_clicks == 0:
        # If the button has not been clicked yet, do not generate the checkboxes
        raise PreventUpdate

    checkboxes = []

    pool_checkbox_value = pool_data is not None
    iso_checkbox_value = iso_data is not None
    lingress_checkbox_value = lin_data is not None

    checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-pool'}, label='Pool Data', value=False, disabled=not pool_checkbox_value)))
    
    checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-iso'}, label='Isotopologue Data', value=False, disabled=not iso_checkbox_value)))

    checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-lingress'}, label='Lingress Data (Only with Pool Data)', value=False, disabled=True)))

    return dbc.Row(checkboxes, justify='center')


@app.callback(
    Output({'type': 'download-type-checkbox', 'index': 'download-lingress'}, 'disabled'),
    Input({'type': 'download-type-checkbox', 'index': 'download-pool'}, 'value'),
    State('store-data-lingress', 'data')
)
def toggle_lingress_checkbox(pool_checked, lin_data):
    """
    Toggles the enabled state of the Lingress Data checkbox based on the Pool Data checkbox.

    Parameters:
    ----------
    pool_checked : bool
        Indicates if the Pool Data checkbox is checked.
    lin_data : json
        JSON-formatted string containing the lingress data DataFrame.

    Returns:
    -------
    bool
        The disabled state of the Lingress Data checkbox.
    """
    
    if lin_data is None:
        return True  # Lingress checkbox remains disabled if no data
    return not pool_checked  # Enable Lingress checkbox only if Pool checkbox is checked


@app.callback(
    Output({'type': 'download-type-checkbox', 'index': 'download-lingress'}, 'value'),
    Input({'type': 'download-type-checkbox', 'index': 'download-pool'}, 'value'),
    State({'type': 'download-type-checkbox', 'index': 'download-lingress'}, 'value')
)
def uncheck_lingress_if_pool_unchecked(pool_checked, lingress_checked):
    """
    Unchecks the Lingress Data checkbox if the Pool Data checkbox is unchecked.

    Parameters:
    ----------
    pool_checked : bool
        Indicates if the Pool Data checkbox is checked.
    lingress_checked : bool
        Indicates if the Lingress Data checkbox is checked.

    Returns:
    -------
    bool
        The checked state of the Lingress Data checkbox.
    """
    
    if not pool_checked and lingress_checked:
        return False  # Uncheck Lingress checkbox if Pool checkbox is unchecked
    return lingress_checked  # Maintain the current value if Pool checkbox is checked


# Callback for generating normalization dropdown in download modal
@app.callback(
    Output('download-container-normalization', 'children'),
    Input('open-download-data', 'n_clicks'),
    State('store-data-pool', 'data')
)
def generate_download_container_normalization(n_clicks, pool_data):
    """
    Generates the normalization options dropdown for the download modal.

    Parameters:
    ----------
    n_clicks : int
        Number of times the modal open button has been clicked.
    pool_data : json
        JSON-formatted string containing the pool data DataFrame.

    Returns:
    -------
    list
        A list containing the placeholder message and dropdown component for normalization options.
    """
    
    if n_clicks == 0:
        # If the button has not been clicked yet, do not generate the normalization dropdown
        raise PreventUpdate

    disabled = not pool_data

    placeholder_message = html.Div(
        'Please upload a metabolomics data file to populate the normalization options.',
        className='modal-placeholder-message'
    ) if disabled else None

    options = []
    preselected_options = []

    if pool_data:
        strings_to_check = normalization_preselected

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

    dropdown = dcc.Dropdown(
        id='normalization-dropdown-selector-download',
        options=options,
        value=preselected_options,
        multi=True,
        disabled=disabled
    )

    return [html.Div([placeholder_message, dropdown])]


@app.callback(
    Output('download-container-classes', 'children'),
    Input('open-download-data', 'n_clicks')
)
def generate_download_container_classes(n_clicks):
    """
    Generates the dropdown for selecting metabolite classes in the download modal.

    Parameters:
    ----------
    n_clicks : int
        Number of times the modal open button has been clicked.

    Returns:
    -------
    list
        A list containing the dropdown component for selecting metabolite classes.
    """

    if n_clicks == 0:
        raise PreventUpdate

    dropdown = dcc.Dropdown(
        id='metabolite-class-dropdown',
        options=[
            {'label': 'All metabolite classes', 'value': 'all'},
            {'label': 'Already selected metabolite classes', 'value': 'selected'}
        ],
        value='all',
        multi=False,
        style={'width': '600px', 'margin': '0 auto'}  # Set the desired width and center alignment
    )

    return [html.Div([dropdown], style={'width': '100%', 'text-align': 'center'})]


@app.callback(
    Output('download-container-groups', 'children'),
    Input('open-download-data', 'n_clicks')
)
def generate_download_container_groups(n_clicks):
    """
    Generates the dropdown for selecting sample replicate groups in the download modal.

    Parameters:
    ----------
    n_clicks : int
        Number of times the modal open button has been clicked.

    Returns:
    -------
    list
        A list containing the dropdown component for selecting sample replicate groups.
    """
    
    if n_clicks == 0:
        raise PreventUpdate

    dropdown = dcc.Dropdown(
        id='metabolite-groups-dropdown',
        options=[
            {'label': 'All sample replicates', 'value': 'all'},
            {'label': 'Already stored sample replicate selection', 'value': 'selected'}
        ],
        value='all',
        multi=False,
        style={'width': '600px', 'margin': '0 auto'}  # Set the desired width and center alignment
    )

    return [html.Div([dropdown], style={'width': '100%', 'text-align': 'center'})]


@app.callback(
    Output('download-p-value-container', 'children'),
    Input('open-download-data', 'n_clicks'),
    Input('generate-download-p-value-comparison-button', 'n_clicks'),
    Input('clear-download-p-value-comparisons-button', 'n_clicks'),
    Input({'type': 'delete-download-p-value-comparison', 'index': ALL}, 'n_clicks'),
    State('store-data-order', 'data'),
    State('download-p-value-container', 'children')
)
def manage_download_p_value_comparisons(n_clicks_open, n_clicks_generate, n_clicks_clear, n_clicks_delete, stored_group_order, current_comparisons):
    '''
    Manage the generation, clearing, and deletion of p-value comparisons when downloading the data.

    Parameters:
    ----------
    n_clicks_open : int
        Number of times the modal open button has been clicked.
    n_clicks_generate : int
        Number of times the generate button has been clicked.
    n_clicks_clear : int
        Number of times the clear button has been clicked.
    n_clicks_delete : list of int
        List of the number of times delete buttons have been clicked.
    stored_group_order : dict
        Stored dictionary containing the ordered groups of sample replicates.
    current_comparisons : list of dict
        List of current comparison components in the container.

    Returns:
    -------
    list of dict
        Updated list of components in the comparison container.
    '''

    ctx = callback_context
    if not ctx.triggered:
        raise PreventUpdate
    
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if button_id == 'open-download-data':
        if stored_group_order is None:
            placeholder_message = html.Div("Please group sample replicates to make p-value comparisons available at 'Group Sample Replicates for Data Analysis'.",
                                           className='modal-placeholder-message')
            return [placeholder_message]
        else:
            return []

    if button_id == 'clear-download-p-value-comparisons-button' and n_clicks_clear:
        if stored_group_order is None:
            placeholder_message = html.Div("Please group sample replicates to make p-value comparisons available at 'Group Sample Replicates for Data Analysis'.",
                                           className='modal-placeholder-message')
            return [placeholder_message]
        else:
            # If the clear button was clicked, remove all dropdowns
            return []

    elif button_id == 'generate-download-p-value-comparison-button' and n_clicks_generate:
        if stored_group_order is None:
            raise PreventUpdate
        else:
            # Creating dropdown options from the stored group order data
            sample_groups_dropdown = [{'label': group, 'value': group} for group in stored_group_order.keys()] if stored_group_order else []
            
            # Adding a new dropdown row for each button click
            new_element_id = len(current_comparisons)
            new_dropdown_row = html.Div([
                dbc.Row([
                    dbc.Col(html.Div(html.Label(f'Comparison #{new_element_id + 1}:'), style={'textAlign': 'center'}), width=2),
                    dbc.Col(html.Div(dcc.Dropdown(
                        id={
                            'type': 'dynamic-dropdown-p-value-download',
                            'index': new_element_id
                        },
                        options=sample_groups_dropdown,
                    ), style={'padding': '5px', 'margin': '5px'})),
                    dbc.Col(html.Div(html.Label('to'), style={'textAlign': 'center'}), width=1),
                    dbc.Col(html.Div(dcc.Dropdown(
                        id={
                            'type': 'dynamic-dropdown2-p-value-download',
                            'index': new_element_id
                        },
                        options=sample_groups_dropdown,
                    ), style={'padding': '5px', 'margin': '5px'})),
                    dbc.Col(dbc.Button("Delete", id={'type': 'delete-download-p-value-comparison', 'index': new_element_id}, color='danger', className='mr-1'))
                ],
                justify='center',
                align='center'
                ),
            ], style={'margin-bottom': '10px'}, id={'type': 'comparison-row', 'index': new_element_id})

            current_comparisons.append(new_dropdown_row)
            return current_comparisons

    elif 'delete-download-p-value-comparison' in button_id:
        # Correctly extract the index of the delete button that was clicked
        delete_indices = [i for i, n_clicks in enumerate(n_clicks_delete) if n_clicks is not None]
        if not delete_indices:
            raise PreventUpdate
        # Assuming only one button can be clicked at a time, take the first index
        index_to_delete = delete_indices[0]
        # Remove the corresponding child
        current_comparisons = [child for i, child in enumerate(current_comparisons) if i != index_to_delete]
        return current_comparisons

    return no_update


@app.callback(
    Output('store-download-config', 'data'),
    Input('download-data-button', 'n_clicks'),
    State({'type': 'download-type-checkbox', 'index': ALL}, 'value'),
    State({'type': 'download-type-checkbox', 'index': ALL}, 'id'),
    State('normalization-dropdown-selector-download', 'value'),
    State('metabolite-class-dropdown', 'value'),
    State('metabolite-groups-dropdown', 'value'),
    State({'type': 'dynamic-dropdown-p-value-download', 'index': ALL}, 'value'),
    State({'type': 'dynamic-dropdown2-p-value-download', 'index': ALL}, 'value'),
    State('download-pvalue-correction-selection', 'value'),
    State('store-data-order', 'data'),
    prevent_initial_call=True
)
def collect_download_options(n_clicks, checkbox_values, checkbox_ids, normalization_values, met_class_user, met_groups_user, p_value_comp_1, p_value_comp_2, pvalue_correction, stored_group_order):
    """
    Collects and stores the user-selected options for data download.

    Parameters:
    ----------
    n_clicks : int
        Number of times the download button has been clicked.
    checkbox_values : list
        List of boolean values indicating the checked state of each checkbox.
    checkbox_ids : list
        List of ids for each checkbox.
    normalization_values : list
        List of selected normalization variables.
    met_class_user : str
        User-selected metabolite class option.
    met_groups_user : str
        User-selected metabolite groups option.
    p_value_comp_1 : list
        List of selected values for the first dropdown in p-value comparisons.
    p_value_comp_2 : list
        List of selected values for the second dropdown in p-value comparisons.
    pvalue_correction : str
        User-selected p-value correction method.
    stored_group_order : dict
        Stored dictionary containing the ordered groups of sample replicates.

    Returns:
    -------
    dict
        A dictionary containing all user-selected options for data download.
    """

    if n_clicks is None:
        raise PreventUpdate

    # Collecting the data types selected
    selected_data_types = {
        checkbox_id['index']: value 
        for checkbox_id, value in zip(checkbox_ids, checkbox_values)
    }

    # Collecting normalization values
    normalization_selected = normalization_values if normalization_values else []

    # Collecting p-value comparisons
    if stored_group_order:
        group_order = list(stored_group_order.keys())
        
        # Extract and store unique combinations of selected groups for comparisons
        seen_combinations = set()
        combined_values = []
        for group1, group2 in zip(p_value_comp_1, p_value_comp_2):
            if group1 is None or group2 is None:
                continue
            # Sort indices to avoid duplicated mirror combinations
            combination = sorted([group_order.index(group1), group_order.index(group2)])
            combination_tuple = tuple(combination)
            
            if combination_tuple not in seen_combinations:
                seen_combinations.add(combination_tuple)
                combined_values.append(combination)
        
        p_value_comparisons = {
            "combinations": combined_values,
            "pvalue_correction": pvalue_correction
        }
    else:
        p_value_comparisons = {
            "combinations": [],
            "pvalue_correction": None
        }

    print(f"P-value comparisons: {p_value_comparisons}")

    download_config = {
        'data_types': selected_data_types,
        'normalization': normalization_selected,
        'metabolite_class': met_class_user,
        'metabolite_groups': met_groups_user,
        'p_value_comparisons': p_value_comparisons
    }

    return download_config


@app.callback(
    [Output('toast-container', 'children', allow_duplicate=True),
     Output('download-link', 'data')],
    Input('store-download-config', 'data'),
    State('download-data-input', 'value'),
    State('store-data-pool', 'data'),
    State('store-data-iso', 'data'),
    State('store-data-lingress', 'data'),
    State('store-metabolite-ratios', 'data'),
    State('store-met-classes', 'data'),
    State('store-data-order', 'data'),
    prevent_initial_call=True
)
def download_sheet_w_options(download_config, filename, pool_data, iso_data, lingress_data, met_ratios, met_classes_selected, met_groups_selected):
    if download_config is None:
        raise PreventUpdate

    # Set default filename if not provided
    if not filename:
        filename = "default_filename"

    # Read user selected config for download from stored values into variables
    selected_data_types = download_config.get('data_types', {})
    normalization_list = download_config.get('normalization', {})

    # Create a list of metabolite classes based on user selection
    class_user_selection = download_config.get('metabolite_class', {})
    if class_user_selection == 'selected':
        if met_classes_selected is None:
            return generate_toast("error", "Error", "No selected classes detected."), no_update
        else:
            met_classes = met_classes_selected['selected_values']
    else:
        met_classes = df_met_group_list['pathway_class'].drop_duplicates().tolist()

    # Create a dict of sample replicate groups based on user selection
    groups_user_selection = download_config.get('metabolite_groups', {})
    if groups_user_selection == 'selected':
        if met_groups_selected is None:
            return generate_toast("error", "Error", "No selected sample replicate groups detected."), no_update
        else:
            grouped_samples = {group: samples for group, samples in met_groups_selected.items() if group and samples}
    else:
        grouped_samples = 'all'

    # Initialize an Excel writer
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Check if pool data is selected and available
        if 'download-pool' in selected_data_types and selected_data_types['download-pool']:
            if pool_data is None:
                return generate_toast("error", "Error", "No uploaded pool data."), no_update

            pool_json_file = io.StringIO(pool_data)
            df_download_pool = pd.read_json(pool_json_file, orient='split')
            # Proceed with generating the pool data dataframe
            df_download_normalized_pool = get_download_df_normalized_pool(df_download_pool, met_classes, normalization_list, grouped_samples, met_ratios)

            df_download_pool.to_excel(writer, sheet_name='PoolAfterDF', index=False)
            df_download_normalized_pool.to_excel(writer, sheet_name='Normalized Pool', index=False)

        # Check if iso data is selected and available
        if 'download-iso' in selected_data_types and selected_data_types['download-iso']:
            if iso_data is None:
                return generate_toast("error", "Error", "No uploaded iso data."), no_update

            iso_json_file = io.StringIO(iso_data)
            df_iso = pd.read_json(iso_json_file, orient='split')
            # Proceed with generating the iso data dataframe
            df_download_iso = get_download_df_iso(df_iso, met_classes)
            df_download_iso.to_excel(writer, sheet_name='Normalized', index=False)

        # Check if lingress data is selected and available
        if 'download-lingress' in selected_data_types and selected_data_types['download-lingress']:
            if lingress_data is None:
                return generate_toast("error", "Error", "No uploaded lingress data."), no_update

            lingress_json_file = io.StringIO(lingress_data)

            pool_json_file = io.StringIO(pool_data)
            df_download_pool = pd.read_json(pool_json_file, orient='split')
            
            df_download_lingress = pd.read_json(lingress_json_file, orient='split')
            # Get each possible variable for the lingress (can do more than one)
            for _, row in df_download_lingress.iterrows():
                df_var_data = pd.DataFrame(row).T
                # Proceed with generating the lingress data dataframe
                df_download_lingress_stats = get_download_df_lingress(df_var_data, df_download_pool, met_classes, normalization_list, grouped_samples, met_ratios)
                df_download_lingress_stats.to_excel(writer, sheet_name=f'Lingress Data {row["Variable"]}', index=False)

    # Save the Excel file to BytesIO buffer
    output.seek(0)
    excel_data = output.getvalue()

    return generate_toast("success", "Success", f"File {filename}.xlsx downloaded."), dcc.send_bytes(excel_data, f"{filename}.xlsx")
