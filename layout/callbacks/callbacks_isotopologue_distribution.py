# callbacks_isotopologue_distribution.py

import io
import pandas as pd
from plotly.graph_objects import Figure, Bar
from dash import html, dcc, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from layout.toast import generate_toast
from layout.utilities_figure import generate_isotopologue_distribution_figure, add_p_value_annotations_iso_distribution


@app.callback(
    Output('isotopologue-distribution-dropdown', 'options'),
    Input('store-data-iso', 'data'),
)
def update_iso_distribution_dropdown_options(iso_data):
    '''
    Update the dropdown list options for selecting metabolites in the isotopologue distribution section.
    This function is activated when new isotopologue data is present in the 'store-data-iso'. It processes 
    the isotopologue data to extract and sort unique metabolite compounds, updating the dropdown options 
    accordingly. This allows users to select specific metabolites for display in the isotopologue distribution.

    Parameters:
    ----------
    iso_data : json
        JSON-formatted string containing the isotopologue data DataFrame.

    Returns:
    -------
    list
        A list of dictionaries with label-value pairs for the dropdown options, 
        representing the metabolites available for selection in the isotopologue distribution.
    '''
    
    if iso_data is None:
        # If there's no data, return an empty options list
        return []
    else:
        # Converting the JSON string back to a DataFrame
        iso_json_file = io.StringIO(iso_data)
        df_iso = pd.read_json(iso_json_file, orient='split')
        
        # Getting unique compounds from the DataFrame and sorting them in a case-insensitive manner
        unique_compounds = sorted(df_iso['Compound'].unique(), key=lambda x: x.lower())
        
        # Creating a list of option dictionaries to be used in the dropdown component
        options = [{'label': compound, 'value': compound} for compound in unique_compounds]
        
        return options
    
    
@app.callback(
[
    Output('isotopologue-distribution-container', 'children'),
    Output('toast-container', 'children', allow_duplicate=True)
],
[
    Input('generate-isotopologue-distribution', 'n_clicks'),
    Input('store-data-iso', 'data'),
    Input('isotopologue-distribution-dropdown', 'value'),
],
[
    State('store-data-order', 'data'),
    State('store-p-value-isotopologue-distribution', 'data'),
    State('store-settings-isotopologue-distribution', 'data')
],
    prevent_initial_call = True
)
def display_isotopologue_distribution_plot(n_clicks, iso_data, met_name, met_groups, pvalue_info, settings):
    '''
    Display an isotopologue distribution plot based on user-selected parameters and provided data.
    This function is triggered by the 'generate-isotopologue-distribution' button and creates a bar chart 
    showing the distributions of isotopologues for a selected metabolite, including average and standard deviation 
    across different sample groups.

    Parameters:
    ----------
    n_clicks : int
        Number of times the button has been clicked.
    iso_data : json
        JSON-formatted string containing the isotopologue data DataFrame.
    met_name : str
        Name of the selected metabolite from the dropdown.
    met_groups : dict
        Dictionary containing the grouping of samples for analysis.
    pvalue_info : dict
        Information about p-values for statistical significance.
    settings : dict
        Selected or placeholder settings for the isotopologue distribution plot.

    Returns:
    -------
    list
        A list containing dcc.Graph objects for the isotopologue distribution plot.
    '''
    
    ctx = callback_context  # Get callback context to identify which input has triggered the callback
    
    fig = Figure()  # Create a new plotly figure
    
    if not ctx.triggered:
        triggered_id = 'No clicks yet'
    else:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'generate-isotopologue-distribution' and n_clicks > 0:

        if iso_data is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "No uploaded isopotologue (labelling) data detected.")
        
        if met_name is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "No selected metabolite for isotopologue distribution plot.")
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        # Read the isotopologue data from the JSON string
        iso_json_file = io.StringIO(iso_data)
        df_iso = pd.read_json(iso_json_file, orient='split')
        
        # Filter the data for the selected metabolite
        df_iso_met = df_iso[df_iso['Compound'] == met_name].fillna(0).reset_index(drop=True)
        
        # Process and group the sample data based on the input groups
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        
        fig = generate_isotopologue_distribution_figure(df_iso_met, grouped_samples, settings)

        if pvalue_info is not None:
            pvalue_comparisons = pvalue_info['combinations']
            pvalue_numerical = pvalue_info['numerical_bool']
            fig = add_p_value_annotations_iso_distribution(fig, df_iso_met, grouped_samples, pvalue_comparisons, pvalue_numerical, settings)
            

        filename = 'iso_distribution_' + str(met_name)
        
        # Returning the plotly figure as a Dash Graph component within a list
        return [dcc.Graph(
                    id='isotopologue-distribution-plot', 
                    figure=fig, 
                    config={
                        'toImageButtonOptions': {
                            'format': 'svg',
                            'filename': filename,
                            'height': None,
                            'width': None,
                        }
                    }
                )], no_update
            
    else:
        # Prevent the callback from updating the output if conditions are not met
        raise PreventUpdate
