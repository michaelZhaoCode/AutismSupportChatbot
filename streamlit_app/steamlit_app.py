import streamlit as st
import streamlit.components.v1 as components
import textwrap
import time
import geocoder
import requests
import json

DEFAULT_NAME = "User"
DEFAULT_TYPE = "Adult"
DEFAULT_LOCATION = ""

USER_IMAGE = "user.png"
BOT_IMAGE = "chatbot.png"
LOADING_IMAGE = "loading.gif"

URL = "http://127.0.0.1:5000"

LOADING_DELAY = 0

SCRIPTED_RESPONSES = [
]


def request_api(message: str, location="") -> str:
    """
    Simulates sending an API request to a chatbot.
    For now, returns a constant response.
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
            # Print the JSON response from the server
            response_data = response.json()

            # Access and print the specific part of the response, i.e., the response from the chat function
            print('Response from server:', response_data['response'])
            return response_data['response']
        else:
            # Print the error
            print('Failed to get a valid response:', response.status_code, response.text)
            return "Error"


def format_message(role: str, message: str) -> str:
    """
    Returns an HTML-formatted string for the given message.
    Each message is wrapped in a full-width container.
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

    # Combine the chat container and auto-scroll script into a single HTML block.
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
          border: 2px solid #333;          /* Dark grey border */
          border-radius: 10px;              /* Rounded border */
          padding: 10px;
          height: 400px;
          overflow-y: auto;
          margin-bottom: 20px;
        }}
        /* WebKit scrollbar styling (if needed) */
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
        // Auto-scroll to the bottom of the chat container.
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

    # Custom CSS to override the default red focus border on the input element.
    st.markdown("""
    <style>
    /* Target the input container when it has focus (via its child element) */
    div[data-baseweb="input"]:focus-within {
        border-color: #ccc !important;
        box-shadow: none !important;
    }
    /* Also target the input itself on focus */
    div[data-baseweb="input"] input:focus, div[data-baseweb="input"] textarea:focus {
        outline: none !important;
        box-shadow: none !important;
        border-color: #ccc !important;
    }
    </style>
    """, unsafe_allow_html=True)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []

    # Create a placeholder for the chat history.
    chat_placeholder = st.empty()

    # Create the input form below the chat history.
    with st.form(key="chat_form", clear_on_submit=True):
        user_message = st.text_input("Enter your message:")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_message:
        st.session_state["chat_history"].append(("user", user_message))
        response = request_api(user_message)
        st.session_state["chat_history"].append(("bot", response))

    chat_history_html = render_chat_history(st.session_state["chat_history"])

    with chat_placeholder:
        components.html(chat_history_html, height=440)


if __name__ == "__main__":
    main()
