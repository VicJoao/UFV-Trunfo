# view.py

import tkinter as tk
from tkinter import scrolledtext


class View:
    def __init__(self, controller):
        self.controller = controller
        self.window = tk.Tk()
        self.window.title("MVC View")

        # Create a text area
        self.text_area = scrolledtext.ScrolledText(self.window, width=40, height=10)
        self.text_area.pack(pady=10)

        # Create input field
        self.entry = tk.Entry(self.window, width=40)
        self.entry.pack(pady=10)

        # Create a submit button
        self.submit_button = tk.Button(self.window, text="Submit", command=self.submit)
        self.submit_button.pack(pady=10)

        # Create a quit button
        self.quit_button = tk.Button(self.window, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

    def start(self):
        self.window.mainloop()

    def submit(self):
        user_input = self.entry.get()
        self.text_area.insert(tk.END, f"Input: {user_input}\n")
        self.controller.handle_user_input(user_input)
        self.entry.delete(0, tk.END)

    def quit(self):
        self.window.quit()
