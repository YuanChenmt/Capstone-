import gradio as gr
import os
import dotenv
dotenv.load_dotenv()
import openai   
import json
import pandas as pd
from openai.types import FunctionDefinition  # Using OpenAI SDK's FunctionDefinition
from pandas_operations import load_csv, list_columns, summarize_top_rows, delete_column, describe_data, plot_covariance_heatmap

# Call OpenAI API with function support
def call_openai_with_functions(user_input, api_key):
    """ Call OpenAI API with function support """
    client = openai.OpenAI(api_key=api_key)

    pd_functions = [
        {  
            'name':"load_csv",
            'description':"Load a CSV file.",
            'parameters':{"type": "object", "properties": {"file_path": {"type": "string"}}}
        },
        {
            'name':"list_columns",
            'description':"Get the column names of the CSV.",
            'parameters':{}
        },
        {
            'name':"summarize_top_rows",
            'description':"Get the top 5 rows of the dataset.",
            'parameters':{}
        },
        {
            'name':"delete_column",
            'description':"Delete a column.",
            'parameters':{"type": "object", "properties": {"column_name": {"type": "string"}}}
        },
        {
            'name':"describe_data",
            'description':"Describe the data.",
            'parameters':{}
        },
        {
            'name':"plot_covariance_heatmap",
            'description':"Plot the covariance heatmap.",
            'parameters':{}
        }
    ]

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": user_input}],
        functions=pd_functions,   # type: ignore , DK how to fix this
        function_call="auto"
    )

    # Correctly parse if function_call exists
    message = response.choices[0].message
    if message.function_call:  # Directly check if function_call exists
        function_name = message.function_call.name
        arguments = json.loads(message.function_call.arguments)
        # return message # test code, test the response when you call a functions.
        if function_name == "load_csv":
            return load_csv(arguments["file_path"]), None, None
        elif function_name == "list_columns":
            return list_columns(), None, None
        elif function_name == "summarize_top_rows":
            return summarize_top_rows(), None, None
        elif function_name == "delete_column":
            return delete_column(arguments["column_name"]), None, None
        elif function_name == "describe_data":
            desc_result, df_table = describe_data()
            if df_table is not None:
                return None, None, df_table  
            else:
                return desc_result, None, None

        elif function_name == "plot_covariance_heatmap":
            image_path = plot_covariance_heatmap()
            return None, image_path, None   
    return message.content, None, None  # Return AI's normal response

# Gradio interface
def chatbot_ui(user_input, api_key=os.getenv("OPENAI_API_KEY")):
    return call_openai_with_functions(user_input, api_key=os.getenv("OPENAI_API_KEY"))

# Create a Gradio interface
iface = gr.Interface(
    fn=chatbot_ui,
    inputs=["text", "text"], 
    outputs=[
        "text",      # text
        "image",     # plot
        "dataframe"  # table
    ],
    title="OpenAI Chatbot + Pandas Operations",
    description="""Ask questions or use natural language to operate on Pandas!
    Supports text output, data visualization (image), and structured data (table).
    """
)

iface.launch(server_name="0.0.0.0", server_port=7860)
