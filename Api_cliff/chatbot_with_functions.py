import os, json
import openai
import pandas as pd
import requests

# Load API keys from environment (do not hardcode them)
openai.api_key = os.getenv("OPENAI_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")  # for weather API (e.g., OpenWeatherMap)

# Global variable to hold the DataFrame once loaded
df = None

# Define functions that the AI can call:

def load_data():
    """Load data from a sample CSV file into a DataFrame."""
    global df
    try:
        df = pd.read_csv("sample.csv")
        return f"✅ Data loaded. Rows: {len(df)}, Columns: {len(df.columns)}."
    except Exception as e:
        return f"⚠️ Failed to load data: {e}"

def list_columns():
    """List the column names of the DataFrame."""
    if df is None:
        return "⚠️ No data loaded. Use load_data() first."
    cols = df.columns.tolist()
    return f"Columns: {', '.join(cols)}"

def summarize_data():
    """Return summary statistics of the DataFrame."""
    if df is None:
        return "⚠️ No data loaded to summarize."
    # Use pandas describe to get summary; convert to plain text
    summary = df.describe(include='all').to_string()
    return f"Summary statistics:\n{summary}"

def delete_column(column_name: str):
    """Delete a specified column from the DataFrame."""
    global df
    if df is None:
        return "⚠️ No data loaded."
    if column_name in df.columns:
        df.drop(columns=[column_name], inplace=True)
        return f"✅ Column '{column_name}' deleted. Remaining columns: {', '.join(df.columns)}"
    else:
        return f"⚠️ Column '{column_name}' not found in data."

def get_weather(city: str):
    """Fetch current weather for the given city using a weather API."""
    if not weather_api_key:
        return "⚠️ Weather API key is not set."
    try:
        url = (f"http://api.openweathermap.org/data/2.5/weather?"
               f"q={city}&appid={weather_api_key}&units=metric")
        resp = requests.get(url)
        data = resp.json()
        if resp.status_code != 200:
            # If city not found or other error, OpenWeatherMap returns a message
            return f"⚠️ Weather API error: {data.get('message', 'Unable to fetch weather')}."
        # Parse relevant info from response
        temp = data["main"]["temp"]
        desc = data["weather"][0]["description"]
        return f"The current weather in {city} is {desc} with a temperature of {temp}°C."
    except Exception as e:
        return f"⚠️ Error fetching weather data: {e}"

# Describe the functions to the OpenAI API for function calling
functions_spec = [
    {
        "name": "load_data",
        "description": "Load a sample CSV file for data analysis.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "list_columns",
        "description": "List the column names of the loaded dataset.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "summarize_data",
        "description": "Provide summary statistics of the loaded dataset.",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    },
    {
        "name": "delete_column",
        "description": "Delete a column from the dataset.",
        "parameters": {
            "type": "object",
            "properties": {
                "column_name": {
                    "type": "string",
                    "description": "Name of the column to delete"
                }
            },
            "required": ["column_name"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get the current weather for a given city.",
        "parameters": {
            "type": "object",
            "properties": {
                "city": {
                    "type": "string",
                    "description": "City name (e.g. London) to get weather information for"
                }
            },
            "required": ["city"]
        }
    }
]

# Initialize conversation with a system prompt for context
messages = [
    {"role": "system", "content": "You are a smart assistant. You have tools to analyze a dataset and check weather information."}
]

print("Function-Calling Chatbot is ready! Type a message and press enter (or 'quit' to exit).")
while True:
    user_input = input("You: ")
    if user_input.lower() in {"quit", "exit"}:
        print("Exiting chat.")
        break

    # Add user message to conversation history
    messages.append({"role": "user", "content": user_input})

    try:
        # Send the conversation to OpenAI with function support
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0613",    # use model version that supports function calling
            messages=messages,
            functions=functions_spec,
            function_call="auto"           # let the model decide if a function is needed
        )
    except Exception as e:
        print(f"Error: {e}")
        messages.pop()  # remove the last user message on error
        continue

    assistant_msg = response["choices"][0]["message"]
    # Check if the model decided to call a function
    if assistant_msg.get("function_call"):
        func_name = assistant_msg["function_call"]["name"]
        arguments = assistant_msg["function_call"].get("arguments", "{}")
        args = json.loads(arguments)  # parse the arguments JSON string to dict

        # Execute the corresponding function in Python
        if func_name == "load_data":
            result = load_data()
        elif func_name == "list_columns":
            result = list_columns()
        elif func_name == "summarize_data":
            result = summarize_data()
        elif func_name == "delete_column":
            col = args.get("column_name")
            result = delete_column(col)
        elif func_name == "get_weather":
            city = args.get("city")
            result = get_weather(city)
        else:
            result = f"⚠️ Unknown function: {func_name}"

        # Add the function call and its result to the conversation history
        messages.append({
            "role": "assistant",
            "content": None,
            "function_call": assistant_msg["function_call"]  # record the function call request
        })
        messages.append({
            "role": "function",
            "name": func_name,
            "content": result  # the output from the function
        })

        # Call the API again, now including the function result, to get the final answer
        try:
            second_response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-0613",
                messages=messages
            )
        except Exception as e:
            print(f"Error during second call: {e}")
            # Remove function messages on error to avoid a broken state
            messages.pop(); messages.pop()
            continue

        final_answer = second_response["choices"][0]["message"]["content"]
        print(f"Assistant: {final_answer}")
        # Add the assistant's final answer to the history
        messages.append({"role": "assistant", "content": final_answer})
    else:
        # No function call, the assistant gave a direct answer
        answer = assistant_msg.get("content", "")
        print(f"Assistant: {answer}")
        messages.append({"role": "assistant", "content": answer})

