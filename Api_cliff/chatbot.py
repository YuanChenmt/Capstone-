import os
import openai

# Get your OpenAI API key from an environment variable for security.
openai.api_key = os.getenv("OPENAI_API_KEY")
if openai.api_key is None:
    openai.api_key = input("Enter your OpenAI API key: ").strip()

# Simple chat loop: read user input and get response from GPT-3.5-turbo
print("Chatbot is ready! Type a message and press enter (or 'quit' to exit).")
while True:
    user_input = input("You: ")
    if user_input.lower() in {"quit", "exit"}:
        print("Exiting chat.")
        break

    try:
        # Send the user message to the OpenAI ChatCompletion API
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": user_input}]
        )
        # Extract the assistant's reply
        assistant_reply = response["choices"][0]["message"]["content"]
        print(f"Assistant: {assistant_reply}")
    except Exception as e:
        print(f"Error: {e}")

