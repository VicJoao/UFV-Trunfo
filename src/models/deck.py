import socket
import dotenv
import os
import pickle
from models.card import Card
from models.deck import Deck  # Importe a classe Deck


class Server:
    def __init__(self):
        # Get the host and port from the .env file
        dotenv.load_dotenv()
        self.host = os.getenv("HOST")
        self.port = int(os.getenv("PORT"))  # Convert PORT to integer
        self.name = ""
        self.password = ""

    def create(self, name, password):
        self.name = name
        self.password = password
        self.start()

    def start(self):
        try:
            self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server.bind((self.host, self.port))
            self.server.listen(1)
            print(f"Server {self.name} started on {self.host}:{self.port}")
            self.accept_connections()
        except Exception as e:
            print(f"Error starting server: {e}")

    def accept_connections(self):
        while True:
            try:
                client, address = self.server.accept()
                print(f"Connection from {address}")

                # Request password from client
                client.send("Enter password:".encode())
                password = client.recv(1024).decode()

                if password == self.password:
                    client.send("Enter client name:".encode())
                    client_name = client.recv(1024).decode()

                    # Receive serialized deck
                    client.send("Send your deck:".encode())
                    deck_data = client.recv(4096)  # Receive the serialized deck data

                    try:
                        deck = pickle.loads(deck_data)
                        if not isinstance(deck, Deck):
                            raise TypeError("Received object is not a Deck instance.")

                        print(f"Client {client_name} connected with deck:")
                        deck.display()
                    except Exception as e:
                        print(f"Error receiving deck: {e}")
                        client.send("Error receiving deck".encode())

                else:
                    client.send("Incorrect password".encode())
                client.close()

            except Exception as e:
                print(f"Error handling connection: {e}")

    def stop(self):
        try:
            self.server.close()
            print("Server stopped")
        except Exception as e:
            print(f"Error stopping server: {e}")
