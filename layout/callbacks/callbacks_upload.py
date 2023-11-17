# callbacks_upload.py

from dash.dependencies import Input, Output, State
from dash import html

from app import app
from layout.utilities_security import process_pool_data, process_iso_data


@app.callback(
    Output('store-data-pool', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def store_metabolomics_pool_data(contents, filename):
    """
    Callback function to store the processed metabolomics pool data.
    
    This function takes the contents and filename of an uploaded file as inputs, processes the data
    using the `process_pool_data` function, and stores the resulting JSON string in a Dash Store component
    for later use.
    
    Parameters:
    contents (str): The content of the uploaded file as a base64 encoded string.
    filename (str): The name of the uploaded file.
    
    Returns:
    str: A JSON string representing the processed pool data if the uploaded file has contents, else None.
    """
    
    # Check if the uploaded file has contents
    if contents:
        # If there are contents, process the pool data and return the JSON representation
        return process_pool_data(contents, filename)
    
    # If there are no contents in the uploaded file, return None
    return None


@app.callback(
    Output('store-data-iso', 'data'),
[
    Input('upload-data', 'contents'),
    Input('store-data-pool', 'data')
],  
    State('upload-data', 'filename')
)
def store_metabolomics_iso_data(contents, stored_pool_data, filename):
    """
    Callback function to store the processed metabolomics isotopic data.
    
    This function takes the contents and filename of an uploaded file, along with previously stored pool data,
    as inputs. It processes the isotopic data using the `process_iso_data` function and stores the resulting 
    JSON string in a Dash Store component for later use.
    
    Parameters:
    contents (str): The content of the uploaded file as a base64 encoded string.
    stored_pool_data (str): JSON string representing the previously stored pool data.
    filename (str): The name of the uploaded file.
    
    Returns:
    str: A JSON string representing the processed isotopic data if the uploaded file and stored pool data 
         are present, else None.
    """
    
    # Check if the uploaded file and stored pool data are present
    if contents and stored_pool_data:
        # If both are present, process the isotopic data and return the JSON representation
        return process_iso_data(contents, filename, stored_pool_data)
    
    # If either the uploaded file or stored pool data is missing, return None
    return None


@app.callback(
[
    Output('upload-status-display', 'children'),
    Output('uploaded-filename-display', 'children')
],  
[
    Input('store-data-pool', 'data'),
    Input('store-data-iso', 'data')
], 
    State('upload-data', 'filename')
)
def update_upload_status(stored_pool_data, stored_iso_data, filename):
    """
    Callback function to update the upload status and display the uploaded filename.
    
    This function takes the stored pool and isotopologue data, as well as the filename of the uploaded file,
    to generate appropriate upload status messages and display the filename.
    
    Parameters:
    stored_pool_data (str): JSON string representing the stored pool data.
    stored_iso_data (str): JSON string representing the stored isotopologue data.
    filename (str): The name of the uploaded file.
    
    Returns:
    tuple: A tuple containing HTML components or strings to display the upload status and filename.
    """
    
    # Check if there's no uploaded pool data
    if stored_pool_data is None:
        return 'No data uploaded', ''
    
    # Displaying the name of the uploaded file, if available
    filename_display = f"Uploaded: {filename}" if filename else ''
    
    # Checking the availability of pool and isotopic data to generate the appropriate status message
    if stored_pool_data is not None and stored_iso_data is None:
        # Case: Only pool data is uploaded
        return html.Span('Pool data successfully uploaded', style={'color': 'green'}), filename_display
    elif stored_pool_data is not None and stored_iso_data is not None:
        # Case: Both pool and isotopic data are uploaded
        return html.Span('Both pool and isotopologue data successfully uploaded', style={'color': 'green'}), filename_display
    else:
        # Case: Unexpected error
        print("There was an unexpected error when updating filename status!")
        return 'Unexpected error', filename_display