# modals.py

import dash_bootstrap_components as dbc
import dash_ag_grid as dag
from dash import dcc, html

from layout.config import classes_options_w_mets, tooltips, met_class_list_preselected, p_value_correction_options
from layout.utilities_layout import create_button

def build_modal_components():
    modal_components = []
    
    modal_components.append(get_metabolite_ratio_modal())
    
    modal_components.append(get_data_order_modal())
    modal_components.append(get_metabolite_class_modal())
    modal_components.append(get_normalization_modal())
    modal_components.append(get_group_modal())
    
    modal_components.append(get_pvalue_modal_bulk_metabolomics())
    modal_components.append(get_pvalue_modal_isotopologue_distribution())
    
    modal_components.append(get_settings_modal_bulk_heatmap())
    modal_components.append(get_settings_modal_bulk_isotopologue_heatmap())
    modal_components.append(get_settings_modal_custom_heatmap())
    modal_components.append(get_settings_modal_metabolomics())
    modal_components.append(get_settings_modal_iso_distribution())
    modal_components.append(get_settings_modal_volcano())
    modal_components.append(get_settings_modal_lingress())
    
    return modal_components


# Function to create metabolite ratio modal
def get_metabolite_ratio_modal():
    return dbc.Modal(
        children=
        [
            dbc.ModalHeader("Change Metabolite Ratios that are to be displayed."),
            dbc.ModalBody([
                dbc.Row([
                    dbc.Col(html.Div(id='metabolite-ratios-container', children=[]))
                ],
                justify='center',
                align='center'),
                dbc.Row([
                    dbc.Col(dbc.Button("Add Metabolite Ratio", id="add-metabolite-ratio", n_clicks=0, color="info"), 
                            className='just-a-button')
                ],
                justify='center',
                align='center'),
            ]),
            dbc.ModalFooter([
                dbc.Row([
                    dbc.Col(
                        create_button("Clear", "clear-metabolite-ratios", color='warning'),
                        style={"text-align": "center"}
                    ),
                    dbc.Col(
                        create_button("Default", 'restore-metabolite-ratios', color='secondary'),
                        style={"text-align": "center"}
                    ),
                    dbc.Col(
                        create_button("Update", "update-metabolite-ratios", color='success'),
                        style={"text-align": "center"}
                    )
                ])
            ])
        ],
        id="modal-metabolite-ratios",
        size="xl",
        is_open=False
    )


# Function to create data order modal
def get_data_order_modal():
    return dbc.Modal(
        children=
        [
            dbc.ModalHeader("Change ordering of the data that is displayed."),
            dbc.ModalBody(
                html.Div(id='data-order-dnd-container', children=[
                    html.Div('Please group sample replicates to have data ordering enabled. Refer to "Group Sample Replicates for Data Analysis".',
                                                        className='modal-placeholder-message',
                                                        id='data-order-placeholder-message'),
                    dag.AgGrid(
                        id='data-order-grid',
                        columnDefs=[],
                        columnSize="sizeToFit",
                        rowData=[],
                        defaultColDef={
                            'editable': False,
                            'sortable': True,
                            'resizable': True,
                            'filter': 'agTextColumnFilter',
                        },
                    )
                ])
            ),
            dbc.ModalFooter(
                dbc.Button("Update", id="update-data-order", n_clicks=0, color="success")
            )
        ],
        id="modal-data-order",
        size='xl',
        is_open=False
    )


# Function to create metabolite class selection modal
def get_metabolite_class_modal():
    return dbc.Modal(
        children=
        [
            dbc.ModalHeader("Change metabolite classes that are displayed."),
            dbc.ModalBody(
                children=[
                    dbc.Checklist(
                        className='multi-column-checklist',
                        id='met-class-checklist',
                        options=classes_options_w_mets,
                        value=met_class_list_preselected,
                    ),
                    html.Div(tooltips)  # Assuming tooltips is a list of dbc.Tooltip components
                ]
            ),
            dbc.ModalFooter(
                [
                dbc.ButtonGroup(
                    children=
                    [
                        dbc.Button("Select All", id="select-all-classes", n_clicks=0, className="modal-footer-support-button"),
                        dbc.Button("Clear", id="clear-classes", n_clicks=0, className="modal-footer-support-button"),
                    ], className="mr-auto"
                ),
                dbc.Button("Update", id="update-classes", n_clicks=0, color="success")  # This button will stay on the right
                ],
                className="justify-content-between"
            )
        ],
        id="modal-classes",
        size='xl',
        is_open=False,
        backdrop="static"
    )


# Function to create data normalization modal
def get_normalization_modal():
    return dbc.Modal(
        children=
        [
            dbc.ModalHeader("Normalization of the Metabolomics Data"),
            dbc.ModalBody(html.Div(id='normalization-container')),
            dbc.ModalFooter(dbc.Button("Update", id="update-normalization", n_clicks=0, color="success"))
        ],
        id="modal-normalization",
        size='xl',
        is_open=False,
        backdrop="static"
    )


# Function to create groups modal for sample replicates
def get_group_modal():
    return dbc.Modal(
        children=
        [
            dbc.ModalHeader("Groups of Metabolomics Samples for Analysis Graphs"),
            dbc.ModalBody(html.Div(id='group-input-container', className='input-style'), className='flex-container'),
            dbc.ModalFooter(dbc.Button("Update", id="update-groups", n_clicks=0, color="success"))
        ],
        id="modal-met-groups",
        size='xl',
        is_open=False,
        centered=True,
        backdrop="static"
    )
    
    
# Settings modals for plots
# Bulk heatmap
def get_settings_modal_bulk_heatmap():
    return dbc.Modal(
        children=
                [
                    dbc.ModalHeader("Settings for the bulk heatmap."),
                    dbc.ModalBody([
                        dbc.Row([
                             html.Label("General Settings", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label("Height Modifier"),
                                # Slider for height of the plots.
                                dcc.Slider(
                                    id="bulk-heatmap-height-modifier",
                                    min=0.1,
                                    max=3,
                                    step=0.1,
                                    value=1,
                                    marks={0.1: '0.1', 0.5: '0.5', 1: '1', 2: '2', 3: '3'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Width Modifier"),
                                # Slider for the width of the plots.
                                dcc.Slider(
                                    id="bulk-heatmap-width-modifier",
                                    min=0.1,
                                    max=3,
                                    step=0.1,
                                    value=1,
                                    marks={0.1: '0.1', 0.5: '0.5', 1: '1', 2: '2', 3: '3'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Plot Font Style"),
                                # Selection of the font for all text components in the plots.
                                dbc.Select(
                                    id='bulk-heatmap-font-selector',
                                    options=[
                                        {"label": "Arial", "value": "Arial"},
                                        {"label": "Helvetica", "value": "Helvetica"},
                                        {"label": "Times New Roman", "value": "Times New Roman"},
                                        {"label": "Courier New", "value": "Courier New"},
                                        {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                        {"label": "Impact", "value": "Impact"},
                                        {"label": "Verdana", "value": "Verdana"},
                                        {"label": "Georgia", "value": "Georgia"},
                                        {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                        {"label": "Tahoma", "value": "Tahoma"},
                                        {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                        {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                        {"label": "Garamond", "value": "Garamond"},
                                        {"label": "Bookman", "value": "Bookman"},
                                        {"label": "Avant Garde", "value": "Avant Garde"},
                                        # Add more fonts or edit if needed.
                                    ],
                                    value="Arial",  # Default value for fonts
                                    style={'marginTop': '10px'}
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Plot Font Size"),
                                # Slider for changing the font size for all text elements in the plots.
                                dcc.Slider(
                                    id="bulk-heatmap-font-size",
                                    min=5,
                                    max=20,
                                    step=1,
                                    value=12,
                                    marks={5: '5', 20: '20'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            html.Label("Heatmap Colorscale", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label('Decreased Values'),
                                dbc.Input(id='bulk-heatmap-dec-val-color', type='color', value='#08007d')
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label('Unchanged Values'),
                                dbc.Input(id='bulk-heatmap-unch-val-color', type='color', value='#f8f9fa')
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label('Increased Values'),
                                dbc.Input(id='bulk-heatmap-inc-val-color', type='color', value='#b30000')
                            ], className="settings-dbc-col")
                        ], className="settings-dbc-row"),
                        
                        dbc.Row([
                             html.Label("Additional Settings", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label("Significance Dots Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="bulk-pool-heatmap-sig-dots-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Start Gap Column Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="bulk-pool-heatmap-first-gap-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Group Gap Columns Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="bulk-pool-heatmap-group-gaps-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Update", id="update-settings-bulk-heatmap", n_clicks=0, color="success"))
                ],
                id="modal-settings-bulk-heatmap",
                size='xl',
                is_open=False,
                backdrop="static"
            )
    
    
# Bulk heatmap
def get_settings_modal_bulk_isotopologue_heatmap():
    return dbc.Modal(
        children=
                [
                    dbc.ModalHeader("Settings for the bulk Isotopologue heatmap."),
                    dbc.ModalBody([
                        dbc.Row([
                             html.Label("General Settings", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label("Height Modifier"),
                                # Slider for height of the plots.
                                dcc.Slider(
                                    id="bulk-isotopologue-heatmap-height-modifier",
                                    min=0.1,
                                    max=3,
                                    step=0.1,
                                    value=1,
                                    marks={0.1: '0.1', 0.5: '0.5', 1: '1', 2: '2', 3: '3'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Width Modifier"),
                                # Slider for the width of the plots.
                                dcc.Slider(
                                    id="bulk-isotopologue-heatmap-width-modifier",
                                    min=0.1,
                                    max=3,
                                    step=0.1,
                                    value=1,
                                    marks={0.1: '0.1', 0.5: '0.5', 1: '1', 2: '2', 3: '3'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Plot Font Style"),
                                # Selection of the font for all text components in the plots.
                                dbc.Select(
                                    id='bulk-isotopologue-heatmap-font-selector',
                                    options=[
                                        {"label": "Arial", "value": "Arial"},
                                        {"label": "Helvetica", "value": "Helvetica"},
                                        {"label": "Times New Roman", "value": "Times New Roman"},
                                        {"label": "Courier New", "value": "Courier New"},
                                        {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                        {"label": "Impact", "value": "Impact"},
                                        {"label": "Verdana", "value": "Verdana"},
                                        {"label": "Georgia", "value": "Georgia"},
                                        {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                        {"label": "Tahoma", "value": "Tahoma"},
                                        {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                        {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                        {"label": "Garamond", "value": "Garamond"},
                                        {"label": "Bookman", "value": "Bookman"},
                                        {"label": "Avant Garde", "value": "Avant Garde"},
                                        # Add more fonts or edit if needed.
                                    ],
                                    value="Arial",  # Default value for fonts
                                    style={'marginTop': '10px'}
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Plot Font Size"),
                                # Slider for changing the font size for all text elements in the plots.
                                dcc.Slider(
                                    id="bulk-isotopologue-heatmap-font-size",
                                    min=5,
                                    max=20,
                                    step=1,
                                    value=12,
                                    marks={5: '5', 20: '20'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            html.Label("Heatmap Colorscale", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label('Unchanged Values'),
                                dbc.Input(id='bulk-isotopologue-heatmap-unch-val-color', type='color', value='#f8f9fa')
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label('Increased Values'),
                                dbc.Input(id='bulk-isotopologue-heatmap-inc-val-color', type='color', value='#b30000')
                            ], className="settings-dbc-col")
                        ], className="settings-dbc-row"),
                        
                        dbc.Row([
                             html.Label("Additional Settings", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label("Significance Dots Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="bulk-isotopologue-heatmap-sig-dots-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Start Gap Column Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="bulk-isotopologue-heatmap-first-gap-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Group Gap Columns Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="bulk-isotopologue-heatmap-group-gaps-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Update", id="update-settings-bulk-isotopologue-heatmap", n_clicks=0, color="success"))
                ],
                id="modal-settings-bulk-isotopologue-heatmap",
                size='xl',
                is_open=False,
                backdrop="static"
            )    
    
    
# Custom heatmap
def get_settings_modal_custom_heatmap():
    return dbc.Modal(
                [
                    dbc.ModalHeader("Settings for the custom heatmap"),
                    dbc.ModalBody([
                        dbc.Row([
                             html.Label("General Settings", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label("Height"),
                                # Slider for height of the plots.
                                dcc.Slider(
                                    id="custom-heatmap-height-modifier",
                                    min=0.1,
                                    max=2,
                                    step=0.1,
                                    value=1,
                                    marks={0.1: '0.1', 0.5: '0.5', 1: '1', 2: '2'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Width"),
                                # Slider for the width of the plots.
                                dcc.Slider(
                                    id="custom-heatmap-width-modifier",
                                    min=0.1,
                                    max=2,
                                    step=0.1,
                                    value=1,
                                    marks={0.1: '0.1', 0.5: '0.5', 1: '1', 2: '2'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Plot Font Style"),
                                # Selection of the font for all text components in the plots.
                                dbc.Select(
                                    id='custom-heatmap-font-selector',
                                    options=[
                                        {"label": "Arial", "value": "Arial"},
                                        {"label": "Helvetica", "value": "Helvetica"},
                                        {"label": "Times New Roman", "value": "Times New Roman"},
                                        {"label": "Courier New", "value": "Courier New"},
                                        {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                        {"label": "Impact", "value": "Impact"},
                                        {"label": "Verdana", "value": "Verdana"},
                                        {"label": "Georgia", "value": "Georgia"},
                                        {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                        {"label": "Tahoma", "value": "Tahoma"},
                                        {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                        {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                        {"label": "Garamond", "value": "Garamond"},
                                        {"label": "Bookman", "value": "Bookman"},
                                        {"label": "Avant Garde", "value": "Avant Garde"},
                                        # Add more fonts or edit if needed.
                                    ],
                                    value="Arial",  # Default value for fonts
                                    style={'marginTop': '10px'}
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Plot Font Size"),
                                # Slider for changing the font size for all text elements in the plots.
                                dcc.Slider(
                                    id="custom-heatmap-font-size",
                                    min=5,
                                    max=20,
                                    step=1,
                                    value=12,
                                    marks={5: '5', 20: '20'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            html.Label("Heatmap Colorscale", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label('Decreased Values'),
                                dbc.Input(id='custom-heatmap-dec-val-color', type='color', value='#08007d')
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label('Unchanged Values'),
                                dbc.Input(id='custom-heatmap-unch-val-color', type='color', value='#f8f9fa')
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label('Increased Values'),
                                dbc.Input(id='custom-heatmap-inc-val-color', type='color', value='#b30000')
                            ], className="settings-dbc-col")
                        ], className="settings-dbc-row"),
                        
                        dbc.Row([
                             html.Label("Additional Settings", className='sample-group-dropdown-label'),
                            dbc.Col([
                                html.Label("Significance Dots Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[0],
                                            id="custom-heatmap-sig-dots-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Start Gap Column Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="custom-heatmap-first-gap-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Group Gap Columns Present"),
                                dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="custom-heatmap-group-gaps-present",
                                            inline=True
                                        )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Update", id="update-settings-custom-heatmap", n_clicks=0, color="success")
                    )
                ],
                id="modal-settings-custom-heatmap",
                size='xl',
                is_open=False,
                backdrop="static"
            )
    
    
# Metabolomics (both isotopologue and pool)
def get_settings_modal_metabolomics():
    return dbc.Modal(
                [
                    dbc.ModalHeader("Change settings for the bulk metabolomics plots."),
                    dbc.ModalBody([
                        dbc.Row([
                            dbc.Col([
                                html.Label("Height"),
                                # Slider for height of the plots.
                                dcc.Slider(
                                    id="metabolomics-pool-height",
                                    min=100,
                                    max=1500,
                                    step=50,
                                    value=400,
                                    marks={100: '100', 500: '500', 1000: '1000', 1500: '1500'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Width"),
                                # Slider for the width of the plots.
                                dcc.Slider(
                                    id="metabolomics-pool-width",
                                    min=100,
                                    max=2000,
                                    step=50,
                                    value=600,
                                    marks={100: '100', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            dbc.Col([
                                html.Label("Plot Font Style"),
                                # Selection of the font for all text components in the plots.
                                dbc.Select(
                                    id='metabolomics-font-selector',
                                    options=[
                                        {"label": "Arial", "value": "Arial"},
                                        {"label": "Helvetica", "value": "Helvetica"},
                                        {"label": "Times New Roman", "value": "Times New Roman"},
                                        {"label": "Courier New", "value": "Courier New"},
                                        {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                        {"label": "Impact", "value": "Impact"},
                                        {"label": "Verdana", "value": "Verdana"},
                                        {"label": "Georgia", "value": "Georgia"},
                                        {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                        {"label": "Tahoma", "value": "Tahoma"},
                                        {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                        {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                        {"label": "Garamond", "value": "Garamond"},
                                        {"label": "Bookman", "value": "Bookman"},
                                        {"label": "Avant Garde", "value": "Avant Garde"},
                                        # Add more fonts or edit if needed.
                                    ],
                                    value="Arial",  # Default value for fonts
                                    style={'marginTop': '10px'}
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Plot Font Size"),
                                # Slider for changing the font size for all text elements in the plots.
                                dcc.Slider(
                                    id="metabolomics-font-size",
                                    min=5,
                                    max=20,
                                    step=1,
                                    value=14,
                                    marks={5: '5', 20: '20'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Boxgap (distance between groups, use with width)"),
                                # Slider for editing the distance between sample groups elements in the plots.
                                dcc.Slider(
                                    id="metabolomics-pool-boxgap",
                                    min=0,
                                    max=1,
                                    step=0.05,
                                    value=0.5,
                                    marks={0: '0', 1: '1'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                # Slider for editing the distance between sample groups elements in the plots.
                                html.Label("Boxwidth (width of the bar/box of the group)"),
                                dcc.Slider(
                                    id="metabolomics-pool-boxwidth",
                                    min=0,
                                    max=1,
                                    step=0.05,
                                    value=0.3,
                                    marks={0: '0', 1: '1'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        dbc.Row([
                            dbc.Col([
                                # Container for isotopologue plot specific settings.
                                html.Label("Isotopologue Specific Plot Settings", className='sample-group-dropdown-label'),
                                html.Label("Coming soon, work in progress.", className='modal-placeholder-message')
                            ]),
                            dbc.Col([
                                html.Label("Pool Size Specific Plot Settings", className='sample-group-dropdown-label'),
                                 # Container for pool plot specific settings.
                                 dbc.Row([
                                    dbc.Col([
                                        html.Label("Datapoints Visible"),
                                        # Selecting if individual datapoints are visible.
                                        dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="metabolomics-pool-datapoints-visible",
                                            inline=True
                                        )
                                    ], className="settings-dbc-col"),
                                    dbc.Col([
                                        html.Label("Datapoint Size"),
                                        # Slider for changing size of datapoints if visible.
                                        dcc.Slider(
                                            id="metabolomics-pool-datapoint-size",
                                            min=1,
                                            max=20,
                                            step=1,
                                            value=7,
                                            marks={1: '1', 20: '20'},
                                        )
                                    ], className="settings-dbc-col"),
                                    dbc.Col([
                                        html.Label("Datapoint Color"),
                                        # Color selection for the datapoint display color
                                        # Default is black
                                        dbc.Input(id="metabolomics-pool-datapoint-color", type="color", value="#000000")
                                    ], className="settings-dbc-col"),
                                ], className="settings-dbc-row"),
                                 
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Same color for groups"),
                                        # Selection if all colors should be the same for all sample groups
                                        dbc.Checklist(
                                            options=[
                                                {"value": 1},
                                            ],
                                            value=[1],
                                            id="metabolomics-pool-same-color-for-groups",
                                            inline=True
                                        ),
                                    ], className="settings-dbc-col"),
                                    dbc.Col([
                                        # Color selection for all sample groups if same color is checked
                                        dbc.Input(id="metabolomics-pool-data-color", type="color", value="#bdbdbd")
                                    ], className="settings-dbc-col"),
                                ], className="settings-dbc-row"),
                                dbc.Row([
                                    dbc.Col([
                                        html.Label("Uncheck 'Same color for groups' to work"),
                                        # Container for dynamic color selection for every sample group if same color is not checked
                                        html.Div(id='metabolomics-pool-dynamic-checkbox-input')
                                    ], className="settings-dbc-col"),
                                ], className="settings-dbc-row"),
                                 
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                       
                        
                        
                    ]),
                    dbc.ModalFooter(
                        dbc.Button("Update", id="update-settings-metabolomics", n_clicks=0, color="success")
                    ),
                ],
                id="modal-settings-metabolomics",
                size='xl',
                is_open=False,
                backdrop="static"
            )
    

# Isotopologue distribution
def get_settings_modal_iso_distribution():
    return dbc.Modal(
                [
                    dbc.ModalHeader("Change the settings for the isotopologue distribution plot."),
                    dbc.ModalBody([
                        html.Label("Select specific isotopologues for the selected metabolite to be displayed in the isotpologue distribution plot."),
                        dbc.Row([
                            dbc.Col(html.Div(id='isotopologue-distribution-selection-checkboxes', children=[])),
                        ],
                        justify='center',
                        align='center'),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Height"),
                                # Slider for height of the plots.
                                dcc.Slider(
                                    id="isotopologue-distribution-height",
                                    min=100,
                                    max=1500,
                                    step=50,
                                    value=400,
                                    marks={100: '100', 500: '500', 1000: '1000', 1500: '1500'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Width"),
                                # Slider for the width of the plots.
                                dcc.Slider(
                                    id="isotopologue-distribution-width",
                                    min=100,
                                    max=2000,
                                    step=50,
                                    value=1000,
                                    marks={100: '100', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        
                        dbc.Row([
                            dbc.Col([
                                html.Label("Plot Font Style"),
                                # Selection of the font for all text components in the plots.
                                dbc.Select(
                                    id='isotopologue-distribution-font-selector',
                                    options=[
                                        {"label": "Arial", "value": "Arial"},
                                        {"label": "Helvetica", "value": "Helvetica"},
                                        {"label": "Times New Roman", "value": "Times New Roman"},
                                        {"label": "Courier New", "value": "Courier New"},
                                        {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                        {"label": "Impact", "value": "Impact"},
                                        {"label": "Verdana", "value": "Verdana"},
                                        {"label": "Georgia", "value": "Georgia"},
                                        {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                        {"label": "Tahoma", "value": "Tahoma"},
                                        {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                        {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                        {"label": "Garamond", "value": "Garamond"},
                                        {"label": "Bookman", "value": "Bookman"},
                                        {"label": "Avant Garde", "value": "Avant Garde"},
                                        # Add more fonts or edit if needed.
                                    ],
                                    value="Arial",  # Default value for fonts
                                    style={'marginTop': '10px'}
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Plot Font Size"),
                                # Slider for changing the font size for all text elements in the plots.
                                dcc.Slider(
                                    id="isotopologue-distribution-font-size",
                                    min=5,
                                    max=20,
                                    step=1,
                                    value=14,
                                    marks={5: '5', 20: '20'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                html.Label("Bargap (distance between groups, use with width)"),
                                # Slider for editing the distance between sample groups elements in the plots.
                                dcc.Slider(
                                    id="isotopologue-distribution-bargap",
                                    min=0,
                                    max=1,
                                    step=0.05,
                                    value=0.1,
                                    marks={0: '0', 1: '1'},
                                )
                            ], className="settings-dbc-col"),
                            dbc.Col([
                                # Slider for editing the distance between sample groups elements in the plots.
                                html.Label("Boxwidth (width of the bar/box of the group)"),
                                dcc.Slider(
                                    id="isotopologue-distribution-barwidth",
                                    min=0,
                                    max=1,
                                    step=0.05,
                                    value=0.2,
                                    marks={0: '0', 1: '1'},
                                )
                            ], className="settings-dbc-col"),
                        ], className="settings-dbc-row"),
                        ]),
                    dbc.ModalFooter(
                        dbc.Button("Update", id="update-settings-isotopologue-distribution", n_clicks=0, color="success")
                    )
                ],
                id="modal-settings-istopomer-distribution",
                size='xl',
                is_open=False,
                backdrop="static"
            )
    

# Volcano
def get_settings_modal_volcano():
    return dbc.Modal(
            [
                dbc.ModalHeader("Settings for the volcano plot"),
                dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Height"),
                            # Slider for height of the volcano plot.
                            dcc.Slider(
                                id="volcano-plot-height",
                                min=100,
                                max=2000,
                                step=50,
                                value=800,
                                marks={100: '100', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Width"),
                            # Slider for the width of the volcano plot.
                            dcc.Slider(
                                id="volcano-plot-width",
                                min=100,
                                max=2000,
                                step=50,
                                value=800,
                                marks={100: '100', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000'},
                            )
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Plot Font Style"),
                            # Selection of the font for all text components in the plots.
                            dbc.Select(
                                id='volcano-plot-font-selector',
                                options=[
                                    {"label": "Arial", "value": "Arial"},
                                    {"label": "Helvetica", "value": "Helvetica"},
                                    {"label": "Times New Roman", "value": "Times New Roman"},
                                    {"label": "Courier New", "value": "Courier New"},
                                    {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                    {"label": "Impact", "value": "Impact"},
                                    {"label": "Verdana", "value": "Verdana"},
                                    {"label": "Georgia", "value": "Georgia"},
                                    {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                    {"label": "Tahoma", "value": "Tahoma"},
                                    {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                    {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                    {"label": "Garamond", "value": "Garamond"},
                                    {"label": "Bookman", "value": "Bookman"},
                                    {"label": "Avant Garde", "value": "Avant Garde"},
                                    # Add more fonts or edit if needed.
                                ],
                                value="Arial",  # Default value for fonts
                                style={'marginTop': '10px'}
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Plot Font Size"),
                            # Slider for changing the font size for all text elements in the plots.
                            dcc.Slider(
                                id="volcano-plot-font-size",
                                min=5,
                                max=20,
                                step=1,
                                value=14,
                                marks={5: '5', 20: '20'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Datapoint Size"),
                            # Slider for changing size of datapoints if visible.
                            dcc.Slider(
                                id="volcano-plot-datapoint-size",
                                min=2,
                                max=20,
                                step=1,
                                value=7,
                                marks={2: '2', 20: '20'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Not Significant Datapoint Color"),
                            # Color selection for the not significant datapoint display color
                            dbc.Input(id="volcano-plot-datapoint-color", type="color", value="#A8A8A8")
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Fold Change Cutoff Visible"),
                            dbc.Checklist(
                                options=[
                                    {"value": 1},
                                ],
                                value=[1],
                                id="volcano-plot-fc-cutoff-visible",
                                inline=True
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Fold Change Cutoff Value"),
                            dcc.Input(
                                id='volcano-plot-fc-value-input',
                                type='number',
                                min=0.1,
                                step=0.1,
                                value=1,
                                placeholder='Enter a positive number'
                            ),
                        ], width=2, className="settings-dbc-col"),
                        dbc.Col([
                            html.Label('p-value Cutoff Visible'),
                            dbc.Checklist(
                                options=[
                                    {"value": 1},
                                ],
                                value=[1],
                                id="volcano-plot-pvalue-cutoff-visible",
                                inline=True
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label('p-value Cutoff Text Visible'),
                            dbc.Checklist(
                                options=[
                                    {"value": 1},
                                ],
                                value=[1],
                                id="volcano-plot-pvalue-cutoff-text-visible",
                                inline=True
                            )
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        html.Label('Increasing value colors'),
                        dbc.Col([
                            html.Label('* Color'),
                            dbc.Input(id="volcano-plot-color-inc-1", type="color", value="#d58585")
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label('** Color'),
                            dbc.Input(id="volcano-plot-color-inc-2", type="color", value="#ff0000")
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label('*** Color'),
                            dbc.Input(id="volcano-plot-color-inc-3", type="color", value="#850000")
                        ], className="settings-dbc-col")
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        html.Label('Decreasing value colors'),
                        dbc.Col([
                            html.Label('* Color'),
                            dbc.Input(id="volcano-plot-color-dec-1", type="color", value="#6475e3")
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label('** Color'),
                            dbc.Input(id="volcano-plot-color-dec-2", type="color", value="#002aff")
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label('*** Color'),
                            dbc.Input(id="volcano-plot-color-dec-3", type="color", value="#002185")
                        ], className="settings-dbc-col")
                    ], className="settings-dbc-row"),
                ]),
                dbc.ModalFooter(
                    dbc.Button("Update", id="update-settings-volcano", n_clicks=0, color="success")
                )
            ], 
            id="modal-settings-volcano", 
            size='xl', 
            is_open=False,
            backdrop="static"
        )
    
      
def get_pvalue_modal_bulk_metabolomics():
    return dbc.Modal(
                [
                    dbc.ModalHeader("Configure p-value calculations for metabolomics data."),
                    dbc.ModalBody([
                        dbc.Row([
                            dbc.Col(html.Div(id='p-value-data-order-metabolomics', children=[])),
                        ],
                        justify='center',
                        align='center'),
                        dbc.Row([
                            dbc.Col(dbc.Button("Add a p value Comparison", id="add-pvalue-metabolomics-dropdown", n_clicks=0, color="info"), className='just-a-button'),
                        ],
                        justify='center',
                        align='center'),
                        # Container for selecting sample group pairs for p value comparison.
                        html.Div(id='p-value-metabolomics-dropdown-container', children=[]),
                    ]),
                    dbc.ModalFooter([
                        dbc.Row([
                            dbc.Col(
                                dcc.Dropdown(
                                    id='bulk-metabolomics-pvalue-correction-selection',
                                    options=p_value_correction_options,
                                    value=p_value_correction_options[0]
                                ),
                                width=5
                            ),
                            dbc.Col(
                                # Option to display calculated numerical p value.
                                dbc.Checklist(
                                    options=[
                                        {"label": "Display numerical p-value", "value": 1}
                                    ],
                                    id="numerical-p-value-checkbox",
                                    inline=True,
                                    value=[]
                                ),
                                width=3,
                                style={"text-align": "center"}
                            ),
                            dbc.Col(
                                dbc.Button("Clear All", id="clear-p-value-metabolomics", n_clicks=0),
                                width=2,
                                style={"text-align": "center"}
                            ),
                            dbc.Col(
                                dbc.Button("Update", id="update-p-value-metabolomics", n_clicks=0, color="success"),
                                width=2,
                                style={"text-align": "center"}
                            )
                        ]),
                    ])
                ],
                id="modal-p-value-metabolomics",
                size='xl',
                is_open=False,
                backdrop="static"   
            )
    
    
def get_pvalue_modal_isotopologue_distribution():
    return dbc.Modal(
                [
                    dbc.ModalHeader("Configure p-value calculations for Isotopologue distribution data."),
                    dbc.ModalBody([
                        dbc.Row([
                            dbc.Col(html.Div(id='p-value-data-order-isotopologue-distribution', children=[]))
                        ],
                        justify='center',
                        align='center'),
                        dbc.Row([
                            dbc.Col(dbc.Button("Add p-value Comparison", id="add-pvalue-isotopologue-distribution-dropdown", n_clicks=0, color="info"), 
                                    className='just-a-button')
                        ],
                        justify='center',
                        align='center'),
                        # Container for selecting sample group pairs for p value comparison.
                        html.Div(id='p-value-isotopologue-distribution-dropdown-container', children=[])
                    ]),
                    dbc.ModalFooter([
                        dbc.Row([
                            dbc.Col(
                            dbc.Checklist(
                                options=[
                                        {"label": "Display numerical p-value", "value": 1}
                                ],
                                id="numerical-p-value-checkbox-isotopologue-distribution",
                                inline=True,
                                value=[]
                            ),
                            width=4,
                            style={"text-align": "center"}
                            ),
                            dbc.Col(
                                dbc.Button("Clear All", id="clear-p-value-isotopologue-distribution", n_clicks=0),
                                width=4,
                                style={"text-align": "center"}
                            ),
                            dbc.Col(
                                dbc.Button("Update", id="update-p-value-isotopologue-distribution", n_clicks=0, color="success"),
                                width=4,
                                style={"text-align": "center"}
                            )
                        ]),
                    ])
                ],
                id="modal-p-value-isotopologue-distribution",
                size='xl',
                is_open=False,
                backdrop="static"
            )
    
    
def get_settings_modal_lingress():
    return dbc.Modal(
        [
            dbc.ModalHeader('Configure settings for the linear regression to metabolomics plots.'),
            
            dbc.ModalBody([
                    dbc.Row([
                        dbc.Col([
                            html.Label("Height"),
                            # Slider for height of the volcano plot.
                            dcc.Slider(
                                id="lingress-plot-height",
                                min=100,
                                max=2000,
                                step=50,
                                value=500,
                                marks={100: '100', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Width"),
                            # Slider for the width of the volcano plot.
                            dcc.Slider(
                                id="lingress-plot-width",
                                min=100,
                                max=2000,
                                step=50,
                                value=800,
                                marks={100: '100', 500: '500', 1000: '1000', 1500: '1500', 2000: '2000'},
                            )
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Plot Font Style"),
                            # Selection of the font for all text components in the plots.
                            dbc.Select(
                                id='lingress-font-selector',
                                options=[
                                    {"label": "Arial", "value": "Arial"},
                                    {"label": "Helvetica", "value": "Helvetica"},
                                    {"label": "Times New Roman", "value": "Times New Roman"},
                                    {"label": "Courier New", "value": "Courier New"},
                                    {"label": "Comic Sans MS", "value": "Comic Sans MS"},
                                    {"label": "Impact", "value": "Impact"},
                                    {"label": "Verdana", "value": "Verdana"},
                                    {"label": "Georgia", "value": "Georgia"},
                                    {"label": "Lucida Sans Unicode", "value": "Lucida Sans Unicode"},
                                    {"label": "Tahoma", "value": "Tahoma"},
                                    {"label": "Trebuchet MS", "value": "Trebuchet MS"},
                                    {"label": "Palatino Linotype", "value": "Palatino Linotype"},
                                    {"label": "Garamond", "value": "Garamond"},
                                    {"label": "Bookman", "value": "Bookman"},
                                    {"label": "Avant Garde", "value": "Avant Garde"},
                                    # Add more fonts or edit if needed.
                                ],
                                value="Arial",  # Default value for fonts
                                style={'marginTop': '10px'}
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Plot Font Size"),
                            # Slider for changing the font size for all text elements in the plots.
                            dcc.Slider(
                                id="lingress-font-size",
                                min=5,
                                max=20,
                                step=1,
                                value=14,
                                marks={5: '5', 20: '20'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Datapoint Size"),
                            # Slider for changing size of datapoints if visible.
                            dcc.Slider(
                                id="lingress-datapoint-size",
                                min=1,
                                max=20,
                                step=1,
                                value=7,
                                marks={1: '1', 10: '10', 20: '20'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Datapoint Color"),
                            # Color selection for the datapoint display color
                            # Default is black
                            dbc.Input(id="lingress-datapoint-color", type="color", value="#000000")
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Line Thickness"),
                            # Slider for changing the font size for all text elements in the plots.
                            dcc.Slider(
                                id="lingress-line-thickness",
                                min=1,
                                max=10,
                                step=1,
                                value=5,
                                marks={1: '1', 5: '5', 10: '10'},
                            )
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Line Color"),
                            dbc.Input(id="lingress-line-color", type="color", value="#FF0000")
                        ], className="settings-dbc-col"),
                        dbc.Col([
                            html.Label("Line Opacity"),
                            # Slider for changing the font size for all text elements in the plots.
                            dcc.Slider(
                                id="lingress-line-opacity",
                                min=0.1,
                                max=1,
                                step=0.1,
                                value=1,
                                marks={0.1: '0.1', 1: '1'},
                            )
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
                    
                    dbc.Row([
                        dbc.Col([
                            html.Label("Show Stats in Graph"),
                            dbc.Checklist(
                                        options=[
                                            {"value": 1},
                                        ],
                                        value=[1],
                                        id="lingress-show-stats-in-graph",
                                        inline=True
                                    )
                        ], className="settings-dbc-col"),
                    ], className="settings-dbc-row"),
            ]),
                    
            dbc.ModalFooter(
                dbc.Button("Update", id="update-settings-lingress", n_clicks=0, color="success")
            )
        ],
        id="modal-settings-lingress",
        size='xl',
        is_open=False,
        backdrop="static"
    )