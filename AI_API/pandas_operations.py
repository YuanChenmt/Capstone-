import pandas as pd
import os

# Store the current DataFrame
dataframe = None

def load_csv(file_path):
    """ Load a CSV file """
    global dataframe
    if os.path.exists(file_path):
        dataframe = pd.read_csv(file_path)
        return f"File {file_path} loaded successfully!"
    return "File does not exist, please check the path!"

def list_columns():
    """ Display the column names of the dataset """
    if dataframe is not None:
        return list(dataframe.columns)
    return "Please load the data file first!"

def summarize_top_rows(n=5):
    """ Get the top n rows of the data """
    if dataframe is not None:
        return dataframe.head(n).to_dict()
    return "Please load the data file first!"

def delete_column(column_name):
    """ Delete a specific column """
    global dataframe
    if dataframe is not None:
        if column_name in dataframe.columns:
            dataframe.drop(columns=[column_name], inplace=True)
            return f"Column '{column_name}' has been deleted."
        return f"Column '{column_name}' does not exist!"
    return "Please load the data file first!"
