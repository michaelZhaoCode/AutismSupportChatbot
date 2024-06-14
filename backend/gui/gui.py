import tkinter as tk
from tkinter import scrolledtext, ttk
import threading
import requests
import json


class ChatInterface(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Rudimentary Chat Interface")
        self.geometry("600x720")  # Set the window size
        self.resizable(False, False)

        # Chat history pane with scrolling
        self.chat_history = scrolledtext.ScrolledText(self, wrap=tk.WORD, state='disabled', font=("Helvetica", 14),
                                                      height=20, padx=10, pady=10)
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=False)

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
        self.send_button = tk.Button(self.entry_frame, text="Send", command=self.on_send_button_click, font=("Helvetica", 14))
        self.send_button.grid(row=0, column=1, padx=5, pady=5)
        self.send_button.config(height=self.button_height * 2, width=self.button_height * 5)  # Makes the button square

        # Chatbox to write a message
        self.message_entry = tk.Text(self.entry_frame, height=5, wrap=tk.WORD, font=("Helvetica", 14), padx=10, pady=10)
        self.message_entry.grid(row=0, column=0, sticky="ew")
        self.message_entry.config(height=self.button_height * 2)

        # Configure grid weights
        self.entry_frame.columnconfigure(0, weight=1)  # Text entry takes maximum possible space
        self.entry_frame.columnconfigure(1, weight=0)  # Button size is fixed

    def create_chatbox(self, message, side='left'):
        self.chat_history.config(state='normal')
        tag = "user" if side == 'left' else "other"
        bubble_text = f"\n{message}\n"
        self.chat_history.insert(tk.END, bubble_text, tag)
        self.chat_history.insert(tk.END, "\n", tag)  # Add spacing after each message

        # Configuring tags with dynamic margins based on text size
        self.chat_history.tag_configure("user", background="#E6E6FA", lmargin1=10, lmargin2=10, rmargin=50, spacing3=10)
        self.chat_history.tag_configure("other", background="#DDDDDE", lmargin1=50, lmargin2=50, rmargin=10,
                                        spacing3=10)

        self.chat_history.config(state='disabled')
        self.chat_history.yview(tk.END)

    def send_message(self):
        message = self.message_entry.get("1.0", tk.END).strip()
        username = self.username_entry.get().strip() or "Bob"
        usertype = self.usertype_entry.get().strip() or "Adult"
        if message:
            self.create_chatbox(message, side='left')
            print(f"Sent message: {message}")
            self.message_entry.delete("1.0", tk.END)
            response = send_api_request(message, username, usertype)
            self.create_chatbox(response, side='right')

    def on_send_button_click(self):
        # Disable the send button
        self.send_button.config(state=tk.DISABLED)
        # Run send_message in a separate thread
        threading.Thread(target=self.send_message_with_reenable).start()

    def send_message_with_reenable(self):
        self.send_message()
        # Re-enable the send button
        self.send_button.config(state=tk.NORMAL)


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


if __name__ == "__main__":
    app = ChatInterface()
    app.mainloop()
