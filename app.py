import gradio as gr
from agent.me import Me

WELCOME_MESSAGE = """👋 Hi! I'm Muhammad Ibrahim's AI assistant.

I can help you learn about his professional background, skills, and experience. Feel free to ask me anything about:
- His technical expertise 
- Skills in front-end development and AI integration

What would you like to know?
"""

def chat(message, history):
    return me.chat(message, history)

if __name__ == "__main__":
    me = Me()

    with gr.Blocks() as demo:
        chatbot = gr.Chatbot(
            value=[
                {
                    "role": "assistant",
                    "content": WELCOME_MESSAGE
                }
            ],
            label="Chatbot"
        )

        gr.ChatInterface(
            fn=chat,
            chatbot=chatbot,
            title="Muhammad Ibrahim - Career Assistant",
        )

    demo.launch()

    