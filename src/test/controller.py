# controller.py

import threading
import socket
import time


class Controller(threading.Thread):
    def __init__(self, model):
        super().__init__()
        self.model = model
        self.server_thread = None
        self.server_socket = None

    def run(self):
        # Optional: Start server thread
        self.server_thread = threading.Thread(target=self.start_server)
        self.server_thread.start()

        # Simulate handling of other tasks
        while True:
            # Perform controller logic here
            time.sleep(5)  # Adjusted sleep time for easier observation

    def handle_user_input(self, input):
        if input.startswith("update"):
            new_data = input.split(" ", 1)[1]
            self.model.update_data(new_data)
            print(f"Data updated to: {self.model.get_data()}")
        elif input.startswith("connect"):
            # Handle connection logic to server
            print("Connecting to server...")
            self.connect_to_server()

    def start_server(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind(('localhost', 12345))
            self.server_socket.listen(5)
            print("Server started and listening for connections...")

            while True:
                client_socket, address = self.server_socket.accept()
                print(f"Connection from {address}")
                threading.Thread(target=self.handle_client, args=(client_socket,)).start()

        except OSError as e:
            print(f"Error starting server: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received data: {data.decode()}")
            client_socket.sendall(b"Message received")
        client_socket.close()

    def connect_to_server(self):
        try:
            # Connect to the server
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 12345))
            client_socket.sendall(b"Hello Server")
            response = client_socket.recv(1024)
            print(f"Received from server: {response.decode()}")
        except Exception as e:
            print(f"Error connecting to server: {e}")
        finally:
            client_socket.close()
