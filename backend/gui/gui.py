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

USER_IMAGE = "user.png"
BOT_IMAGE = "chatbot.png"
LOADING_IMAGE = "loading.gif"

LOADING_DELAY = 0


class ChatInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rudimentary Chat Interface")
        self.geometry("700x740")  # Set the window size

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
        self.canvas.bind("<Configure>", self.on_canvas_configure)
        self.chat_frame.bind("<Configure>", self.on_frame_configure)

        self.message_frames = []

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
                                cursor="hand2", command=lambda: text_to_speech(message))

        if side == 'left':
            label_image.pack(side='left', padx=10, pady=10, anchor="n")
            label_text.pack(side='left', padx=10, pady=10, fill="both", expand=True)
            button_text.pack(side='right', padx=10, pady=10, anchor="n")
        else:
            button_text.pack(side='left', padx=10, pady=10, anchor="n")
            label_text.pack(side='left', padx=10, pady=10, fill="both", expand=True)
            label_image.pack(side='right', padx=10, pady=10, anchor="n")

        self.message_frames.append(message_frame)

    def create_loading(self):
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

    def on_frame_configure(self, _):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event):
        # Update the scroll region to encompass the inner frame
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def remove_last_message(self):
        if self.message_frames:  # Ensure there's a message to remove
            last_frame = self.message_frames.pop()  # Get the last frame
            last_frame.destroy()  # Remove it from the display

    def send_message(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        username = self.username_entry.get().strip() or DEFAULT_NAME
        usertype = self.usertype_entry.get().strip() or DEFAULT_TYPE
        if message:
            self.create_chatbox(message, USER_IMAGE, side='left')
            print(f"Sent message: {message}")
            self.message_entry.delete("1.0", tk.END)
            time.sleep(LOADING_DELAY)
            self.create_loading()
            response = send_api_request(message, username, usertype)
            self.remove_last_message()
            self.create_chatbox(response, BOT_IMAGE, side='right')

    def on_send_button_click(self):
        # Disable the send button
        self.send_button.config(state=tk.DISABLED)
        # Run send_message in a separate thread
        threading.Thread(target=self.send_message_with_reenable).start()

    def send_message_with_reenable(self):
        self.send_message()
        # Re-enable the send button
        self.send_button.config(state=tk.NORMAL)


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


def send_api_request(message: str, username: str, usertype: str):
    url = 'http://127.0.0.1:5000/generate'

    data = {
        'username': username,
        'message': message,
        'usertype': usertype
    }

    json_data = json.dumps(data)
    response = requests.post(url, data=json_data, headers={'Content-Type': 'application/json'})
    if response.status_code == 200:
        # Print the JSON response from the server
        response_data = response.json()

        # Access and print the specific part of the response, i.e., the response from the chat function
        print('Response from server:', response_data['response'])
        return response_data['response']
    else:
        # Print the error
        print('Failed to get a valid response:', response.status_code, response.text)

def text_to_speech(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 140)  # Speed of speech
    engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
    engine.say(text)
    engine.runAndWait()


if __name__ == "__main__":
    app = ChatInterface()
    app.mainloop()
