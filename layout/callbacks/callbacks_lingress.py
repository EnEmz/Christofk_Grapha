#callbacks_lingress.py

import io
import pandas as pd
from dash import html, dcc, callback_context, no_update
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State

from app import app
from layout.toast import generate_toast
from layout.utilities_figure import normalize_met_pool_data, group_met_pool_data, generate_single_lingress_plot


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
        return []
    
    else:
        lingress_json_file = io.StringIO(lingress_data)
        df_lingress = pd.read_json(lingress_json_file, orient='split')
        unique_variables = sorted(df_lingress['Variable'].unique(), key=lambda x: x.lower())
        options = [{'label': variable, 'value': variable} for variable in unique_variables]
        
        return options


@app.callback(
[
    Output('lingress-plot-container', 'children'),
    Output('toast-container', 'children', allow_duplicate=True)
],
[
    Input('generate-lingress', 'n_clicks'),
    Input('lingress-variable-dropdown', 'value'),
],
[
    State('store-data-lingress', 'data'),
    State('store-data-pool', 'data'),
    State('store-met-classes', 'data'),
    State('store-data-normalization', 'data'),
    State('store-data-order', 'data'),
    State('store-settings-lingress', 'data')
],
    prevent_initial_call = True
)
def display_lingress_plots(n_clicks, var_name, lingress_data, pool_data, met_classes, met_normalization, met_groups, settings):
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
    
    if not ctx.triggered:
        triggered_id = 'No clicks yet'
    else:
        triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if triggered_id == 'generate-lingress' and n_clicks > 0:

        # Validate the presence of pool data
        if pool_data is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Upload a valid metabolomics file.")
            
        if lingress_data is None:
            return no_update, generate_toast("error", "Error", "No uploaded linear regression variable data detected.")
        
        if var_name is None:
            return no_update, generate_toast("error", "Error", "No selected variable for linear regression plot.")
                
        # Check if the user has selected any metabolite classes  and if not return an error toast
        if not met_classes or met_classes['selected_values'] is None:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected metabolite classes. Refer to 'Select Metabolite Classes to be Displayed'.")
        
        # Check if the user has selected the normalization variables and if not return an error toast
        if not met_normalization:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected normalization variables for the data (possible to have none). Refer to 'Change Normalization Variables'.")
        
        # Check if the user has entered any sample groups  and if not return an error toast
        if not met_groups:
            return no_update, generate_toast("error", 
                                             "Error", 
                                             "Not selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")
        
        pool_json_file = io.StringIO(pool_data)
        df_pool = pd.read_json(pool_json_file, orient='split')
        df_pool = df_pool.replace(0, 1000)  # Replace zeros with 1000
        
        lingress_json_file = io.StringIO(lingress_data)
        df_lingress = pd.read_json(lingress_json_file, orient='split')
        
        # Filter the data for the selected external variable
        df_var = df_lingress[df_lingress['Variable'] == var_name].fillna(0).reset_index(drop=True)

        # Filter met_groups to include only items where the value is not None from the Dynamic Input of the user
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}
        
        # Flatten grouped_samples to get a list of all relevant sample columns
        all_samples = [sample for group_samples in grouped_samples.values() for sample in group_samples]

        # Include the first column (index 0)
        df_var_cols_to_keep = [df_var.columns[0]]

        # Add columns starting from the second column (index 1) that are in all_samples
        df_var_cols_to_keep.extend(col for col in df_var.columns[1:] if col in all_samples)

        # Filter the DataFrame with the selected columns
        df_var_filtered = df_var[df_var_cols_to_keep]
        
        normalization_list = met_normalization['selected_values']
        selected_met_classes = met_classes['selected_values']
        
        df_pool_normalized = normalize_met_pool_data(df_pool, grouped_samples, normalization_list)
        df_pool_normalized_grouped = group_met_pool_data(df_pool_normalized, selected_met_classes)
        
        df_pool_normalized_groupby = df_pool_normalized_grouped.groupby('pathway_class', sort=False)
               
        figures_mets = []
        for pathway, group_df in df_pool_normalized_groupby:
            figures_mets.append(html.Div([html.H3(pathway, className='met-class-style')]))

            # Iterate over each row in the grouped_df and generate the graphs
            for _, row in group_df.iterrows():
                
                # Add metabolite name to when a new row is read from the metabolite pool df
                met_name = row['Compound']
                figures_mets.append(html.H5(met_name + ' vs ' + var_name, className='met-name-style'))
                
                # Prepare the data for the plot
                df_met_data = pd.DataFrame(row).T  # Transpose row to DataFrame

                # Generate the plot and statistics
                fig, stats = generate_single_lingress_plot(df_met_data, df_var_filtered, settings)
                
                lingress_filename = 'lingress_' + str(met_name) + '_' + str(var_name)

                # Create Graph component for the plot
                plot_component = dcc.Graph(
                                    figure=fig,
                                    config={
                                        'toImageButtonOptions': {
                                            'format': 'svg',
                                            'filename': lingress_filename,
                                            'height': None,
                                            'width': None,
                                        }
                                    })

                # Create a div to display the statistics
                stats_component = html.Div([
                    html.P(f"Slope: {stats['slope']:.3f} ± {stats['std_err']:.3f}"),
                    html.P(f"Intercept: {stats['intercept']:.3f}"),
                    html.P(f"R-squared: {stats['r_squared']:.3f}"),
                    html.P(f"P-value: {stats['p_value']:.3g}"),
                ], className='stats-container')

                # Add to a row with two columns: one for the plot and one for the stats
                dbc_row = dbc.Row([
                    dbc.Col(plot_component, className= 'bulk-met-graph-col'),
                    dbc.Col(stats_component, width=4)
                ])

                figures_mets.append(dbc_row)

        return html.Div(figures_mets), no_update
    else:
        return no_update, no_update

