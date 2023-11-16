# callbacks_isotopomer_distribution.py

import io
import pandas as pd
from plotly.graph_objects import Figure, Bar
from dash import html, dcc, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from layout.toast import generate_toast
from layout.utilities_figure import generate_isotopomer_distribution_figure, add_p_value_annotations_iso_distribution
from layout.config import iso_color_palette

@app.callback(
    Output('isotopomer-distribution-dropdown', 'options'),
    Input('store-data-iso', 'data'),
)
def update_iso_distribution_dropdown_options(iso_data):
    """
    Update the options of the isotopomer distribution dropdown list.
    
    This function is triggered when there's new isotopomer data in the 'store-data-iso'.
    It extracts unique metabolite compounds from the isotopomer data, sorts them,
    and updates the dropdown options, enabling the user to select the metabolites 
    they want to display in the isotopomer distribution.
    
    Parameters:
    - iso_data (json): JSON-formatted string of the isotopomer data DataFrame.
    
    Returns:
    - list: A list of dictionaries containing label and value pairs for the dropdown options.
    """
    
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
    Output('isotopomer-distribution-container', 'children'),
    Output('toast-container', 'children', allow_duplicate=True)
],
[
    Input('generate-isotopomer-distribution', 'n_clicks'),
    Input('store-data-iso', 'data'),
    Input('isotopomer-distribution-dropdown', 'value'),
],
[
    State('store-data-order', 'data'),
    State('store-p-value-isotopomer-distribution', 'data'),
    State('store-settings-isotopomer-distribution', 'data')
],
    prevent_initial_call = True
)
def display_isotopomer_distribution_plot(n_clicks, iso_data, met_name, met_groups, pvalue_info, settings):
    """
    Display the isotopomer distribution plot based on user inputs and selections.
    
    This function is triggered by clicking the 'generate-isotopomer-distribution' button.
    It creates a bar chart representing the isotopomer distributions for selected metabolites,
    including the average and standard deviation calculations across sample groups.
    
    Parameters:
    - n_clicks (int): Number of button clicks.
    - iso_data (json): JSON-formatted string of the isotopomer data DataFrame.
    - met_name (str): Selected metabolite name from the dropdown.
    - met_groups (dict): A dictionary containing sample groupings.
    
    Returns:
    - list: A list containing dcc.Graph object with the isotopomer distribution plot.
    """
    
    # Constants for bar widths and gaps in the plot
    BAR_WIDTH = 0.15
    BAR_GAP = 0.03
    GROUP_GAP = 0.085
    C_LABEL_AXIS_CONST = 0.04
    
    ctx = callback_context  # Get callback context to identify which input has triggered the callback
    
    fig = Figure()  # Create a new plotly figure
    
    if not ctx.triggered:
        triggered_id = 'No clicks yet'
    else:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    if triggered_id == 'generate-isotopomer-distribution' and n_clicks > 0:

        if iso_data is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "No uploaded isopotologue (labelling) data detected.")
        
        if met_name is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "No selected metabolite for isotopomer distribution plot.")
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        # Read the isotopomer data from the JSON string
        iso_json_file = io.StringIO(iso_data)
        df_iso = pd.read_json(iso_json_file, orient='split')
        
        # Filter the data for the selected metabolite
        df_iso_met = df_iso[df_iso['Compound'] == met_name].fillna(0).reset_index(drop=True)
        
        # Process and group the sample data based on the input groups
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        
        fig = generate_isotopomer_distribution_figure(df_iso_met, grouped_samples, settings)

        if pvalue_info is not None:
            pvalue_comparisons = pvalue_info['combinations']
            pvalue_numerical = pvalue_info['numerical_bool']
            fig = add_p_value_annotations_iso_distribution(fig, df_iso_met, grouped_samples, pvalue_comparisons, pvalue_numerical, settings)
            

        filename = 'iso_distribution_' + str(met_name)
        
        # Returning the plotly figure as a Dash Graph component within a list
        return [dcc.Graph(
                    id='isotopomer-distribution-plot', 
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
