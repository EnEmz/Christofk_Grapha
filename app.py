# app.py

from dash import Dash
import dash_bootstrap_components as dbc

FONT_AWESOME = "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css"

external_stylesheets = [dbc.themes.SOLAR, FONT_AWESOME]

app = Dash(__name__, 
           external_stylesheets=external_stylesheets,
           suppress_callback_exceptions=True
           )

app.title = 'Christofk_Grapha'
server = app.server
