import queue
import threading
import tkinter as tk
import socket
import time

class Connection:
    def __init__(self, host='127.0.0.1', server_port=5002, broadcast_port=6002):
        self.host = host
        self.server_port = server_port
        self.broadcast_port = broadcast_port
        self.servers = []  # List to store discovered servers
        self.connections = {}  # Dictionary to store connected clients
        self.user_name = ""
        self.current_server = None
        self.current_client_socket = None

        # Initialize Tkinter
        self.root = tk.Tk()
        self.root.title("Server and Scanner")
        self.text_area = tk.Text(self.root, height=20, width=60)
        self.text_area.pack()
        self.text_area.config(state=tk.DISABLED)

        # Initialize message queue
        self.message_queue = queue.Queue()

        # Start the message processing thread
        self.message_processing_thread = threading.Thread(target=self.process_messages, daemon=True)
        self.message_processing_thread.start()

    def log_message(self, message):
        self.message_queue.put(message)

    def process_messages(self):
        while True:
            message = self.message_queue.get()
            if message is None:
                break
            self.root.after(0, self._log_message, message)

    def _log_message(self, message):
        self.text_area.config(state=tk.NORMAL)
        self.text_area.insert(tk.END, message + "\n")
        self.text_area.config(state=tk.DISABLED)
        self.text_area.yview(tk.END)

    def create_server(self, server_name, user_name):
        self.user_name = user_name
        self.current_server = server_name

        def broadcast():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                message = f'SERVER_DISCOVERY:{server_name}'.encode('utf-8')
                while True:
                    try:
                        sock.sendto(message, ('<broadcast>', self.broadcast_port))
                        time.sleep(5)
                    except Exception as e:
                        self.log_message(f"Broadcast error: {e}")

        def handle_client(client_socket, client_address):
            try:
                data = client_socket.recv(1024)
                if data:
                    self.log_message(f"Received data from {client_address}: {data.decode('utf-8')}")
                    response = f"Hello, {self.user_name}!"
                    client_socket.sendall(response.encode('utf-8'))

                    # Notify all connected clients including the server creator
                    for conn in self.connections.values():
                        if conn:
                            conn.sendall(f"{client_address} connected.".encode('utf-8'))

                    self.update_connected_users()
            finally:
                client_socket.close()
                self.connections.pop(client_address, None)
                self.update_connected_users()

        def start_server():
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.bind((self.host, self.server_port))
                server_socket.listen(5)
                self.log_message(f"Server '{server_name}' listening on {self.host}:{self.server_port}")

                # Automatically connect the server creator
                self.connections[(self.host, self.server_port)] = None
                self.update_connected_users()

                while True:
                    try:
                        client_socket, client_address = server_socket.accept()
                        self.connections[client_address] = client_socket
                        self.log_message(f"Connected with client at {client_address}")
                        threading.Thread(target=handle_client, args=(client_socket, client_address),
                                         daemon=True).start()
                    except Exception as e:
                        self.log_message(f"Server error during communication: {e}")

        broadcast_thread = threading.Thread(target=broadcast, daemon=True)
        server_thread = threading.Thread(target=start_server, daemon=True)
        broadcast_thread.start()
        server_thread.start()

        # Create the server interface
        self.create_server_interface()

    def create_server_interface(self):
        self.root.withdraw()  # Hide the main window
        self.server_window = tk.Toplevel(self.root)
        self.server_window.title(f"Connected to Server '{self.current_server}'")

        self.server_text_area = tk.Text(self.server_window, height=20, width=60)
        self.server_text_area.pack()
        self.server_text_area.config(state=tk.DISABLED)

        # Show server name and user name
        self.update_connected_users()

        self.server_window.protocol("WM_DELETE_WINDOW", self.close_server_window)

    def close_server_window(self):
        self.server_window.destroy()
        self.root.deiconify()  # Show the main window again

    def update_connected_users(self):
        connected_users = [f"Server Creator ({self.user_name})"]
        connected_users.extend(f"{addr}" for addr in self.connections.keys() if addr != (self.host, self.server_port))
        self.server_text_area.config(state=tk.NORMAL)
        self.server_text_area.delete(1.0, tk.END)
        self.server_text_area.insert(tk.END, f"Server Name: {self.current_server}\n")
        self.server_text_area.insert(tk.END, f"User Name: {self.user_name}\n")
        self.server_text_area.insert(tk.END, f"Connected users: {', '.join(connected_users)}\n")
        self.server_text_area.config(state=tk.DISABLED)

    def scan(self, user_name):
        self.user_name = user_name

        def discover_servers():
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind(('', self.broadcast_port))
                while True:
                    try:
                        data, addr = sock.recvfrom(1024)
                        if data.startswith(b'SERVER_DISCOVERY:'):
                            name = data.decode('utf-8').split(':', 1)[1]
                            if (addr, name) not in self.servers:
                                self.servers.append((addr, name))
                                self.log_message(f"Discovered server: {name} ({addr[0]}:{addr[1]})")
                                refresh_server_list()
                    except Exception as e:
                        self.log_message(f"Error receiving data: {e}")

        def connect_to_server(server_addr):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                try:
                    client_socket.connect(server_addr)
                    self.current_client_socket = client_socket
                    client_socket.sendall(f"USER:{self.user_name}".encode('utf-8'))
                    data = client_socket.recv(1024)
                    self.log_message(f"Received from server: {data.decode('utf-8')}")
                    self.create_client_interface(server_addr)
                except Exception as e:
                    self.log_message(f"Connection error: {e}")

        def on_connect_button_click():
            selected_server_index = self.server_listbox.curselection()
            if not selected_server_index:
                self.log_message("No server selected.")
                return
            server_addr = self.servers[selected_server_index[0]][0]
            self.log_message(f"Connecting to server at {server_addr}...")
            connect_to_server(server_addr)

        def refresh_server_list():
            if hasattr(self, 'server_listbox'):
                self.server_listbox.delete(0, tk.END)
                for addr, name in self.servers:
                    self.server_listbox.insert(tk.END, f"{name} ({addr[0]}:{addr[1]})")

        self.server_frame = tk.Frame(self.root)
        self.server_frame.pack()

        self.server_listbox = tk.Listbox(self.server_frame, height=10, width=60)
        self.server_listbox.pack()

        connect_button = tk.Button(self.server_frame, text="Connect", command=on_connect_button_click)
        connect_button.pack()

        discover_thread = threading.Thread(target=discover_servers, daemon=True)
        discover_thread.start()

        # Start Tkinter main loop here
        self.root.mainloop()

    def create_client_interface(self, server_addr):
        self.root.withdraw()  # Hide the main window
        self.client_window = tk.Toplevel(self.root)
        self.client_window.title(f"Connected to Server at {server_addr}")

        self.client_text_area = tk.Text(self.client_window, height=20, width=60)
        self.client_text_area.pack()
        self.client_text_area.config(state=tk.DISABLED)

        self.client_window.protocol("WM_DELETE_WINDOW", self.close_client_window)

    def close_client_window(self):
        self.client_window.destroy()
        self.root.deiconify()  # Show the main window again

    def start(self):
        self.scan("default_user")

