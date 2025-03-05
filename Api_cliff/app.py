import os
import openai
import gradio as gr
import pandas as pd
import json
import random

# --------------------
# 1. API Key Configuration
# --------------------
# Best practice: use environment variables for API keys to avoid hardcoding.
# Attempt to get the OpenAI API key from an environment variable.
openai.api_key = os.environ.get("OPENAI_API_KEY")
# If not provided via environment, the application will prompt for it through the Gradio UI.

# --------------------
# 2. Function Definitions (CSV handling & Weather data)
# --------------------
def analyze_csv(file_path: str, column: str = None) -> str:
    """
    Analyze a CSV file to provide summary statistics or specific column analysis.

    Args:
        file_path (str): Path to the CSV file.
        column (str, optional): Specific column to analyze. 
            - If provided and the column is numeric, returns the column's mean.
            - If provided and the column is non-numeric, returns the count of unique values (with examples).
            - If not provided, returns the shape (rows, columns) and column names of the CSV.
    Returns:
        str: A summary of the CSV or analysis of the specified column.
    """
    # Only allow CSV files for safety
    if not file_path.lower().endswith('.csv'):
        return "Error: Only CSV files are supported."
    # Check if the file exists to avoid FileNotFoundError
    if not os.path.exists(file_path):
        return f"Error: File '{file_path}' not found."
    try:
        # Read the CSV file into a DataFrame
        df = pd.read_csv(file_path)
    except Exception as e:
        # Handle errors in reading the CSV (e.g., file permissions, encoding issues)
        return f"Error reading CSV file: {e}"
    # If a specific column is requested, provide detail on that column
    if column:
        if column not in df.columns:
            return f"Error: Column '{column}' not found in the CSV."
        # If the column is numeric, calculate the mean as an example statistic
        if pd.api.types.is_numeric_dtype(df[column]):
            mean_val = df[column].mean(numeric_only=True)
            return f"The average of '{column}' is {mean_val:.2f}."
        else:
            # For non-numeric columns, return the number of unique values and example values
            unique_vals = df[column].dropna().unique()
            num_unique = len(unique_vals)
            # Show up to the first 5 unique values as examples
            sample_vals = [str(val) for val in unique_vals[:5]]
            examples = ", ".join(sample_vals)
            if num_unique > 5:
                examples += ", ... (and more)"
            return f"Column '{column}' has {num_unique} unique values. Examples: {examples}."
    else:
        # No specific column requested: provide a general summary of the CSV
        rows, cols = df.shape
        col_names = list(df.columns)
        return f"The CSV file has {rows} rows and {cols} columns. Column names: {', '.join(col_names)}."

def get_weather(location: str) -> str:
    """
    Get the current weather for a given location (dummy implementation).

    Args:
        location (str): City or location name.
    Returns:
        str: A description of the current weather at the location.
    """
    # Dummy weather data (for real data, integrate with a weather API e.g., OpenWeatherMap)
    conditions = ["sunny", "cloudy", "rainy", "windy", "stormy"]
    temperature = random.randint(-10, 35)  # temperature in °C
    condition = random.choice(conditions)
    return f"The weather in {location} is currently {condition} with a temperature of {temperature}°C."

# --------------------
# 3. OpenAI Chat and Function Calling Logic
# --------------------
# Define the functions metadata for the OpenAI API (to tell the model about available functions)
functions_spec = [
    {
        "name": "analyze_csv",
        "description": "Analyze a CSV file and provide summary or specific column statistics.",
        "parameters": {
            "type": "object",
            "properties": {
                "file_path": {"type": "string", "description": "Path to the CSV file to analyze."},
                "column": {"type": "string", "description": "Optional column name to analyze."}
            },
            "required": ["file_path"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get current weather information for a city or location.",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "Name of the city or location (e.g., 'London')."}
            },
            "required": ["location"]
        }
    }
]

# System message to prime the assistant with initial context or behavior
SYSTEM_MESSAGE = {
    "role": "system",
    "content": "You are a helpful assistant. You can analyze CSV files and retrieve weather information using provided functions."
}

def process_user_message(user_message: str, message_history: list):
    """
    Process a user message using the OpenAI API, handling function calls if the model requests them.

    Args:
        user_message (str): The user's input message.
        message_history (list): Conversation history (list of message dicts) including the system message and prior interactions.
    Returns:
        tuple: (assistant_response, updated_message_history)
            - assistant_response (str): The assistant's response text to display.
            - updated_message_history (list): The conversation history updated with the latest messages.
    """
    # Append the user's message to the conversation history
    message_history.append({"role": "user", "content": user_message})
    try:
        # Send the conversation and function definitions to the OpenAI API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # model supporting function calling
            messages=message_history,
            functions=functions_spec,
            function_call="auto"        # allow the model to decide if it should use a function
        )
    except Exception as e:
        # If the API call fails, remove the user message and return an error message
        message_history.pop()
        return f"Error: Failed to communicate with OpenAI API. ({e})", message_history

    # Get the assistant's message from the response
    assistant_message = response["choices"][0]["message"]

    # Check if the assistant decided to call a function
    if assistant_message.get("function_call"):
        # Extract the name and arguments of the function the model wants to call
        function_name = assistant_message["function_call"]["name"]
        args_str = assistant_message["function_call"].get("arguments", "")
        # Parse the arguments from JSON string to a Python dict
        try:
            function_args = json.loads(args_str) if args_str else {}
        except json.JSONDecodeError:
            function_args = {}

        # Call the corresponding Python function with the parsed arguments
        if function_name == "analyze_csv":
            function_result = analyze_csv(**function_args)
        elif function_name == "get_weather":
            function_result = get_weather(**function_args)
        else:
            function_result = f"Error: Function '{function_name}' is not available."

        # Append the assistant's function call request to the history
        message_history.append({
            "role": "assistant",
            "content": None,
            "function_call": {
                "name": function_name,
                "arguments": json.dumps(function_args)
            }
        })
        # Append the function's result as a message in the history (role "function")
        message_history.append({
            "role": "function",
            "name": function_name,
            "content": function_result
        })

        try:
            # Call the OpenAI API again, now with the function's result in the conversation, to get the final answer
            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=message_history,
                functions=functions_spec,
                function_call="auto"
            )
        except Exception as e:
            return f"Error: Failed to get response after function call. ({e})", message_history

        # Extract the final assistant message after function execution
        final_assistant_message = second_response["choices"][0]["message"]
        # Append the final assistant message to the history
        message_history.append(final_assistant_message)
        # Return the content of the final assistant message and the updated history
        return final_assistant_message.get("content", ""), message_history

    else:
        # If no function call was made, simply append the assistant's message to history and return it
        message_history.append(assistant_message)
        return assistant_message.get("content", ""), message_history

# --------------------
# 4. Gradio Interface Setup
# --------------------
# Build the Gradio interface for the chatbot
with gr.Blocks() as demo:
    gr.Markdown("## OpenAI Function-Calling Chatbot\nEnter your question, and the assistant may use tools (functions) to help answer it.")
    # Textbox for API key input (if not set via environment, user can input here)
    api_key_input = gr.Textbox(
        placeholder="OpenAI API Key (sk-...)",
        show_label=True,
        label="OpenAI API Key",
        type="password"
    )
    # Chatbot component to display the conversation
    chatbot = gr.Chatbot(label="Chatbot")
    # Textbox for the user's message
    user_input = gr.Textbox(placeholder="Type your message here and press Enter", show_label=False)
    # Buttons for sending the message and clearing the chat
    submit_btn = gr.Button("Send")
    clear_btn = gr.Button("Clear")
    # State to hold the conversation history for the model (includes system and all messages)
    chat_state = gr.State([SYSTEM_MESSAGE])
    # State to hold the chat history in (user, assistant) pairs for display
    chat_history = gr.State([])

    def send_message(user_message, api_key, history_state, history_pairs):
        """
        Handle the user submitting a message: update state, get model response, and update the chat history.
        """
        # Use the provided API key, if given (overrides the environment key for this session)
        if api_key:
            openai.api_key = api_key
        # If no API key is set, do not proceed (the user needs to input their API key)
        if not openai.api_key:
            # Return with no changes (user will be prompted to input an API key)
            return user_message, history_pairs, history_state, history_pairs
        # Retrieve the current conversation state (list of message dicts)
        messages = history_state
        # Process the user message through the OpenAI API and potentially a function call
        assistant_reply, updated_messages = process_user_message(user_message, messages)
        # Update the visible chat history with the new user question and assistant answer
        updated_pairs = history_pairs + [(user_message, assistant_reply)]
        # Return the updated components: clear the input box, update chat display, and update states
        return "", updated_pairs, updated_messages, updated_pairs

    def clear_conversation():
        """
        Clear the conversation history and reset the chat.
        """
        # Return empty chat, reset state to just the system message, and clear chat history pairs
        return [], [SYSTEM_MESSAGE], []

    # Set up the event handlers for sending a message and clearing the chat
    submit_btn.click(send_message, inputs=[user_input, api_key_input, chat_state, chat_history],
                     outputs=[user_input, chatbot, chat_state, chat_history])
    user_input.submit(send_message, inputs=[user_input, api_key_input, chat_state, chat_history],
                      outputs=[user_input, chatbot, chat_state, chat_history])
    clear_btn.click(clear_conversation, outputs=[chatbot, chat_state, chat_history])

# Launch the Gradio app if this script is run directly
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
    #demo.launch()

