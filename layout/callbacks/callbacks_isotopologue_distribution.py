# callbacks_isotopologue_distribution.py

import io
import pandas as pd
from plotly.graph_objects import Figure, Bar
from dash import html, dcc, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from layout.toast import generate_toast
from layout.utilities_figure import generate_isotopologue_distribution_figure, add_p_value_annotations_iso_distribution, generate_corrected_pvalues, filter_and_order_isotopologue_data_by_met_class


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
    Output('isotopologue-distribution-container', 'children', allow_duplicate=True),
    Output('toast-container', 'children', allow_duplicate=True)
],
    Input('generate-isotopologue-distribution', 'n_clicks'),
[
    State('store-data-iso', 'data'),
    State('isotopologue-distribution-dropdown', 'value'),
    State('store-data-order', 'data'),
    State('store-p-value-isotopologue-distribution', 'data'),
    State('store-settings-isotopologue-distribution', 'data'),
    State('store-isotopologue-distribution-selection', 'data')
],
    prevent_initial_call=True
)
def display_single_isotopologue_distribution_plot(n_clicks_single, iso_data, met_name, met_groups, pvalue_info, settings, selected_isos):
    '''
    Display an isotopologue distribution plot for a single selected compound.

    Parameters:
    ----------
    n_clicks_single : int
        Number of times the single compound button has been clicked.
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
    selected_isos: list
        Select isotopologues to be displayed in the isotopologue distribution plot.

    Returns:
    -------
    list
        A list containing dcc.Graph objects for the isotopologue distribution plot.
    '''
    
    ctx = callback_context  # Get callback context to identify which input has triggered the callback

    if not ctx.triggered:
        raise PreventUpdate

    if n_clicks_single > 0:
        # Validate inputs and display toasts if necessary
        if not iso_data:
            return no_update, generate_toast("error", "Error", "No uploaded isotopologue (labelling) data detected.")

        if not met_groups:
            return no_update, generate_toast("error", "Error", "No selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")

        if met_name is None:
            return no_update, generate_toast("error", "Error", "No selected metabolite for isotopologue distribution plot.")

        try:
            # Read the isotopologue data from the JSON string
            iso_json_file = io.StringIO(iso_data)
            df_iso = pd.read_json(iso_json_file, orient='split')
        except ValueError as e:
            return no_update, generate_toast("error", "Error", "Failed to read isotopologue data.")

        df_iso_met = df_iso[df_iso['Compound'] == met_name].fillna(0).reset_index(drop=True)

        if selected_isos:
            selected_isos = [int(iso) for iso in selected_isos]
        else:
            selected_isos = df_iso_met['C_Label'].dropna().unique().tolist()

        df_iso_met = df_iso_met[df_iso_met['C_Label'].isin(selected_isos)]
        grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}

        fig = generate_isotopologue_distribution_figure(df_iso_met, grouped_samples, settings)

        corrected_pvalues_iso = None

        if pvalue_info is not None:
            pvalue_comparisons = pvalue_info['combinations']
            pvalue_numerical = pvalue_info['numerical_bool']
            pvalue_correction = pvalue_info['pvalue_correction']

            if pvalue_correction != 'none':
                corrected_pvalues_iso = generate_corrected_pvalues(df_iso, grouped_samples, pvalue_comparisons, pvalue_correction, 'isodistribution')

            fig = add_p_value_annotations_iso_distribution(fig,
                                                           df_iso_met,
                                                           met_name,
                                                           grouped_samples,
                                                           pvalue_comparisons,
                                                           pvalue_numerical,
                                                           corrected_pvalues_iso,
                                                           settings)

        filename = 'iso_distribution_' + str(met_name)

        return [html.Div([
            html.H5(met_name, className='met-name-style'),
            dcc.Graph(
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
            )
        ])], no_update

    raise PreventUpdate


@app.callback(
[
    Output('isotopologue-distribution-container', 'children'),
    Output('toast-container', 'children', allow_duplicate=True)
],
    Input('generate-isotopologue-distribution-all', 'n_clicks'),
[
    State('store-data-iso', 'data'),
    State('store-data-order', 'data'),
    State('store-met-classes', 'data'),
    State('store-p-value-isotopologue-distribution', 'data'),
    State('store-settings-isotopologue-distribution', 'data'),
    State('store-isotopologue-distribution-selection', 'data')
],
prevent_initial_call=True
)
def display_all_isotopologue_distribution_plots(n_clicks_all, iso_data, met_groups, met_classes, pvalue_info, settings, selected_isos):
    '''
    Display isotopologue distribution plots for all compounds.

    Parameters:
    ----------
    n_clicks_all : int
        Number of times the all compounds button has been clicked.
    iso_data : json
        JSON-formatted string containing the isotopologue data DataFrame.
    met_groups : dict
        Dictionary containing the grouping of samples for analysis.
    met_classes : list
        User-selected metabolite classes.
    pvalue_info : dict
        Information about p-values for statistical significance.
    settings : dict
        Selected or placeholder settings for the isotopologue distribution plot.
    selected_isos: list
        Select isotopologues to be displayed in the isotopologue distribution plot.

    Returns:
    -------
    list
        A list containing dcc.Graph objects for the isotopologue distribution plot.
    '''
    
    ctx = callback_context  # Get callback context to identify which input has triggered the callback

    if not ctx.triggered:
        raise PreventUpdate

    if n_clicks_all > 0:

        # Validate inputs and display toasts if necessary
        if not iso_data:
            return no_update, generate_toast("error", "Error", "No uploaded isotopologue (labelling) data detected.")

        if not met_groups:
            return no_update, generate_toast("error", "Error", "No selected sample groups for grouping replicates. Refer to 'Group Sample Replicates for Data Analysis.'")

        try:
            # Read the isotopologue data from the JSON string
            iso_json_file = io.StringIO(iso_data)
            df_iso = pd.read_json(iso_json_file, orient='split')
        except ValueError as e:
            return no_update, generate_toast("error", "Error", "Failed to read isotopologue data.")
        
        # Filter and order the df_iso based on met_classes
        filtered_ordered_df, compound_metadata_df = filter_and_order_isotopologue_data_by_met_class(df_iso, met_classes['selected_values'])

        unique_compounds = filtered_ordered_df['Compound'].unique()
        figures_mets = []

        last_class = None

        for compound in unique_compounds:
            current_class = compound_metadata_df[compound_metadata_df['Compound'] == compound]['pathway_class'].iloc[0]

            if current_class != last_class:
                # Add a header for the new metabolite class
                figures_mets.append(html.H3(current_class, className='met-class-style'))
                last_class = current_class

            df_iso_met = filtered_ordered_df[filtered_ordered_df['Compound'] == compound].fillna(0).reset_index(drop=True)

            if selected_isos:
                selected_isos = [int(iso) for iso in selected_isos]
            else:
                selected_isos = df_iso_met['C_Label'].dropna().unique().tolist()

            df_iso_met = df_iso_met[df_iso_met['C_Label'].isin(selected_isos)]
            grouped_samples = {group: samples for group, samples in met_groups.items() if group and samples}

            figure_met_iso = generate_isotopologue_distribution_figure(df_iso_met, grouped_samples, settings)
            iso_filename = 'iso_' + str(compound)

            corrected_pvalues_iso = None

            if pvalue_info is not None:
                pvalue_comparisons = pvalue_info['combinations']
                pvalue_numerical = pvalue_info['numerical_bool']
                pvalue_correction = pvalue_info['pvalue_correction']

                if pvalue_correction != 'none':
                    corrected_pvalues_iso = generate_corrected_pvalues(filtered_ordered_df, grouped_samples, pvalue_comparisons, pvalue_correction, 'isodistribution')

                figure_met_iso = add_p_value_annotations_iso_distribution(figure_met_iso,
                                                                          df_iso_met,
                                                                          compound,
                                                                          grouped_samples,
                                                                          pvalue_comparisons,
                                                                          pvalue_numerical,
                                                                          corrected_pvalues_iso,
                                                                          settings)

            figures_mets.append(html.Div([
                html.H4(compound, className='met-name-style'),
                dcc.Graph(
                    figure=figure_met_iso,
                    config={
                        'toImageButtonOptions': {
                            'format': 'svg',
                            'filename': iso_filename,
                            'height': None,
                            'width': None,
                        }
                    },
                )
            ], style={'padding-bottom': '10%'}))

        return html.Div(figures_mets), no_update

    raise PreventUpdate