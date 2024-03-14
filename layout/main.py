# header.py
# Header, Upload and Status Display 
from dash import html, dcc
import dash_bootstrap_components as dbc

from layout.utilities_layout import create_button


def get_main_layout():
    return html.Div([
        dbc.Row([
            dbc.Col(
                get_header(),
                width=6,
                className='print-header'
            ), 
            
            dbc.Col(
                get_upload(),
                width=2,
                className='print-header'
            ),
            
            dbc.Col(
                get_status_display(),
                width=4,
                className='print-header'
            )
        ],
        justify='center',
        align='center'),
        
        dbc.Row([
            dbc.Col(
                create_button("Configure Metabolite Ratios",
                              "open-metabolite-ratios",
                              color='secondary'),
                className='just-a-button'
            )
        ]),
        
        dbc.Row([
            dbc.Col(
                create_button("Select Metabolite Classes to be Displayed",
                              "open-classes"),
                className='just-a-button'
            ),
            
            dbc.Col(
                create_button("Change Normalization Variables",
                              "open-normalization"),
                className='just-a-button'
            ),
            
            dbc.Col(
                create_button("Group Sample Replicates for Data Analysis",
                              "open-met-groups"),
                className='just-a-button'
            ),
            
            dbc.Col(
                create_button("Order the Sample Groups for Display",
                              "open-data-order"),
                className='just-a-button'
            )
        ],
        justify='center',
        align='center',
        className='no-print')
    ])


# Header with styling
def get_header():
    return html.H1("Christofk_Grapha", 
                   style={
                       "textAlign": "center",
                       "padding": "45px 45px",
                       "background": "linear-gradient(to right, #ff8a00 0%, #dd4c4f 100%)",
                       "WebkitBackgroundClip": "text",
                       "WebkitTextFillColor": "transparent"
                   })


# Element to upload the metabolomics data file to
def get_upload():
    return dcc.Upload(
        id="upload-data",
        className='file-upload',
        children=html.Div(["Drag and Drop Metabolomics Excel File or ", html.B("Select Files")]),
        multiple=False
    )
    
    
# Container to update the data reading status after a data upload
def get_status_display():
    return [
        html.Div(id='upload-status-display', 
                 children='No data uploaded', 
                 style={'color': 'red', "textAlign": "center", "padding": "5px"},
                 className='no-print'),
        
        html.Div(id='uploaded-filename-display', 
                 children='', 
                 style={"textAlign": "center", "padding": "5px"})
    ]

