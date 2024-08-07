import socket
import threading
import tkinter as tk
from tkinter import messagebox

class ConnectionClient:
    def __init__(self):
        self.client_socket = None
        self.server_ip = None
        self.server_port = 12345  # Default port
        self.client_name = "Client"
        self.connection_thread = None
        self.window = None
        self.server_listbox = None

    def show(self):
        self.window = tk.Tk()
        self.window.title("Client")

        # Listbox to show servers
        self.server_listbox = tk.Listbox(self.window)
        self.server_listbox.pack()

        # Button to find servers
        self.find_button = tk.Button(self.window, text="Find Servers", command=self.find_servers)
        self.find_button.pack()

        # Button to connect to selected server
        self.connect_button = tk.Button(self.window, text="Connect to Server", command=self.connect_to_server)
        self.connect_button.pack()

        # Start GUI loop
        self.window.mainloop()

    def find_servers(self):
        if self.server_listbox is None:
            messagebox.showerror("Error", "Server listbox is not initialized.")
            return

        self.server_listbox.delete(0, tk.END)  # Clear existing list
        servers = []
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            sock.settimeout(5)
            try:
                sock.sendto(b"DISCOVER", ('<broadcast>', self.server_port))
                print("Discovery message sent.")
                while True:
                    try:
                        message, _ = sock.recvfrom(1024)
                        if message.startswith(b"SERVER_INFO:"):
                            server_name = message.decode().split(":", 1)[1]
                            servers.append(server_name)
                            self.server_listbox.insert(tk.END, server_name)  # Add server name to list
                            print(f"Server found: {server_name}")
                    except socket.timeout:
                        break
            except Exception as e:
                print(f"Find servers error: {e}")

        if not servers:
            print("No servers found.")
            messagebox.showinfo("Info", "No servers found.")

    def connect_to_server(self):
        selected_server = self.server_listbox.get(tk.ACTIVE)
        if not selected_server:
            messagebox.showerror("Error", "No server selected.")
            return

        # Assuming the selected server is in the format 'server_name'
        self.server_ip = self._resolve_server_ip(selected_server)

        if not self.server_ip:
            messagebox.showerror("Error", "Server IP could not be resolved.")
            return

        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.server_ip, self.server_port))
            self.connection_thread = threading.Thread(target=self._receive_messages)
            self.connection_thread.start()
            messagebox.showinfo("Info", f"Connected to server at {self.server_ip}.")
        except Exception as e:
            messagebox.showerror("Error", f"Connection error: {e}")

    def _resolve_server_ip(self, server_name):
        # This is a placeholder function. Implement IP resolution if needed.
        return "127.0.0.1"  # Replace with actual IP resolution logic

    def _receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                print(f"Received message: {message}")
            except Exception as e:
                print(f"Receive message error: {e}")
                break

    def disconnect(self):
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
            messagebox.showinfo("Info", "Disconnected from server.")

if __name__ == "__main__":
    client = ConnectionClient()
    client.show()
