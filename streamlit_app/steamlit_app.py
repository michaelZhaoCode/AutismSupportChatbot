import streamlit as st
import streamlit.components.v1 as components
import textwrap
import time
import geocoder
import requests
import json
import base64
import os

DEFAULT_NAME = "User"
DEFAULT_TYPE = "Adult"
DEFAULT_LOCATION = ""

USER_IMAGE = "user.png"
BOT_IMAGE = "chatbot.png"
LOADING_IMAGE = "loading.gif"

URL = "http://127.0.0.1:5000"

LOADING_DELAY = 0

SCRIPTED_RESPONSES = [
    "Hi"
]


def get_base64_image(image_path):
    """Return base64 encoded image if exists, else None."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            data = base64.b64encode(img_file.read()).decode()
            return data
    else:
        return None


def request_api(message: str, location="") -> str:
    """
    Sends an API request to a chatbot.
    """
    if SCRIPTED_RESPONSES:
        time.sleep(2)
        return SCRIPTED_RESPONSES.pop(0)
    else:
        url = f'{URL}/generate'
        if location == "":
            location = geocoder.ip("me").latlng
        data = {
            'username': DEFAULT_NAME,
            'message': message,
            'usertype': DEFAULT_TYPE,
            'location': location,
            'region_id': -1
        }
        json_data = json.dumps(data)
        try:
            response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
        except requests.exceptions.ConnectionError:
            return "Error, no connection"
        if response.status_code == 200:
            response_data = response.json()
            print('Response from server:', response_data['response'])
            return response_data['response']
        else:
            print('Failed to get a valid response:', response.status_code, response.text)
            return "Error"


def format_message(role: str, message: str) -> str:
    """
    Returns an HTML-formatted string for the given message.
    """
    if role == "user":
        return f"""
<div style="width: 100%;">
  <div style="background-color: #0000FF; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: right; max-width: 60%; float: right;">
    <strong>You:</strong> {message}
  </div>
  <div style="clear: both;"></div>
</div>
"""
    else:
        return f"""
<div style="width: 100%;">
  <div style="background-color: #444444; color: white; padding: 10px; border-radius: 10px; margin: 5px 0; text-align: left; max-width: 60%; float: left;">
    <strong>Bot:</strong> {message}
  </div>
  <div style="clear: both;"></div>
</div>
"""


def render_chat_history(chat_history):
    """Builds an HTML block for the chat history with auto-scroll."""
    chat_history_content = ""
    for role, message in chat_history:
        chat_history_content += format_message(role, message)

    chat_history_html = textwrap.dedent(f"""\
    <html>
    <head>
      <style>
        body {{
          font-family: sans-serif;
          margin: 0;
          padding: 0;
        }}
        .chat-container {{
          border: 2px solid #333;
          border-radius: 10px;
          padding: 10px;
          height: 400px;
          overflow-y: auto;
          margin-bottom: 20px;
        }}
        /* WebKit scrollbar styling */
        .chat-container::-webkit-scrollbar {{
          width: 10px;
        }}
        .chat-container::-webkit-scrollbar-track {{
          background: #f1f1f1;
          border-radius: 10px;
        }}
        .chat-container::-webkit-scrollbar-thumb {{
          background: #888;
          border-radius: 10px;
        }}
        .chat-container::-webkit-scrollbar-thumb:hover {{
          background: #555;
        }}
        /* Firefox scrollbar styling */
        .chat-container {{
          scrollbar-width: thin;
          scrollbar-color: #888 #f1f1f1;
        }}
      </style>
    </head>
    <body>
      <div id="chat-history" class="chat-container">
        {chat_history_content}
        <div style="clear: both;"></div>
      </div>
      <script>
        var chatHistory = document.getElementById("chat-history");
        if(chatHistory) {{
          chatHistory.scrollTop = chatHistory.scrollHeight;
        }}
      </script>
    </body>
    </html>
    """)
    return chat_history_html


def main():
    st.title("Chatbot App")

    st.markdown("""
    <style>
    /* Override default red focus border on input */
    div[data-baseweb="input"]:focus-within {
        border-color: #ccc !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"] input:focus, div[data-baseweb="input"] textarea:focus {
        outline: none !important;
        box-shadow: none !important;
        border-color: #ccc !important;
    }
    </style>
    """, unsafe_allow_html=True)

    base64_image = get_base64_image(LOADING_IMAGE)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    chat_placeholder = st.empty()

    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input("Enter your message:")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_message:
        # Append user's message.
        st.session_state["chat_history"].append(("user", user_message))
        # Append a temporary loading message.
        loading_message = f'<img src="data:image/gif;base64,{base64_image}" alt="loading" style="width:50px;height:50px;">'
        st.session_state["chat_history"].append(("bot", loading_message))
        # Immediately update the chat display.
        chat_history_html = render_chat_history(st.session_state["chat_history"])
        with chat_placeholder:
            components.html(chat_history_html, height=440)
        # Display a spinner while waiting for the API response.
        with st.spinner("Waiting for response..."):
            response = request_api(user_message)
        # Replace the loading message with the actual response.
        st.session_state["chat_history"][-1] = ("bot", response)

    chat_history_html = render_chat_history(st.session_state["chat_history"])
    with chat_placeholder:
        components.html(chat_history_html, height=440)


if __name__ == "__main__":
    main()
