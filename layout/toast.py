# toast_component.py
import dash_bootstrap_components as dbc

def generate_toast(toast_type, header, message):
    """
    Generates a toast notification with custom styling.

    This function creates a toast notification using the Dash Bootstrap Components library.
    It applies predefined CSS classes for different toast types (success, error, warning) and 
    ensures that the toast notification appears at the top-right corner of the screen with a fixed position.
    
    Parameters:
    - toast_type (str): The type of the toast to display. Accepts 'success', 'error', or 'warning'.
    - header (str): The header text of the toast notification.
    - message (str): The main message text of the toast notification.

    Returns:
    - dbc.Toast: A Toast component styled and configured to display as a popup notification.
    
    The toast is set to dismiss after a set duration automatically and is styled according to the type 
    specified, which corresponds to custom CSS classes that control the appearance.

    The function is designed to be flexible and can be used throughout a Dash application wherever toast
    notifications are needed. It simplifies the process of creating consistent and styled notifications for
    user actions.

    Note:
    The 'className' attribute of the returned Toast is dynamically set based on the toast_type argument to 
    match the corresponding CSS class for styling.
    """
    
    toast_class = f"toast-{toast_type}"
    
    return dbc.Toast(
        header=header,
        children=message,
        is_open=True,
        dismissable=True,
        # The className property is used to apply your custom CSS classes
        className=toast_class,
        # Override the position to 'fixed' and place at top right
        style={"position": "fixed", "top": 0, "right": 0, "width": 350, "zIndex": 9999},
        duration=4000,  # Duration for auto-dismissal of toast
    )