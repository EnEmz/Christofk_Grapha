# callback_modals_open.py

from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
from dash import callback_context

from app import app


def map_button_to_modal():
    """
    Maps modal IDs to their corresponding button IDs. Each modal is associated with multiple buttons.
    """
    
    return {
        
        'modal-metabolite-ratios': ['open-metabolite-ratios', 'update-metabolite-ratios'],
        'modal-download-data': ['open-download-data', 'download-data-button'],
        
        'modal-classes': ['open-classes', 'update-classes'],
        'modal-normalization': ['open-normalization', 'update-normalization'],
        'modal-met-groups': ['open-met-groups', 'update-groups'],
        'modal-data-order': ['open-data-order', 'update-data-order'],
        
        'modal-settings-bulk-heatmap': ['change-settings-bulk-heatmap', 'update-settings-bulk-heatmap'],
        'modal-settings-bulk-isotopologue-heatmap': ['change-settings-bulk-isotopologue-heatmap', 'update-settings-bulk-isotopologue-heatmap'],
        'modal-settings-custom-heatmap': ['change-settings-custom-heatmap', 'update-settings-custom-heatmap'],
        'modal-settings-metabolomics': ['change-settings-metabolomics', 'update-settings-metabolomics'],
        'modal-settings-istopomer-distribution': ['change-settings-isotopologue-distribution', 'update-settings-isotopologue-distribution'],
        'modal-settings-volcano': ['change-settings-volcano', 'update-settings-volcano'],
        'modal-settings-lingress': ['change-settings-lingress', 'update-settings-lingress'],
        
        'modal-p-value-metabolomics': ['configure-p-value-metabolomics', 'update-p-value-metabolomics'],
        'modal-p-value-isotopologue-distribution': ['configure-p-value-isotopologue-distribution', 'update-p-value-isotopologue-distribution']
    }

def manage_modal_state(current_states, triggered_button):
    """
    Manages the state of modals based on the button clicked.

    Parameters:
    ----------
    current_states: dict
        Current state of all modals.
    triggered_button: str
        ID of the button that triggered the callback.

    Returns:
    -------
    dict
        Updated state of all modals.
    """
    
    button_modal_mapping = {button: modal for modal, buttons in map_button_to_modal().items() for button in buttons}
    updated_states = current_states.copy()

    if triggered_button in button_modal_mapping:
        modal_id = button_modal_mapping[triggered_button]
        updated_states[modal_id] = not current_states[modal_id]

    return updated_states


@app.callback(
    [Output(modal_id, 'is_open') for modal_id in map_button_to_modal().keys()],
    [Input(button_id, 'n_clicks') for button_list in map_button_to_modal().values() for button_id in button_list],
    [State(modal_id, 'is_open') for modal_id in map_button_to_modal().keys()],
)
def toggle_modal(*args):
    """
    Toggles the open state of various modals in a Dash application.

    This function is triggered by a set of button clicks, each associated with a modal. It determines
    which button was clicked and toggles the open state of the corresponding modal. If no button
    has been clicked, it returns the current state of all modals.

    The function handles a dynamic number of modals and buttons, which are defined in the 
    `map_button_to_modal` function. This allows for easy extension of the application with new modals 
    and buttons without changing the core logic of this function.

    Parameters:
    ----------
    *args : tuple
        A variable-length argument list. The first part of `args` contains the states of the buttons
        (number of clicks), and the second part contains the states of the modals (whether each is open or closed).

    Returns:
    -------
    tuple
        A tuple of boolean values, each representing the open/closed state of a corresponding modal.

    Note:
    -----
    - The callback context of Dash is used to determine which button was clicked.
    - The structure of the `args` tuple is dependent on the number and order of Inputs and States
      defined in the `@app.callback` decorator of this function.
    """
    
    ctx = callback_context

    # Number of buttons (inputs)
    num_buttons = len([button_id for button_list in map_button_to_modal().values() for button_id in button_list])

    # If no button has been clicked, return the current state of all modals
    if not ctx.triggered:
        return args[num_buttons:]
    
    # Get the id of the clicked button
    button_id = ctx.triggered[0]['prop_id'].split('.')[0]
    
    # Current visibility state of all modals
    current_modal_states = {modal_id: state for modal_id, state in zip(map_button_to_modal().keys(), args[num_buttons:])}

    # Update the modal states
    updated_modal_states = manage_modal_state(current_modal_states, button_id)

    return tuple(updated_modal_states.values())
