import time
import tkinter as tk
from tkinter import ttk
import threading
import requests
import json
import itertools
from PIL import Image, ImageTk  # Required for image processing
import pyttsx3

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


class ChatInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rudimentary Chat Interface")
        self.geometry("750x740")  # Set the window size

        # Container for Canvas and Scrollbar
        self.canvas_container = tk.Frame(self)
        self.canvas_container.pack(side="top", fill="both", expand=True)

        # Canvas for chat history with scrolling
        self.canvas = tk.Canvas(self.canvas_container, bg="white", height=400)
        self.scrollbar = ttk.Scrollbar(self.canvas_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # Frame that will contain chat messages
        self.chat_frame = tk.Frame(self.canvas, bg="white")
        self.canvas_window = self.canvas.create_window((0, 0), window=self.chat_frame, anchor="nw")

        # Method ensures that the canvas frame adjusts its size
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        self.chat_frame.bind("<Configure>", self._on_frame_configure)

        self.message_frames = []

        self.tts_buttons = []

        ##################

        # Frame for new text fields
        self.info_frame = ttk.Frame(self)
        self.info_frame.pack(padx=10, pady=10, fill=tk.X)

        # Username field
        self.username_label = ttk.Label(self.info_frame, text="Username:", font=("Helvetica", 14))
        self.username_label.grid(row=0, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(self.info_frame, font=("Helvetica", 14))
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        # Usertype field
        self.usertype_label = ttk.Label(self.info_frame, text="User type:", font=("Helvetica", 14))
        self.usertype_label.grid(row=1, column=0, padx=5, pady=5)
        self.usertype_entry = ttk.Entry(self.info_frame, font=("Helvetica", 14))
        self.usertype_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        # Location field
        self.location_label = ttk.Label(self.info_frame, text="Location:", font=("Helvetica", 14))
        self.location_label.grid(row=0, column=2, padx=5, pady=5)
        self.location_entry = ttk.Entry(self.info_frame, font=("Helvetica", 14))
        self.location_entry.grid(row=0, column=3, padx=5, pady=5, sticky="ew")

        ###### Add uneditable field, dropdown, and reset button ######

        # Load regions data
        self.regions_data = load_regions_data()

        # Internal variables
        self.region_id = -1
        self.current_region = None  # To keep track of the current region path

        # Variable to hold the uneditable field value
        self.region_label_var = tk.StringVar(value="No Region Bound")

        # Uneditable field
        self.region_label = ttk.Label(self.info_frame, textvariable=self.region_label_var, font=("Helvetica", 14),
                                      foreground="Black", anchor="w")  # Left-justified by anchor="w"
        self.region_label.grid(row=2, column=1, padx=5, pady=5, sticky="w")  # Left-justified by sticky="w"

        # Dropdown variable
        self.dropdown_var = tk.StringVar(value="Choose Next Bound")

        # Dropdown menu
        self.dropdown = ttk.OptionMenu(self.info_frame, self.dropdown_var, "Choose Next Bound", *[],
                                       command=self.on_dropdown_select)
        self.dropdown.grid(row=2, column=2, padx=5, pady=5, sticky="ew")  # Full width expansion

        # Set the font for dropdown's menu
        dropdown_menu = self.dropdown["menu"]
        dropdown_menu.config(font=("Helvetica", 14))  # Set font for dropdown menu items

        # Populate the initial dropdown options
        self.update_dropdown_options(self.regions_data)

        # Reset button
        self.reset_button = ttk.Button(self.info_frame, text="Reset", command=self.reset_region_selection,
                                       style="Custom.TButton")  # Assigning custom style to button
        self.reset_button.grid(row=2, column=3, padx=5, pady=5)

        # Define a style for the reset button if you're using ttk.
        style = ttk.Style()
        style.configure("Custom.TButton", font=("Helvetica", 14))  # Set font for reset button

        ###

        # Frame for entry box and send button
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(padx=10, pady=10, fill=tk.X)

        # Frame for entry box and send button
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.pack(padx=10, pady=10, fill=tk.X)

        # Send button defined to be a square
        self.button_height = 2  # Defined height for the button
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.on_send_button_click,
                                     font=("Helvetica", 14))
        self.send_button.grid(row=0, column=1, padx=5, pady=5)
        self.send_button.config(height=self.button_height * 2, width=self.button_height * 5)  # Makes the button square

        # Chatbox to write a message
        self.message_entry = tk.Text(self.entry_frame, height=5, wrap=tk.WORD, font=("Helvetica", 14), padx=10, pady=10)
        self.message_entry.grid(row=0, column=0, sticky="ew")
        self.message_entry.config(height=self.button_height * 2)

        # Configure grid weights
        self.entry_frame.columnconfigure(0, weight=1)  # Text entry takes maximum possible space
        self.entry_frame.columnconfigure(1, weight=0)  # Button size is fixed

    # Function to update dropdown options
    def update_dropdown_options(self, regions_list):
        # Clear current options
        menu = self.dropdown['menu']
        menu.delete(0, 'end')

        # Add default option
        menu.add_command(label="Choose Next Bound", command=lambda: self.dropdown_var.set("Choose Next Bound"))

        # Add new options
        for region in regions_list:
            menu.add_command(label=region['region_name'],
                             command=lambda value=region['region_name']: self.on_dropdown_select(value))

    # Function called when an option is selected from the dropdown
    def on_dropdown_select(self, selected_value):
        if selected_value == "Choose Next Bound":
            return

        # Find the selected region in the current list
        selected_region = self.find_region_by_name(selected_value,
                                                   self.regions_data if self.current_region is None else self.current_region.get(
                                                       'subregions', []))

        if selected_region:
            # Update the uneditable field
            self.region_label_var.set(selected_region['region_name'])

            # Update the internal region_id
            self.region_id = selected_region['region_id']

            # Reset the dropdown
            self.dropdown_var.set("Choose Next Bound")

            # Update current region
            self.current_region = selected_region

            # Update dropdown options with subregions
            if selected_region.get('subregions'):
                self.update_dropdown_options(selected_region['subregions'])
            else:
                # No more subregions, disable the dropdown
                menu = self.dropdown['menu']
                menu.delete(0, 'end')
                menu.add_command(label="No more subregions", command=lambda: None)
                self.dropdown_var.set("No more subregions")
        else:
            # Reset to initial state if selection is invalid
            self.reset_region_selection()

    # Helper function to find a region by name in a list
    def find_region_by_name(self, name, regions_list):
        for region in regions_list:
            if region['region_name'] == name:
                return region
        return None

    # Function to reset the region selection
    def reset_region_selection(self):
        self.region_label_var.set("No Region Bound")
        self.region_id = -1
        self.current_region = None
        self.dropdown_var.set("Choose Next Bound")
        self.update_dropdown_options(self.regions_data)

    def create_chatbox(self, message, image_path, side='left'):
        # Frame for the message
        message_frame = tk.Frame(self.chat_frame, bg="white")

        # Determine the correct side for the message frame within the chat frame
        if side == 'left':
            message_frame.pack(padx=10, pady=5, anchor='w')
            name_label = tk.Label(message_frame, text=self.username_entry.get().strip() or DEFAULT_NAME, bg="white",
                                  justify="center",
                                  font=("Helvetica", 12))
            name_label.pack(side='top', padx=10, pady=(5, 0), anchor="w")
        else:
            message_frame.pack(padx=10, pady=5, anchor='e')
            name_label = tk.Label(message_frame, text="Chatbot", bg="white", justify="center",
                                  font=("Helvetica", 12))
            name_label.pack(side='top', padx=10, pady=(5, 0), anchor="e")

        # Load and resize image
        image = Image.open(image_path)
        image = image.resize((50, 50), Image.Resampling.LANCZOS)  # Resize the image using the LANCZOS method
        photo = ImageTk.PhotoImage(image)

        # Label for the first image
        label_image = tk.Label(message_frame, image=photo, bg="white")
        label_image.image = photo  # keep a reference!

        # Label for text with configurable font size
        font = ("Helvetica", 14)
        label_text = tk.Label(message_frame, text=message, font=font, wraplength=500, bg="white", justify="left")

        # Button for the second image (image2) on the opposite side of the first image
        button_text = tk.Button(message_frame, text="🔊", bg="white", borderwidth=0, font=("Helvetica", 16),
                                cursor="hand2", command=lambda: self.start_tts(message))
        self.tts_buttons.append(button_text)

        if side == 'left':
            label_image.pack(side='left', padx=10, pady=10, anchor="n")
            label_text.pack(side='left', padx=10, pady=10, fill="both", expand=True)
            button_text.pack(side='right', padx=10, pady=10, anchor="n")
        else:
            button_text.pack(side='left', padx=10, pady=10, anchor="n")
            label_text.pack(side='left', padx=10, pady=10, fill="both", expand=True)
            label_image.pack(side='right', padx=10, pady=10, anchor="n")

        self.message_frames.append(message_frame)

        # Update scroll region and scroll to bottom
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

    def _create_loading(self):
        # Frame for the message
        message_frame = tk.Frame(self.chat_frame, bg="white")

        # Determine the correct side for the message frame within the chat frame
        message_frame.pack(padx=10, pady=5, anchor='e')
        name_label = tk.Label(message_frame, text="Chatbot", bg="white", justify="center",
                              font=("Helvetica", 12))
        name_label.pack(side='top', padx=10, pady=(5, 0), anchor="e")

        label_image = AnimatedGIFLabel(message_frame, LOADING_IMAGE, bg="white")
        label_image.pack(side='right', padx=10, pady=10, anchor="n")
        self.message_frames.append(message_frame)
        self.canvas.update_idletasks()
        self.canvas.yview_moveto(1)

    def _on_frame_configure(self, _):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _on_canvas_configure(self, event):
        # Update the scroll region to encompass the inner frame
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def _remove_last_message(self):
        if self.message_frames:  # Ensure there's a message to remove
            last_frame = self.message_frames.pop()  # Get the last frame
            last_frame.destroy()  # Remove it from the display

    def _send_message(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        username = self.username_entry.get().strip() or DEFAULT_NAME
        usertype = self.usertype_entry.get().strip() or DEFAULT_TYPE
        location = self.location_entry.get().strip() or DEFAULT_LOCATION
        region_id = self.region_id
        if message:
            self.create_chatbox(message, USER_IMAGE, side='left')
            print(f"Sent message: {message}")
            self.message_entry.delete("1.0", tk.END)
            time.sleep(LOADING_DELAY)
            self._create_loading()
            response = send_api_request(message, username, usertype, location, region_id)
            self._remove_last_message()
            self.create_chatbox(response, BOT_IMAGE, side='right')
        self.send_button.config(state=tk.NORMAL)

    def on_send_button_click(self):
        # Disable the send button
        self.send_button.config(state=tk.DISABLED)
        # Run send_message in a separate thread
        threading.Thread(target=self._send_message).start()

    def start_tts(self, text):
        for button in self.tts_buttons:
            # disable button and change cursor
            button.config(state=tk.DISABLED, cursor="arrow")
        thread = threading.Thread(target=self._text_to_speech, args=(text,))
        thread.start()

    # TODO: different voices, voice constant
    def _text_to_speech(self, text):
        engine = pyttsx3.init()
        engine.setProperty('rate', 150)  # Speed of speech
        engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
        engine.say(text)
        try:
            engine.runAndWait()
        except RuntimeError:
            print("TTS already running")
        finally:
            for button in self.tts_buttons:
                # renable button and change cursor
                button.config(state=tk.NORMAL, cursor="hand2")


class AnimatedGIFLabel(tk.Label):
    def __init__(self, master, path, *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.master = master
        self.path = path
        self.image = Image.open(self.path)

        self.frames = []
        try:
            for i in itertools.count():
                photo = ImageTk.PhotoImage(self.image.copy().resize((50, 50), Image.Resampling.LANCZOS))
                self.frames.append(photo)
                self.image.seek(i)
        except EOFError:
            pass

        self.index = 0
        self.label = tk.Label(self.master, image=self.frames[0], bg="white")
        self.label.pack()

        self.animate()

    def animate(self):
        self.index = (self.index + 1) % len(self.frames)
        self.label.configure(image=self.frames[self.index])
        self.master.after(100, self.animate)  # Adjust the frame delay as needed


def send_api_request(message: str, username: str, usertype: str, location: str, region_id: int):
    if SCRIPTED_RESPONSES:
        time.sleep(2)
        return SCRIPTED_RESPONSES.pop(0)
    else:
        url = f'{URL}/generate'

        data = {
            'username': username,
            'message': message,
            'usertype': usertype,
            'location': location,
            'region_id': region_id
        }

        json_data = json.dumps(data)
        try:
            print(f"{usertype} usertype for user {username} in {location} under region {region_id} sending message: {message}")
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


def retrieve_regions_and_save():
    url = f'{URL}/retrieve_regions'

    try:
        response = requests.get(url)
    except requests.exceptions.ConnectionError as e:
        print("Error, no connection")
        return  # Do nothing if there's a connection error

    if response.status_code == 200:
        # Get the JSON response
        response_data = response.json()

        # Save the result to a local file
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


if __name__ == "__main__":
    retrieve_regions_and_save()
    app = ChatInterface()
    app.mainloop()
