import pandas as pd
import io
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from dash import html, dcc, no_update, callback_context

from app import app
from layout.config import normalization_preselected

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
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'checkbox', 'index': 'download-pool'}, label='Pool Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'checkbox', 'index': 'download-pool'}, label='Pool Data', value=False, disabled=True)))

    if iso_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'checkbox', 'index': 'download-iso'}, label='Isotopologue Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'checkbox', 'index': 'download-iso'}, label='Isotopologue Data', value=False, disabled=True)))

    if lin_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'checkbox', 'index': 'download-lingress'}, label='Lingress Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id={'type': 'checkbox', 'index': 'download-lingress'}, label='Lingress Data', value=False, disabled=True)))

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


