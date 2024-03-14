# security.py
# Main upload troubleshooting functions for the uploaded file

import datetime
import base64
import io
import pandas as pd


def current_timestamp():
    """
    Gets the current timestamp for logging purposes.

    Returns:
        str: Current timestamp in 'YYYY-MM-DD HH:MM:SS' format.
    """
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')


def decode_contents(contents):
    """
    Decodes the uploaded file content encoded in base64.

    Parameters:
        contents (str): The content of the uploaded file as a string in base64 format.

    Returns:
        bytes: Decoded content as bytes.
    """
    try:
        content_type, content_string = contents.split(',')
        decoded = base64.b64decode(content_string)
    except:
        error_message = "Error with decoding contents."
        print(current_timestamp(), error_message)
        raise ValueError(error_message)
        
    return decoded


def read_excel_file(decoded_content, required_sheet):
    """
    Reads the specified sheet from a decoded Excel file into a DataFrame.

    Parameters:
        decoded_content (bytes): The decoded content of an Excel file.
        required_sheet (str): The name of the sheet to be extracted from the Excel file.

    Returns:
        pd.DataFrame: Data from the required sheet as a pandas DataFrame.
    
    Raises:
        ValueError: If the required sheet is not present in the Excel file.
    """
    try:
        xls = pd.ExcelFile(io.BytesIO(decoded_content))
    except:
        error_message = "Error with reading the uploaded file."
        print(current_timestamp(), error_message)
        raise ValueError(error_message)
        
    if required_sheet not in xls.sheet_names:
        error_message = f"\nNo '{required_sheet}' sheet found in the uploaded file."
        print(current_timestamp(), error_message)
        raise ValueError(error_message)
    
    return pd.read_excel(xls, sheet_name=required_sheet)


def validate_column_names(df, compound_column_name):
    """
    Validates the expected name of the first column in the DataFrame.

    Parameters:
        df (pd.DataFrame): DataFrame with data to be validated.
        compound_column_name (str): The expected name of the first column in the DataFrame.

    Returns:
        pd.DataFrame: DataFrame with validated column names.

    Raises:
        ValueError: If the first column does not match the expected name.
    """
    if df.columns[0] != compound_column_name:
        error_message = f"The first column should be named '{compound_column_name}'."
        print(current_timestamp(), error_message)
        raise ValueError(error_message)
    return df


def clean_compound_column(df, metabolite_name_column_name="Compound"):
    """
    Cleans up the 'Compound' column in the DataFrame by stripping leading and trailing whitespace.

    Parameters:
        df (pd.DataFrame): DataFrame with the 'Compound' column to clean.
        metabolite_name_column_name (str): The name of the 'Compound' column.

    Returns:
        pd.DataFrame: DataFrame with the cleaned 'Compound' column.
    """
    if metabolite_name_column_name in df.columns:
        df[metabolite_name_column_name] = df[metabolite_name_column_name].str.strip()
    else:
        error_message = f"'{metabolite_name_column_name}' column not found in the DataFrame."
        print(current_timestamp(), error_message)
        raise ValueError(error_message)
    return df


def clean_column_headers(df):
    """
    Cleans up the DataFrame column headers by stripping whitespace and removing unwanted characters.

    Parameters:
        df (pd.DataFrame): DataFrame with column headers to clean.

    Returns:
        pd.DataFrame: DataFrame with cleaned column headers.

    Raises:
        ValueError: If column names contain invalid characters such as quotes.
    """
    df.columns = df.columns.str.replace(r'\s+', '', regex=True).str.strip()
    invalid_chars = ["'", '"', '\"']
    for char in invalid_chars:
        if df.columns.str.contains(char).any():
            error_message = f"Sample names should not have '{char}' characters."
            print(current_timestamp(), error_message)
            raise ValueError(error_message)
    return df


def process_pool_data(contents, filename, compound_column_name="Compound"):
    """
    Processes pool data from an uploaded Excel file. This function ensures the file contains the expected 
    sheet and columns, and that the data conforms to expected types and structures.

    Parameters:
        contents (str): Content of the uploaded file in base64 format.
        filename (str): Original name of the uploaded file for reference.
        compound_column_name (str): Name of the column to check for in the pool data.

    Returns:
        str: A JSON string representing the processed DataFrame if all validation checks pass.
    """
    decoded_content = decode_contents(contents)
    df_pool = read_excel_file(decoded_content, 'PoolAfterDF')
    df_pool = validate_column_names(df_pool, compound_column_name)
    df_pool = clean_column_headers(df_pool)
    df_pool = clean_compound_column(df_pool, compound_column_name)
    

    return df_pool.to_json(date_format='iso', orient='split')


def process_iso_data(contents, filename, stored_pool_data, compound_column_name="Compound"):
    """
    Processes isotopic data from an uploaded Excel file against previously stored pool data. This function ensures
    consistency and correctness of the isotopic data according to the pool data format and columns.

    Parameters:
        contents (str): Content of the uploaded file in base64 format.
        filename (str): Original name of the uploaded file for reference.
        stored_pool_data (str): A JSON string representing previously stored pool data.
        compound_column_name (str): Name of the column to check for in the isotopic data.

    Returns:
        str: A JSON string representing the processed isotopic DataFrame if all validation checks pass, or None if 'Normalized' sheet is not present.
    """
    
    decoded_content = decode_contents(contents)

    try:
        df_iso = read_excel_file(decoded_content, 'Normalized')
    except ValueError:
        # If 'Normalized' sheet is not found in the Excel file, return None
        return None

    df_iso = validate_column_names(df_iso, compound_column_name)
    df_iso = clean_column_headers(df_iso)
    df_iso = clean_compound_column(df_iso, compound_column_name)
    
    # Check if 'C_Label' column exists and all its values are 0 or NaN
    if 'C_Label' in df_iso.columns:
        if df_iso['C_Label'].isna().all() or (df_iso['C_Label'] == 0).all():
            return None

        else:
            return df_iso.to_json(date_format='iso', orient='split')
        
    else:
        return None
    
    
def process_lingress_data(contents, filename, stored_pool_data, variable_column_name="Variable"):
    """
    Processes external variable data from an uploaded Excel file against previously stored pool data to see if it is viable. 
    This function ensures consistency and correctness of the external variable data according to the pool data format and columns
    that could be used for linear regression external variable correlation to .

    Parameters:
        contents (str): Content of the uploaded file in base64 format.
        filename (str): Original name of the uploaded file for reference.
        stored_pool_data (str): A JSON string representing previously stored pool data.
        compound_column_name (str): Name of the column to check for in the isotopic data.

    Returns:
        str: A JSON string representing the processed isotopic DataFrame if all validation checks pass, or None if 'Normalized' sheet is not present.
    """
    
    decoded_content = decode_contents(contents)
    
    try:
        df_pool = read_excel_file(decoded_content, 'PoolAfterDF')
    except ValueError:
        # If 'PoolAfterDF' sheet is not found in the Excel file, return None
        # No pool data found in the uploaded sheet
        return None

    try:
        df_lingress = read_excel_file(decoded_content, 'Lingress')
    except ValueError:
        # If 'Lingress' sheet is not found in the Excel file, return None
        return None
    
    df_pool = clean_column_headers(df_pool)
    df_lingress = clean_column_headers(df_lingress)
    
    # Exclude the first column and get the remaining column names for both DataFrames
    pool_columns = list(df_pool.columns[1:])
    lingress_columns = list(df_lingress.columns[1:])

    # Compare the sets of column names
    if pool_columns == lingress_columns:
        return df_lingress.to_json(date_format='iso', orient='split')
        
    else:
        return None
    
    
    
    