import pandas as pd
import io
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from dash import html, dcc, no_update, callback_context

from app import app
from layout.config import normalization_preselected, df_met_group_list
from layout.toast import generate_toast
from layout.utilities_download import get_download_df_pool, get_download_df_iso, get_download_df_lingress, get_download_df_pool_pvalues, get_download_df_iso_pvalues
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
    if n_clicks == 0:
        # If the button has not been clicked yet, do not generate the checkboxes
        raise PreventUpdate

    checkboxes = []

    if pool_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-pool'}, label='Pool Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-pool'}, label='Pool Data', value=False, disabled=True)))

    if iso_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-iso'}, label='Isotopologue Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-iso'}, label='Isotopologue Data', value=False, disabled=True)))

    if lin_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-lingress'}, label='Lingress Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'download-type-checkbox', 'index': 'download-lingress'}, label='Lingress Data', value=False, disabled=True)))

    return dbc.Row(checkboxes, justify='center')


# Callback for generating normalization dropdown in download modal
@app.callback(
    Output('download-container-normalization', 'children'),
    Input('open-download-data', 'n_clicks'),
    State('store-data-pool', 'data')
)
def generate_download_container_normalization(n_clicks, pool_data):
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
            placeholder_message = html.Div("Please group sample replicates to make p-value comparisons available.",
                                           className='modal-placeholder-message')
            return [placeholder_message]
        else:
            return []

    if button_id == 'clear-download-p-value-comparisons-button' and n_clicks_clear:
        # If the clear button was clicked, remove all dropdowns
        return []

    elif button_id == 'generate-download-p-value-comparison-button' and n_clicks_generate:
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
    State({'type': 'dynamic-dropdown-p-value-download', 'index': ALL}, 'value'),
    State({'type': 'dynamic-dropdown2-p-value-download', 'index': ALL}, 'value'),
    State('download-pvalue-correction-selection', 'value'),
    State('store-data-order', 'data'),
    prevent_initial_call=True
)
def collect_download_options(n_clicks, checkbox_values, checkbox_ids, normalization_values, metabolite_class, p_value_comp_1, p_value_comp_2, pvalue_correction, stored_group_order):
    if n_clicks is None:
        raise PreventUpdate

    # Collecting the data types selected
    selected_data_types = {
        checkbox_id['index']: value 
        for checkbox_id, value in zip(checkbox_ids, checkbox_values)
    }
    print("Selected Data Types:", selected_data_types)

    # Collecting normalization values
    normalization_selected = normalization_values if normalization_values else []
    print("Selected Normalization:", normalization_selected)

    # Collecting metabolite class
    print("Selected Metabolite Class:", metabolite_class)

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

    download_config = {
        'data_types': selected_data_types,
        'normalization': normalization_selected,
        'metabolite_class': metabolite_class,
        'p_value_comparisons': p_value_comparisons
    }

    print("Download Config:", download_config)

    return download_config


@app.callback(
    Output('toast-container', 'children', allow_duplicate=True),
    Input('store-download-config', 'data'),
    State('store-data-pool', 'data'),
    State('store-data-iso', 'data'),
    State('store-data-lingress', 'data'),
    State('store-metabolite-ratios', 'data'),
    State('store-met-classes', 'data'),
    prevent_initial_call=True
)
def download_sheet_w_options(download_config,
                             pool_data,
                             iso_data,
                             lingress_data,
                             met_ratios,
                             met_classes_selected):
    
    if download_config is None:
        raise PreventUpdate
    
    # Read user selected config for download from stored values into variables
    selected_data_types = download_config.get('data_types', {})
    normalization_selected = download_config.get('normalization', {})

    # Create a list of metabolite classes based on user selection
    class_user_selection = download_config.get('metabolite_class', {})

    if class_user_selection == 'selected':
        met_classes = met_classes_selected['selected_values']

    else:
        met_classes = df_met_group_list['pathway_class'].drop_duplicates().tolist()

    
    p_value_comparisons = download_config.get('p_value_comparisons', {})
    p_value_comparison_combinations = p_value_comparisons['combinations']
    p_value_comparison_corr = p_value_comparisons['pvalue_correction']

    # Check if pool data is selected and available
    if 'download-pool' in selected_data_types and selected_data_types['download-pool']:
        if pool_data is None:
            return generate_toast("error", 
                                  "Error", 
                                  "No uploaded pool data.")
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')

        # Proceed with generating the pool data dataframe
        df_download_pool = get_download_df_pool(df_pool, met_classes, normalization_selected)

    # Check if iso data is selected and available
    if 'download-iso' in selected_data_types and selected_data_types['download-iso']:
        if iso_data is None:
            return generate_toast("error", 
                                  "Error", 
                                  "No uploaded iso data.")
        iso_json_file = io.StringIO(iso_data)
        df_iso = pd.read_json(iso_json_file, orient='split')
        
        # Proceed with generating the iso data dataframe
        df_download_iso = get_download_df_iso(df_iso, met_classes)


    # Check if lingress data is selected and available
    if 'download-lingress' in selected_data_types and selected_data_types['download-lingress']:
        if lingress_data is None:
            return generate_toast("error", 
                                  "Error", 
                                  "No uploaded lingress data.")
        lingress_json_file = io.StringIO(lingress_data)
        df_lingress = pd.read_json(lingress_json_file, orient='split')

        # Proceed with generating the lingress data dataframe
        df_download_lingress = get_download_df_lingress(df_lingress)







