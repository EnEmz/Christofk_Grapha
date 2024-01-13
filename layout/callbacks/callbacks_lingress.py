#callbacks_lingress.py

import io
import pandas as pd
from plotly.graph_objects import Figure, Bar
from dash import html, dcc, callback_context, no_update
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate

from app import app
from layout.toast import generate_toast