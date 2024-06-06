import pandas as pd
import io
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ALL
from dash.exceptions import PreventUpdate
from dash import html, dcc, no_update, callback_context

from app import app

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
        checkboxes.append(dbc.Col(dbc.Checkbox(id='checkbox-pool', label='Pool Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id='checkbox-pool', label='Pool Data', value=False, disabled=True)))

    if iso_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id='checkbox-iso', label='Isotopologue Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id='checkbox-iso', label='Isotopologue Data', value=False, disabled=True)))

    if lin_data is not None:
        checkboxes.append(dbc.Col(dbc.Checkbox(id='checkbox-lingress', label='Lingress Data', value=True)))
    else:
        checkboxes.append(dbc.Col(dbc.Checkbox(id='checkbox-lingress', label='Lingress Data', value=False, disabled=True)))

    # Ensure checkboxes are in a single row
    return dbc.Row(checkboxes, justify='center')
