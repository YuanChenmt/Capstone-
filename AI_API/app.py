import gradio as gr
import os
import dotenv
dotenv.load_dotenv()
import openai   
import json
import pandas as pd
from openai.types import FunctionDefinition  # Using OpenAI SDK's FunctionDefinition
from pandas_operations import load_csv, list_columns, summarize_top_rows, delete_column, describe_data, plot_covariance_heatmap, plot_feature_boxplots, get_dataframe_sample

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
        },
        {
            'name':"plot_feature_boxplots",
            'description':"Plot the feature boxplots.",
            'parameters':{}
        },
        {
            'name': "get_dataframe_advice",
            'description': "Get a small sample of the dataframe to help suggest operations.",
            'parameters': {"type": "object", "properties": {"n": {"type": "integer"}, "max_cols": {"type": "integer"}}}
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
            message,image_path = plot_covariance_heatmap()
            return message, image_path, None   
        elif function_name == "plot_feature_boxplots":
            message,image_path = plot_feature_boxplots()
            return message, image_path, None        
        elif function_name == "get_dataframe_advice":
            sample_json = get_dataframe_sample(arguments.get("n", 5), arguments.get("max_cols", 5))
            
            prompt = f"""
            Given this small sample of the dataset:
            {sample_json}
            With user question: {user_input}

            Provide responses in pure text.
            """

            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7
            )

            return response.choices[0].message.content, None, None

    return message.content, None, None  # Return AI's normal response

# Gradio interface
def chatbot_ui(user_input, api_key=os.getenv("OPENAI_API_KEY")):
    return call_openai_with_functions(user_input, api_key=os.getenv("OPENAI_API_KEY"))

# Create a Gradio interface
iface = gr.Interface(
    fn=chatbot_ui,
    inputs=[
        gr.Textbox(label="Enter Command", placeholder="Type your command here..."),
        gr.Textbox(label="API Key (Optional)", placeholder="Enter OpenAI API Key"),
    ],
    outputs=[
        gr.Markdown(label="Response"),
        gr.Image(label="Generated Plot"),
        gr.Dataframe(label="Table Output"),
    ],
    title="AI-Powered Data Analysis",
    description="Chat with OpenAI to analyze your dataset!"
)


iface.launch(server_name="0.0.0.0", server_port=7860)
