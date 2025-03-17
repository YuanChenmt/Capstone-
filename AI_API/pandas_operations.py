import pandas as pd
import os
import json
import matplotlib.pyplot as plt
import seaborn as sns

# Store the current DataFrame
dataframe = None
file_path_global = None

current_directory = os.getcwd()

def load_csv(file_path):
    """ Load a CSV file """
    global dataframe
    global file_path_global
    if os.path.exists(file_path):
        dataframe = pd.read_csv(file_path)

        if ";" in dataframe.columns[0]: # check if the file is separated by `;`
            dataframe = pd.read_csv(file_path, sep=";")  # reread the file with `;` separator

        for col in dataframe.columns:
            dataframe[col] = pd.to_numeric(dataframe[col], errors="coerce")  
        
        dataframe = dataframe.apply(pd.to_numeric, errors="coerce")

    file_path_global = file_path

    return f"File '{file_path}' loaded successfully!"


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


def describe_data():
    """Returns a properly formatted and visually appealing description of the dataset."""
   
    if dataframe is None or dataframe.empty:
        return "No data loaded. Please load a CSV file first."

    df_description = dataframe.describe(include="all").fillna("N/A")

    # if len(dataframe.columns) == 1 and ";" in dataframe.columns[0] and file_path_global:
    #     df = pd.read_csv(file_path_global, sep=";")  
    #     df_description = df.describe(include="all").fillna("N/A")

    formatted_output = df_description.to_dict()
    df_table = df_description.reset_index()

    return formatted_output, df_table


def plot_covariance_heatmap(output_dir=current_directory, filename="covariance_heatmap.png"):
    """ Save a heatmap of the covariance matrix to an images folder """
    if dataframe is not None:
        # Create the output directory if it doesn't exist
        output_dir = os.path.join(output_dir, "images")
        os.makedirs(output_dir, exist_ok=True)
        
        # Compute the covariance matrix
        covariance_matrix = dataframe.cov()

        # Create the plot
        plt.figure(figsize=(10, 8))
        sns.heatmap(covariance_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
        plt.title("Covariance Matrix Heatmap")
        
        # Save the plot
        save_path = os.path.join(output_dir, filename)
        print("-------",save_path)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()
        
        return save_path
    return "Please load the data file first!"