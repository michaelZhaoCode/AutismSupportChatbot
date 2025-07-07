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
]


def get_base64_image(image_path):
    """Return base64 encoded image if exists, else None."""
    if os.path.exists(image_path):
        with open(image_path, "rb") as img_file:
            data = base64.b64encode(img_file.read()).decode()
            return data
    else:
        return None


def embed_leaflet_map_html(
    coordinates: list[tuple[float, float]],
    width: str = "100%",
    height: str = "400px"
) -> str:
    """
    Returns an HTML string to embed a Leaflet.js map with multiple markers and auto-fit bounds.
    """
    if not coordinates:
        raise ValueError("At least one coordinate must be provided.")

    # JavaScript array for LatLngBounds
    latlng_array = ",\n".join(f"[{lat}, {lon}]" for lat, lon in coordinates)

    # Marker creation
    markers_js = "\n".join(
        f"L.marker([{lat}, {lon}]).addTo(map);" for lat, lon in coordinates
    )

    return f"""
<link
    rel="stylesheet"
    href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
/>
<script
    src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
></script>

    <div id="map" style="height:{height}; width:{width}; border-radius:10px;"></div>
    <script>
        var map = L.map('map');
        L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
            maxZoom: 19,
            attribution: '© OpenStreetMap contributors'
        }}).addTo(map);

        var markers = [
            {latlng_array}
        ];
        var bounds = L.latLngBounds(markers);
        map.fitBounds(bounds);

        {markers_js}
    </script>
    """


def request_api(message: str, username: str, user_type: str, location: str, region_id: int) -> dict:
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
            'username': username,
            'message': message,
            'usertype': user_type,
            'location': location,
            'region_id': region_id
        }
        json_data = json.dumps(data)
        try:
            print(f"[DEBUG] Sending API request to {url} with data: {json_data}")
            response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
        except requests.exceptions.ConnectionError:
            return {"response": "Error, no connection"}
        if response.status_code == 200:
            response_data = response.json()
            print('Response from server:', response_data['response'])
            return response_data
        else:
            print('Failed to get a valid response:', response.status_code, response.text)
            return {"response": "Error"}


def format_message(role: str, message: str) -> str:
    """
    Returns an HTML-formatted string for the given message, preserving newlines
    and allowing raw HTML (e.g., loading GIF).
    """
    # format new lines
    msg_html = message.replace("\n", "<br>")

    bubble_style = (
        "background-color: #0000FF; color: white; text-align: right; float: right;"
        if role == "user" else
        "background-color: #444444; color: white; text-align: left; float: left;"
    )
    label = "You:" if role == "user" else "Bot:"

    return f"""
<div style="width: 100%;">
  <div style="{bubble_style} padding: 10px; border-radius: 10px; margin: 5px 0; max-width: 80%;">
    <strong>{label}</strong> {msg_html}
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


def retrieve_regions_and_save():
    url = f'{URL}/retrieve_regions'
    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        print("Error, no connection")
        return
    if response.status_code == 200:
        response_data = response.json()
        with open('regions_data.json', 'w') as json_file:
            json.dump(response_data['response'], json_file, indent=4)
        print("Regions data successfully saved to regions_data.json")
    else:
        print('Failed to retrieve regions:', response.status_code, response.text)


def load_regions_data() -> list:
    try:
        with open('regions_data.json', 'r') as json_file:
            regions_data = json.load(json_file)
        return regions_data
    except FileNotFoundError:
        print("No regions data found. Please make sure to retrieve and save the data first.")
        return []


# Callback function for automatic region selection
def update_region():
    selected_option = st.session_state.get("region_dropdown")
    if selected_option == "Choose Next Bound":
        return
    selected_region = next((region for region in st.session_state["current_options"]
                            if region["region_name"] == selected_option), None)
    if selected_region:
        st.session_state["region_path"].append(selected_region)
        st.session_state["current_options"] = selected_region.get("subregions", [])


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

    # Persistent fields for username, user type, and location.
    username_input = st.text_input("Enter your username:", key="username_field",
                                   value=st.session_state.get("username_field", DEFAULT_NAME))
    user_type_input = st.text_input("Enter your user type:", key="user_type_field",
                                    value=st.session_state.get("user_type_field", DEFAULT_TYPE))
    location_input = st.text_input("Enter your location:", key="location_field",
                                   value=st.session_state.get("location_field", DEFAULT_LOCATION))

    # ---------------------------
    # Region Filter Widget
    # ---------------------------
    if "region_path" not in st.session_state:
        st.session_state["region_path"] = []  # List to store selected region objects.
    if "current_options" not in st.session_state:
        st.session_state["current_options"] = load_regions_data()  # Start with top-level regions.

    if st.session_state["region_path"]:
        region_path_str = " > ".join([region["region_name"] for region in st.session_state["region_path"]])
    else:
        region_path_str = "No Region Bound"
    st.text_input("Current Region", value=region_path_str, disabled=True)

    options = ["Choose Next Bound"] + (
        [region["region_name"] for region in st.session_state["current_options"]]
        if st.session_state["current_options"] else []
    )
    if options:
        st.selectbox("Choose Next Bound", options, key="region_dropdown",
                     on_change=update_region, label_visibility="collapsed")
    else:
        st.write("No further regions available.")

    if st.button("Reset Region Selection"):
        st.session_state["region_path"] = []
        st.session_state["current_options"] = load_regions_data()
        st.rerun()

    if st.session_state["region_path"]:
        region_id = st.session_state["region_path"][-1]["region_id"]
    else:
        region_id = -1


    # ---------------------------
    # Chat Interface
    # ---------------------------
    base64_image = get_base64_image(LOADING_IMAGE)

    if "chat_history" not in st.session_state:
        st.session_state["chat_history"] = []
    if "created_map" not in st.session_state:
        st.session_state["created_map"] = False
    if "coords" not in st.session_state:
        st.session_state["coords"] = []

    chat_placeholder = st.empty()

    if st.session_state["created_map"]:
        # Render map separately
        map_html = embed_leaflet_map_html(st.session_state["coords"])
        components.html(map_html, height=450)


    # Separate form for the message field only; clear_on_submit clears just this field.
    with st.form(key="message_form", clear_on_submit=True):
        user_message = st.text_input("Enter your message:")
        submit_button = st.form_submit_button("Send")

    if submit_button and user_message:
        st.session_state["chat_history"].append(("user", user_message))
        loading_message = f'<img src="data:image/gif;base64,{base64_image}" alt="loading" style="width:50px;height:50px;">'
        st.session_state["chat_history"].append(("bot", loading_message))
        chat_history_html = render_chat_history(st.session_state["chat_history"])
        with chat_placeholder:
            components.html(chat_history_html, height=440)
        with st.spinner("Waiting for response..."):
            response = request_api(user_message, username_input, user_type_input, location_input, region_id)
            message = response["response"]
            if response["response_type"] == "service":
                st.session_state["coords"] = [(service["Latitude"], service["Longitude"]) for service in response["context"]["services"]]
                st.session_state["created_map"] = True
        st.session_state["chat_history"][-1] = ("bot", message)
        st.rerun()

    chat_history_html = render_chat_history(st.session_state["chat_history"])
    with chat_placeholder:
        components.html(chat_history_html, height=440)


if __name__ == "__main__":
    if "regions_data_loaded" not in st.session_state:
        retrieve_regions_and_save()
        st.session_state["regions_data_loaded"] = True
    main()

