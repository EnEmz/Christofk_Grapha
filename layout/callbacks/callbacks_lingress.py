#callbacks_lingress.py

import io
import pandas as pd
from plotly.graph_objects import Figure, Bar
from dash import html, dcc, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from layout.toast import generate_toast


@app.callback(
    Output('lingress-variable-dropdown', 'options'),
    Input('store-data-lingress', 'data')
)
def update_lingress_dropdown_options(lingress_data):
    '''
    Update the dropdown list options for selecting to variable to perform the linear 
    regression comparison to the metabolomics pool data.
    This function is activated when new linear regression variable data is read from
    the uploaded excel file. The user can select n external variable to do linear
    regression with the metabolomics data.
    
        Parameters:
    ----------
    lingress_data : json
        JSON-formatted string containing the lingress data DataFrame.

    Returns:
    -------
    list
        A list of dictionaries with dropdown options, representing the external
        variables available for selection in the linear regression plotting.
    '''
    
    if lingress_data is None:
        # If there's no data, return an empty options list
        return []
    else:
        # Converting the JSON string back to a DataFrame
        lingress_json_file = io.StringIO(lingress_data)
        df_lingress = pd.read_json(lingress_json_file, orient='split')
        
        # Getting unique variables from the DataFrame and sorting them in a case-insensitive manner
        unique_variables = sorted(df_lingress['Variable'].unique(), key=lambda x: x.lower())
        
        # Creating a list of option dictionaries to be used in the dropdown component
        options = [{'label': variable, 'value': variable} for variable in unique_variables]
        
        return options


@app.callback(
[
    Output('lingress-plot-container', 'children'),
    Output('toast-container', 'children', allow_duplicate=True)
],
[
    Input('generate-lingress', 'n_clicks'),
    Input('store-data-lingress', 'data'),
    Input('lingress-variable-dropdown', 'value'),
],
[
    State('store-data-order', 'data'),
    State('store-settings-lingress', 'data')
],
    prevent_initial_call = True
)
def display_isotopologue_distribution_plot(n_clicks, lingress_data, var_name, met_groups, settings):
    '''
    Display an isotopologue distribution plot based on user-selected parameters and provided data.
    This function is triggered by the 'generate-isotopologue-distribution' button and creates a bar chart 
    showing the distributions of isotopologues for a selected metabolite, including average and standard deviation 
    across different sample groups.

    Parameters:
    ----------
    n_clicks : int
        Number of times the button has been clicked.
    lingress_data : json
        JSON-formatted string containing the linear regression data DataFrame.
    var_name : str
        Name of the selected variable from the linear regression.
    met_groups : dict
        Dictionary containing the grouping of metabolomcics samples for analysis.
    settings : dict
        Selected or placeholder settings for the linear regression plots.

    Returns:
    -------
    list
        A list containing dcc.Graph objects for the linear regression plots.
    '''
    
    ctx = callback_context  # Get callback context to identify which input has triggered the callback
    
    fig = Figure()  # Create a new plotly figure
    
    if not ctx.triggered:
        triggered_id = 'No clicks yet'
    else:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'generate-isotopologue-distribution' and n_clicks > 0:

        if lingress_data is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "No uploaded linear regression variable data detected.")
        
        if var_name is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "No selected variable for linear regression plot.")
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        # Read the isotopologue data from the JSON string
        lingress_json_file = io.StringIO(lingress_data)
        df_lingress = pd.read_json(lingress_json_file, orient='split')
        
        return html.Div("This is going to be the lingress plots.")

