# utilities.py

from dash import html, dcc
import dash_bootstrap_components as dbc


def generate_classes_checklist_options_with_met_names(df_met_group_list):
    """
    Generate options for a checklist based on metabolite groupings, with each option having an associated tooltip.
    
    This function takes a DataFrame that contains metabolite data grouped by 'pathway_class' and 'analyte_name'
    and creates checklist options with tooltips for each pathway class. Each tooltip is filled with the list of
    metabolites associated with the corresponding pathway class.

    Parameters:
    - df_met_group_list (pandas.DataFrame): A DataFrame with at least two columns, 'pathway_class' and 'analyte_name'.
      The DataFrame is expected to contain multiple entries for 'analyte_name' associated with each 'pathway_class'.

    Returns:
    - options_with_tooltips (list): A list of dictionaries, where each dictionary represents a checklist option with 'label'
      and 'value' keys. 'label' is a Dash HTML Div that contains an info icon and the pathway class name, styled to facilitate
      tooltips. 'value' is the pathway class name as a string.
    - tooltips (list): A list of Dash Bootstrap Component Tooltip objects. Each tooltip is configured to show/hide with a delay
      and is targeted at the corresponding info icon included with each pathway class checklist option.

    The function groups the DataFrame by 'pathway_class' and iterates over the groups to create a checklist option and tooltip for each.
    The metabolites are listed in the tooltip content, separated by line breaks.
    """
    
    options_with_tooltips = []
    tooltips = []
    for idx, (pathway, metabolites) in enumerate(df_met_group_list.groupby('pathway_class', sort=False)['analyte_name'].apply(list).items()):
        tooltip_id = f"tooltip-{idx}"
        option_label = html.Div(
            [
                # Add tooltip with two spaces for spacing then the pathway name.
                html.I(className="fa fa-info-circle", id=tooltip_id, style = {'border': '5px solid transparent', 
                                                                              'cursor': 'pointer',
                                                                              'marginRight': '5px'}),
                html.Span(pathway),  # The text of the option
            ],
            className="met-class-option-label",  # Additional style to align items
        )

        option = {"label": option_label, "value": pathway}
        options_with_tooltips.append(option)

        tooltip_content_children = []
        for metabolite in metabolites:
            tooltip_content_children.extend([html.Span(metabolite), html.Br()])  # Add metabolite and line break
            
        # The tooltip's content division with text aligned to center
        tooltip_content = html.Div(tooltip_content_children, style={"textAlign": "center"})
        
        tooltip = dbc.Tooltip(
            tooltip_content,
            target=tooltip_id,
            placement="bottom",
            delay={"show": 500, "hide": 250},  # delay showing and hiding the tooltip (in milliseconds)
        )
        tooltips.append(tooltip)

    return options_with_tooltips, tooltips


def create_button(label, id, color='primary', n_clicks=0):
    """
    Creates a Dash Button component with specified properties.

    Parameters:
        label (str): The text to be displayed on the button.
        id (str): The unique identifier for the button.
        color (str, optional): Defines the button color. Defaults to 'primary'.
        n_clicks (int, optional): The number of times the button has been clicked. Defaults to 0.
        class_name (str, optional): The CSS class to be applied to the button. Defaults to 'just-a-button'.

    Returns:
        dash_html_components.Button: A Button component for use in Dash applications.
    """
    return dbc.Button(label, id=id, n_clicks=n_clicks, color=color)


def create_dropdown_with_label(label_text, dropdown_id, label_classname='sample-group-dropdown-label', dropdown_classname='sample-group-dropdown-style', placeholder=None, multi=False):
    """
    Creates a Dash Dropdown component with an associated label, wrapped in a list for easy layout placement.

    Parameters:
        label_text (str): The text to be displayed in the label associated with the dropdown.
        dropdown_id (str): The unique identifier for the dropdown.
        label_classname (str, optional): The CSS class to be applied to the label. Defaults to 'sample-group-dropdown-label'.
        dropdown_classname (str, optional): The CSS class to be applied to the dropdown. Defaults to 'sample-group-dropdown-style'.
        placeholder (str, optional): A placeholder string to be displayed in the dropdown when no option is selected. Defaults to None.
        multi (bool, optional): Allows multiple selections if set to True. Defaults to False.

    Returns:
        list: A list containing the html.Label and Dropdown components for use in Dash applications.
    """
    return [
        html.Label(label_text, className=label_classname),
        dcc.Dropdown(id=dropdown_id, className=dropdown_classname, placeholder=placeholder, multi=multi)
    ]
  

def generate_available_dropdown_options(selected_value, all_values):
    '''
    Generates dropdown options with a specific value disabled.
    
    Parameters:
    ----------
    selected_value : str
        The value that should be disabled in the dropdown options.
        
    all_values : list of str
        All possible values for the dropdown options.
        
    Returns:
    -------
    list
        A list of dictionaries specifying the label, value, and disabled status of each option.
    '''
    options = []
    for value in all_values:
        options.append({
            'label': value, 
            'value': value, 
            'disabled': value == selected_value
        })
    return options


def map_button_to_modal(button_id, current_modal_states):
    """
    Toggles the state of a modal based on the button clicked. This function is used to map button clicks to modal 
    visibility states. When a button associated with a modal is clicked, this function inverts the current 
    visibility state of the respective modal.

    Parameters:
        button_id (str): The ID of the button that has been clicked. This ID is used to identify which modal's 
                         state should be toggled.
        current_modal_states (dict): A dictionary containing the current visibility states of modals, with modal 
                                     IDs as keys and boolean values as values indicating whether each modal is open or closed.

    Returns:
        dict: The updated dictionary with the toggled state of the modal associated with the clicked button.
        
    Example:
        >>> current_modal_states = {'modal-1': False, 'modal-2': True}
        >>> map_button_to_modal('btn-modal-1-open', current_modal_states)
        {'modal-1': True, 'modal-2': True}  # Assuming 'btn-modal-1-open' is associated with 'modal-1'

    The function assumes that the `button_id` provided is correctly mapped to a modal's visibility state 
    within the `current_modal_states` dictionary.
    """
    if button_id in current_modal_states:
        current_modal_states[button_id] = not current_modal_states[button_id]  # Toggle state
    return current_modal_states

