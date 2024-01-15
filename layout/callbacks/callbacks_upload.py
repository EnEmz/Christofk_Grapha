# callbacks_upload.py

from dash.dependencies import Input, Output, State
from dash import html

from app import app
from layout.utilities_security import process_pool_data, process_iso_data, process_lingress_data


@app.callback(
    Output('store-data-pool', 'data'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename')
)
def store_metabolomics_pool_data(contents, filename):
    '''
    Process and store the metabolomics pool data from an uploaded file.
    This callback function takes the contents and filename of an uploaded file, processes the data 
    using the `process_pool_data` function, and then stores the processed data in JSON format in a Dash Store component 
    for later use in the application.

    Parameters:
    ----------
    contents : str
        The content of the uploaded file, encoded as a base64 string.
    filename : str
        The name of the uploaded file.

    Returns:
    -------
    str
        A JSON-formatted string representing the processed pool data, if the uploaded file contains data; 
        returns None if the file is empty or not properly uploaded.
    '''
    
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
    '''
    Process and store the metabolomics isotopic data from an uploaded file.
    This callback function takes the contents and filename of an uploaded file and 
    previously stored pool data as inputs. It processes the isotopic data using the `process_iso_data` function and 
    stores the processed data in JSON format in a Dash Store component for later use in the application.

    Parameters:
    ----------
    contents : str
        The content of the uploaded file, encoded as a base64 string.
    stored_pool_data : str
        JSON-formatted string of the previously stored pool data.
    filename : str
        The name of the uploaded file.

    Returns:
    -------
    str
        A JSON-formatted string representing the processed isotopic data, if the uploaded file and stored pool data are valid; 
        returns None if either the file is empty, not properly uploaded, or the pool data is not available.
    '''
    
    # Check if the uploaded file and stored pool data are present
    if contents and stored_pool_data:
        # If both are present, process the isotopic data and return the JSON representation
        return process_iso_data(contents, filename, stored_pool_data)
    
    # If either the uploaded file or stored pool data is missing, return None
    return None


@app.callback(
    Output('store-data-lingress', 'data'),
    [
    Input('upload-data', 'contents'),
    Input('store-data-pool', 'data')
],  
    State('upload-data', 'filename')
)
def store_lingress_data(contents, stored_pool_data, filename):
    '''
    Process and store external variable data for linear regression with metabolomics.
    This callback function takes the contents and filename of an uploaded file and 
    previously stored pool data as inputs. It processes the external variable data using the `process_lingress_data` function and 
    stores the processed data in JSON format in a Dash Store component for later use in the application.

    Parameters:
    ----------
    contents : str
        The content of the uploaded file, encoded as a base64 string.
    stored_pool_data : str
        JSON-formatted string of the previously stored pool data.
    filename : str
        The name of the uploaded file.

    Returns:
    -------
    str
        A JSON-formatted string representing the processed external variable data for linear regression,
        if the uploaded file and stored pool data are valid; 
        returns None if either the file is empty, not properly uploaded, or the pool data is not available.
    '''
    
    # Check if the uploaded file and stored pool data are present
    if contents and stored_pool_data:
        # If both are present, process the external variable data and return the JSON representation
        return process_lingress_data(contents, filename, stored_pool_data)
    
    # If either the uploaded file or stored pool data is missing, return None
    return None


@app.callback(
[
    Output('upload-status-display', 'children'),
    Output('uploaded-filename-display', 'children')
],  
[
    Input('store-data-pool', 'data'),
    Input('store-data-iso', 'data'),
    Input('store-data-lingress', 'data'),
], 
    State('upload-data', 'filename')
)
def update_upload_status(stored_pool_data, stored_iso_data, stored_lingress_data, filename):
    '''
    Update and display the upload status and filename of uploaded files.
    This callback function uses the stored pool data, isotopologue data, and the filename of an uploaded file 
    to generate status messages about the upload process. It then prepares these messages and the filename 
    for display in the application's interface.

    Parameters:
    ----------
    stored_pool_data : str
        JSON-formatted string representing the stored metabolomics pool data.
    stored_iso_data : str
        JSON-formatted string representing the stored isotopologue data.
    stored_lingress_data : str
        JSON-formatted string representing the stored linear regression data.
    filename : str
        The name of the most recently uploaded file.

    Returns:
    -------
    tuple
        A tuple containing HTML components or strings, which are used to display the upload status and filename in the application.
    '''
    
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
        if stored_lingress_data is None:
            # Case: Both pool and isotopic data are uploaded but no linear regression data
            return html.Span('Pool and isotopologue data successfully uploaded', style={'color': 'green'}), filename_display
        else:
            # Case: Both pool and isotopic data are uploaded with linear regression data
            return html.Span('Pool, isotopologue and regression data successfully uploaded', style={'color': 'green'}), filename_display
    else:
        # Case: Unexpected error
        print("There was an unexpected error when updating filename status!")
        return 'Unexpected error', filename_display