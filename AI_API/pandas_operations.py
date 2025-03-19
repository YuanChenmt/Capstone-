import pandas as pd
import os
import dotenv
import json
import matplotlib.pyplot as plt
import seaborn as sns
import boto3
from io import StringIO
from botocore.exceptions import NoCredentialsError

dotenv.load_dotenv()
# Store the current DataFrame
dataframe = None
file_path_global = None

current_directory = os.getcwd()
current_directory = os.path.join(current_directory, "images")


AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_REGION")
S3_BUCKET = os.getenv("S3_BUCKET_NAME")
S3_KEY=None


s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY,
    aws_secret_access_key=AWS_SECRET_KEY,
    region_name=AWS_REGION
)

def load_csv_from_s3(s3_key):
    """ Load a CSV file from an S3 bucket """
    global dataframe
    global file_path_global

    try:
        #get object from s3
        obj = s3_client.get_object(Bucket=S3_BUCKET, Key=s3_key)
        data = obj["Body"].read().decode("utf-8")  # decode the bytes to string

        # try to load the data as a CSV file
        dataframe = pd.read_csv(StringIO(data))

        # when the file is separated by `;`
        if ";" in dataframe.columns[0]:  
            dataframe = pd.read_csv(StringIO(data), sep=";")  

        dataframe = dataframe.apply(pd.to_numeric, errors="coerce")

        # keep track of the file path
        file_path_global = f"s3://{S3_BUCKET}/{s3_key}"

        return f"File '{s3_key}' loaded successfully from S3!"
    
    except Exception as e:
        return f"Error loading file from S3: {str(e)}"

def delete_s3_file():
    """ Delete a file from an S3 bucket """
    try:
        s3_client.delete_object(Bucket=S3_BUCKET, Key=S3_KEY)
        return f"S3 file '{S3_KEY}' deleted successfully."
    except Exception as e:
        return f"Error deleting file from S3: {str(e)}"

def upload_csv_to_s3(file_path, bucket_name, s3_key):
    """ Upload a file to an S3 bucket"""
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_REGION"),
    )

    try:
        s3.upload_file(file_path, bucket_name, s3_key)
        file_url = f"https://{bucket_name}.s3.{os.getenv('AWS_REGION')}.amazonaws.com/{s3_key}"
        return f"File uploaded successfully: [Download link]({file_url})"
    except NoCredentialsError:
        return "AWS credentials not found. Please set them as environment variables."
    except Exception as e:
        return f"Error uploading file: {str(e)}"


def upload_and_load_csv(file_path, s3_key):
    """ Upload a CSV file to S3 and load it"""
    global S3_KEY 
    if S3_KEY is not None:
        delete_s3_file()
    S3_KEY = s3_key
    bucket_name = os.getenv("S3_BUCKET_NAME")
    upload_msg = upload_csv_to_s3(file_path, bucket_name, s3_key)
    if "successfully" in upload_msg:
        return load_csv_from_s3(s3_key)
    return upload_msg


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
        return "No data loaded. Please load a CSV file first.", None, None

    df_description = dataframe.describe(include="all").fillna("N/A")

    # if len(dataframe.columns) == 1 and ";" in dataframe.columns[0] and file_path_global:
    #     df = pd.read_csv(file_path_global, sep=";")  
    #     df_description = df.describe(include="all").fillna("N/A")

    formatted_output = df_description.to_dict()
    df_table = df_description.reset_index()

    return  "Done!",formatted_output, df_table


def plot_covariance_heatmap(output_dir=current_directory, filename="covariance_heatmap.png"):
    """ Save a heatmap of the covariance matrix to an images folder """
    if dataframe is not None:
        # Create the output directory if it doesn't exist
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
        
        return "Covariance Heatmap done!", save_path
    return "Please load the data file first!", None


def plot_feature_boxplots(output_dir=current_directory, filename="feature_boxplots.png"):
    """ Generate box plots for all numerical features and save the figure """
    
    if dataframe is not None:

        numeric_df = dataframe.select_dtypes(include=["number"])

        if numeric_df.empty:
            return "Error: No numeric features available for box plot!", None
        
        os.makedirs(output_dir, exist_ok=True)

        plt.figure(figsize=(12, 6)) 
        sns.boxplot(data=numeric_df)
        plt.xticks(rotation=45)  # rotate x-axis labels for better visibility
        plt.title("Feature Box Plots")

        save_path = os.path.join(output_dir, filename)
        plt.savefig(save_path, dpi=300, bbox_inches="tight")
        plt.close()

        return "boxplots done!", save_path

    return "Error: No data loaded. Please load a CSV file first.", None


def get_dataframe_sample(n=5, max_cols=5):
    """ Return a small sample of the dataframe to be included in OpenAI input """
    
    if dataframe is None or dataframe.empty:
        return "No data loaded. Please load a CSV file first."
    max_cols = min(max_cols, len(dataframe.columns))
    sample_df = dataframe.iloc[:n, :max_cols]

    return json.dumps(sample_df.to_dict(), indent=4)
