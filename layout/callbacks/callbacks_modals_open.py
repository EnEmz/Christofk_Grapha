# callback_modals_open.py

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from app import app


@app.callback(
[
    Output('modal-classes', 'is_open'),
    Output('modal-normalization', 'is_open'),
    Output('modal-met-groups', 'is_open'),
    Output('modal-data-order', 'is_open'),
    Output('modal-settings-bulk-heatmap', 'is_open'),
    Output('modal-settings-bulk-isotopologue-heatmap', 'is_open'),
    Output('modal-settings-custom-heatmap', 'is_open'),
    Output('modal-settings-metabolomics', 'is_open'),
    Output('modal-settings-istopomer-distribution', 'is_open'),
    Output('modal-settings-volcano', 'is_open'),
    Output('modal-p-value-metabolomics', 'is_open'),
    Output('modal-p-value-isotopologue-distribution', 'is_open')
],
[
    Input('open-classes', 'n_clicks'),
    Input('open-normalization', 'n_clicks'),
    Input('open-met-groups', 'n_clicks'),
    Input('open-data-order', 'n_clicks'),
    Input('change-settings-bulk-heatmap', 'n_clicks'),
    Input('change-settings-bulk-isotopologue-heatmap', 'n_clicks'),
    Input('change-settings-custom-heatmap', 'n_clicks'),
    Input('change-settings-metabolomics', 'n_clicks'),
    Input('change-settings-isotopologue-distribution', 'n_clicks'),
    Input('change-settings-volcano', 'n_clicks'),
    Input('configure-p-value-metabolomics', 'n_clicks'),
    Input('configure-p-value-isotopologue-distribution', 'n_clicks'),
    Input('update-classes', 'n_clicks'),
    Input('update-normalization', 'n_clicks'),
    Input('update-groups', 'n_clicks'),
    Input('update-data-order', 'n_clicks'),
    Input('update-settings-bulk-heatmap', 'n_clicks'),
    Input('update-settings-bulk-isotopologue-heatmap', 'n_clicks'),
    Input('update-settings-custom-heatmap', 'n_clicks'),
    Input('update-settings-metabolomics', 'n_clicks'),
    Input('update-settings-isotopologue-distribution', 'n_clicks'),
    Input('update-settings-volcano', 'n_clicks'),
    Input('update-p-value-metabolomics', 'n_clicks'),
    Input('update-p-value-isotopologue-distribution', 'n_clicks')
],
[
    State('modal-classes', 'is_open'),
    State('modal-normalization', 'is_open'),
    State('modal-met-groups', 'is_open'),
    State('modal-data-order', 'is_open'),
    State('modal-settings-bulk-heatmap', 'is_open'),
    State('modal-settings-bulk-isotopologue-heatmap', 'is_open'),
    State('modal-settings-custom-heatmap', 'is_open'),
    State('modal-settings-metabolomics', 'is_open'),
    State('modal-settings-istopomer-distribution', 'is_open'),
    State('modal-settings-volcano', 'is_open'),
    State('modal-p-value-metabolomics', 'is_open'),
    State('modal-p-value-isotopologue-distribution', 'is_open')
],
)
def toggle_modal(*args):
    """
    Callback to toggle the visibility of various modals based on button clicks.
    
    Parameters:
    *args: Variable length argument list containing Inputs and States of the function.
    
    Returns:
    tuple: Tuple of boolean values representing the visibility state of each modal.
    """
    ctx = callback_context  # Get callback context
    
    # If no button has been clicked, return the current state of all modals
    if not ctx.triggered:
        return args[24:]
    else:
        button_id = ctx.triggered[0]['prop_id'].split('.')[0]  # Get the id of the clicked button

    modals_open = list(args[24:])  # Current visibility state of all modals

    # Mapping of button ids to their corresponding modal indices
    modal_mapping = {
        'open-classes': 0,
        'open-normalization': 1,
        'open-met-groups': 2,
        'open-data-order': 3,
        'change-settings-bulk-heatmap': 4,
        'change-settings-bulk-isotopologue-heatmap': 5,
        'change-settings-custom-heatmap': 6,
        'change-settings-metabolomics': 7,
        'change-settings-isotopologue-distribution': 8,
        'change-settings-volcano': 9,
        'configure-p-value-metabolomics': 10,
        'configure-p-value-isotopologue-distribution': 11,
        'update-classes': 0,
        'update-normalization': 1,
        'update-groups': 2,
        'update-data-order': 3,
        'update-settings-bulk-heatmap': 4,
        'update-settings-bulk-isotopologue-heatmap': 5,
        'update-settings-custom-heatmap': 6,
        'update-settings-metabolomics': 7,
        'update-settings-isotopologue-distribution': 8,
        'update-settings-volcano': 9,
        'update-p-value-metabolomics': 10,
        'update-p-value-isotopologue-distribution': 11
    }

    # If an update button was clicked, close the corresponding modal
    if button_id.startswith('update-'):
        modals_open[modal_mapping[button_id]] = False
    else:  
        # Toggle the visibility of the corresponding modal
        modals_open[modal_mapping[button_id]] = not modals_open[modal_mapping[button_id]]

    return tuple(modals_open)  # Return the updated visibility state of all modals


