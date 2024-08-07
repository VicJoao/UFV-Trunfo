import socket
import threading
import tkinter as tk
from tkinter import messagebox
import time

class ConnectionServer:
    def __init__(self):
        self.server_socket = None
        self.server_ip = "0.0.0.0"  # Bind to all interfaces
        self.server_port = 12345  # Default port
        self.clients = []
        self.server_name = ""
        self.broadcast_thread = None
        self.accept_thread = None

    def create_server(self, server_name):
        if self.server_socket:
            messagebox.showerror("Error", "Server is already running.")
            return

        self.server_name = server_name
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.server_ip, self.server_port))
        self.server_socket.listen(5)
        messagebox.showinfo("Info", f"Server '{self.server_name}' created successfully.")

        # Start broadcasting server info
        self.broadcast_thread = threading.Thread(target=self._broadcast_server_info)
        self.broadcast_thread.start()

        # Start accepting client connections
        self.accept_thread = threading.Thread(target=self._accept_connections)
        self.accept_thread.start()

    def _broadcast_server_info(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            while True:
                try:
                    message = f"SERVER_INFO:{self.server_name}".encode()
                    sock.sendto(message, ('<broadcast>', self.server_port))
                    time.sleep(5)  # Intervalo entre broadcasts
                except Exception as e:
                    print(f"Broadcast error: {e}")

    def _accept_connections(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            self.clients.append(client_socket)
            print(f"Client connected: {client_address}")

    def show(self):
        pass  # No GUI for server; if needed, use tk.Toplevel() to show server-related messages

    def stop(self):
        if self.server_socket:
            self.server_socket.close()
            self.server_socket = None
            messagebox.showinfo("Info", "Server stopped.")

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()  # Hide main window
    server = ConnectionServer()
    server.create_server("MyServer")
    root.mainloop()
