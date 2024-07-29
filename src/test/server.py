# server.py

import socket
import threading

class Server(threading.Thread):
    def __init__(self):
        super().__init__()
        self.server_socket = None

    def run(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind(('localhost', 12345))
        self.server_socket.listen(5)
        print("Server started and listening for connections...")

        while True:
            client_socket, address = self.server_socket.accept()
            print(f"Connection from {address}")
            threading.Thread(target=self.handle_client, args=(client_socket,)).start()

    def handle_client(self, client_socket):
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            print(f"Received data: {data.decode()}")
            client_socket.sendall(b"Message received")
        client_socket.close()
