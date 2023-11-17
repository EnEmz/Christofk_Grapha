# tabs.py

import dash_bootstrap_components as dbc
from dash import html, dcc

from layout.utilities_layout import create_dropdown_with_label, create_button

# Gets the dbc.Tabs parent component with all the tabs
def get_tabs_parent():
    return dbc.Tabs(
        id='tabs-parent', 
        children=
            [
                get_tab_bulk_pool_heatmap(),
                get_tab_bulk_isotopologue_heatmap(),
                get_tab_custom_heatmap(),
                get_tab_bulk_metabolomics(),
                get_tab_isotopologue_distribution(),
                get_tab_volcano()
            ]
    )
    
    

# Bulk heatmap tab
def get_tab_bulk_pool_heatmap():
    return dbc.Tab(
        label='Bulk Pool Heatmap', 
        children=[
            dbc.Row([
                dbc.Col(
            
                    create_dropdown_with_label('Control Group',
                                               'bulk-heatmap-control-group-dropdown'),
                width=2),
            ],
            justify='center',
            align='center'),
            
            dbc.Row([
                 dbc.Col(
                     create_button("Generate Bulk Heatmap",
                                             "generate-bulk-heatmap-plot",
                                             color='success'),
                     className='just-a-button'
                 ),
                 
                 dbc.Col(
                     create_button("Change Heatmap Settings",
                                             "change-settings-bulk-heatmap",
                                             color='secondary'),
                     className='just-a-button'
                 )
            ],
            justify='center',
            align='center'),
            
            html.Div(id='normalization-display-container-bulk-heatmap', className='normalization-display'),
            
            dbc.Row([
                dbc.Col(
                    html.Div(id="bulk-heatmap-plot-container", 
                             className='heatmap-plot-container')
                )
            ],
            justify='center',
            align='center'
            )
        ]
    )
    
def get_tab_bulk_isotopologue_heatmap():
    return dbc.Tab(
        label='Bulk isotopologue Heatmap',
        children=[
             dbc.Row([
                 dbc.Col(
                     create_button("Generate Bulk Isotopologue Heatmap",
                                             "generate-bulk-isotopologue-heatmap-plot",
                                             color='success'),
                     className='just-a-button'
                 ),
                 
                 dbc.Col(
                     create_button("Change Heatmap Settings",
                                             "change-settings-bulk-isotopologue-heatmap",
                                             color='secondary'),
                     className='just-a-button'
                 )
            ],
            justify='center',
            align='center'),
             
            html.Div(
                id="loader-wrapper-bulk-Isotopologue-heatmap", 
                children=[
                    dcc.Loading(id='loading-bulk-isotopologue-heatmap',
                                type='circle',
                                fullscreen=False,
                                # Container for the bulk metabolomics plots
                                children=html.Div(id="bulk-isotopologue-heatmap-plot-container", 
                                                  className='heatmap-plot-container')
                    )
            ]),
        ]
    )
                    
# Custom heatmap tab                    
def get_tab_custom_heatmap():
    return dbc.Tab(
        label='Custom Heatmap', 
        children=[
            dbc.Row([
                dbc.Col(
                    create_dropdown_with_label('Make a list of metabolites for a custom heatmap',
                                               'custom-heatmap-dropdown-list',
                                                placeholder="Select a list of metabolite names",
                                                multi=True),
                    width=7),
            ],
            justify='center',
            align='center'),
            
            dbc.Row([
                dbc.Col(
                    create_dropdown_with_label('Control Group',
                                                'custom-heatmap-control-group-dropdown'),
                    width=2),
            ],
            justify='center',
            align='center'),
            
            dbc.Row([
                 dbc.Col(
                     create_button("Generate Custom Heatmap",
                                             "generate-custom-heatmap-plot",
                                             color='success'),
                     className='just-a-button'
                 ),
                 
                 dbc.Col(
                     create_button("Change Heatmap Settings",
                                             "change-settings-custom-heatmap",
                                             color='secondary'),
                     className='just-a-button'
                 )
            ],
            justify='center',
            align='center'),
            
            html.Div(id='normalization-display-container-custom-heatmap', className='normalization-display'),
            
            dbc.Row([
                dbc.Col(
                    html.Div(id="custom-heatmap-plot-container", 
                             className='heatmap-plot-container')
                )
            ],
            justify='center',
            align='center'
            )
        ]
    )
    
# Bulk metabolomics tab
def get_tab_bulk_metabolomics():
    return dbc.Tab(
        label="Bulk Metabolomics",
        children=[
            dbc.Row([
                dbc.Col(
                    create_button("Configure p-value Calculations",
                                            "configure-p-value-metabolomics",
                                            color="info"),
                    className='just-a-button'
                ),
                dbc.Col(
                    create_button("Generate Metabolomics Plots",
                                            "generate-metabolomics",
                                            color="success"),
                    className='just-a-button'
                ),
                dbc.Col(
                    create_button("Change Metabolomics Plot Settings",
                                            "change-settings-metabolomics",
                                            color="secondary"),
                    className='just-a-button'
                ),
            ],
            justify='center',
            align='center'
            ),
            
            html.Div(id='normalization-display-container-bulk-metabolomics', className='normalization-display'),
            
            html.Div(
                id="loader-wrapper-metabolomics", 
                children=[
                    dcc.Loading(id='loading-metabolomics',
                                type='circle',
                                fullscreen=False,
                                # Container for the bulk metabolomics plots
                                children=html.Div(id='metabolomics-plot-container')
                    )
            ])
        ]
    )
    
    
# isotopologue distribution tab
def get_tab_isotopologue_distribution():
    return dbc.Tab(
        label="Isotopologue Distribution",
        children=[
            dbc.Row([
                dbc.Col(
                    create_dropdown_with_label("Select a Metabolite for Isotopologue Distribution Plot",
                                                         "isotopologue-distribution-dropdown",
                                                         placeholder="Select a metabolite name"),
                width=3)
            ],
            justify='center',
            align='center'),
            
            dbc.Row([
                dbc.Col(
                    create_button("Configure p-value Calculations",
                                            "configure-p-value-isotopologue-distribution",
                                            color="info"),
                    className='just-a-button'
                ),
                dbc.Col(
                    create_button("Generate Metabolomics Plots",
                                            "generate-isotopologue-distribution",
                                            color="success"),
                    className='just-a-button'
                ),
                dbc.Col(
                    create_button("Change Metabolomics Plot Settings",
                                            "change-settings-isotopologue-distribution",
                                            color="secondary"),
                    className='just-a-button'
                ),
            ],
            justify='center',
            align='center'
            ),
            
            html.Div(id='isotopologue-distribution-container', 
                     children=[
                        dcc.Graph(id='isotopologue-distribution-plot', 
                                  style={'display': 'none'})
                     ],
                     className='graph-container'
            )
        ]
    )
    
    
def get_tab_volcano():
    return dbc.Tab(
        label="Volcano Plot",
        children=[
            dbc.Row([
                dbc.Col(
                    create_dropdown_with_label("Control Group",
                                                         "volcano-control-group-dropdown"),
                width=2),
                
                dbc.Col(
                    create_dropdown_with_label("Condition Group",
                                                         "volcano-condition-group-dropdown"),
                width=2)
            ],
            justify='center',
            align='center'),
            
            dbc.Row([
                dbc.Col(
                    create_button("Mark Significant Points",
                                            "volcano-click-significant-points",
                                            color="info"),
                    className='just-a-button'
                ),
                dbc.Col(
                    create_button("Generate Volcano Plot",
                                            "generate-volcano-plot",
                                            color="success"),
                    className='just-a-button'
                ),
                dbc.Col(
                    create_button("Change Volcano Settings",
                                            "change-settings-volcano",
                                            color="secondary"),
                    className='just-a-button'
                )
            ],
            justify='center',
            align='center'),
            
            dbc.Row([
                dbc.Col(
                    create_dropdown_with_label("Search for a Metabolite in the Volcano Plot",
                                                         "volcano-search-dropdown",
                                                         placeholder="Search or Select a metabolite name"),
                width=3)
            ],
            justify='center',
            align='center'),
            
            html.Div(id='normalization-display-container-volcano', className='normalization-display'),
            
            dbc.Row([
                dbc.Col(
                    html.Div(
                        dcc.Graph(id='volcano-plot', 
                                  style={'display': 'none'}, 
                                  className='graph-container'),
                        id="volcano-plot-container")
                )
            ],
            justify='center',
            align='center')
        ]
    )