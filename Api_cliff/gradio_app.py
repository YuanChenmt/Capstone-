# gradio_app.py
import gradio as gr
import openai

def gradio_chat(api_key, user_input):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",  # or "gpt-4-turbo"
        messages=[{"role": "user", "content": user_input}]
    )
    return response.choices[0].message["content"]

iface = gr.Interface(
    fn=gradio_chat,
    inputs=[
        gr.inputs.Textbox(label="OpenAI API Key", type="password"),
        gr.inputs.Textbox(label="Your Input")
    ],
    outputs="text",
    title="Simple Chatbot using OpenAI API",
    description="Enter your API key and a prompt to chat with the model."
)

if __name__ == "__main__":
    iface.launch()

