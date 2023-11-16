# content.py

from dash import html

from layout.main import get_main_layout
from layout.storage import build_storage_components
from layout.modals import build_modal_components
from layout.tabs import get_tabs_parent


def create_layout():
    return html.Div(
        children=[
            # For displaying error messages for users
            html.Div(id="toast-container"),
            
            *build_modal_components(),
            
            *build_storage_components(),
            
            get_main_layout(),
            
            get_tabs_parent()
        ]
    )
