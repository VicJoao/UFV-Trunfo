import socket
import threading
import time

class Connection:
    def __init__(self, host='127.0.0.1', server_port=5002, broadcast_port=6002):
        self.host = host
        self.server_port = server_port
        self.broadcast_port = broadcast_port

    def create_server(self, name):
        """
        Create a server to handle incoming connections and broadcast its presence.
        """
        def broadcast():
            """
            Broadcast a message to announce the server's presence.
            """
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                message = f'SERVER_DISCOVERY:{name}'.encode('utf-8')
                print("Broadcast thread started")
                while True:
                    try:
                        sock.sendto(message, ('127.0.0.1', self.broadcast_port))
                        print(f"Broadcasting message to port {self.broadcast_port}")
                        time.sleep(5)  # Broadcast every 5 seconds
                    except Exception as e:
                        print(f"Broadcast error: {e}")

        def start_server():
            """
            Start the server to listen for incoming connections.
            """
            while True:
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                        server_socket.bind((self.host, self.server_port))
                        server_socket.listen(5)
                        print(f"Server listening on {self.host}:{self.server_port}")
                        print("Waiting for connections...")

                        while True:
                            try:
                                client_socket, client_address = server_socket.accept()
                                print(f"Connected with client at {client_address}")
                                with client_socket:
                                    data = client_socket.recv(1024)
                                    if data:
                                        print(f"Received data: {data.decode('utf-8')}")
                                        client_socket.sendall(b"Hello, Client!")
                            except Exception as e:
                                print(f"Server error during communication: {e}")
                except OSError as e:
                    print(f"Error binding to port {self.server_port}: {e}")
                    time.sleep(5)  # Wait before retrying

        # Start broadcasting and server threads
        broadcast_thread = threading.Thread(target=broadcast, daemon=True)
        server_thread = threading.Thread(target=start_server, daemon=True)

        print("Starting server and broadcast threads")
        broadcast_thread.start()
        server_thread.start()

        # Adicione um loop principal para manter o script rodando
        while True:
            time.sleep(1)

    def scan(self):
        """
        Scan for servers broadcasting their presence and let the user choose a server to connect to.
        """
        servers = []

        def discover_servers():
            """
            Discover servers broadcasting their presence.
            """
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                sock.bind(('', self.broadcast_port))
                print("Listening for servers...")
                while True:
                    try:
                        data, addr = sock.recvfrom(1024)
                        if data.startswith(b'SERVER_DISCOVERY:'):
                            name = data.decode('utf-8').split(':', 1)[1]
                            print(f"Discovered server '{name}' at {addr}")
                            servers.append((addr, name))
                    except Exception as e:
                        print(f"Error receiving data: {e}")

        def connect_to_server(server_addr):
            """
            Connect to the selected server and exchange data.
            """
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                try:
                    client_socket.connect(server_addr)
                    client_socket.sendall(b"Hello, Server!")
                    data = client_socket.recv(1024)
                    print(f"Received from server: {data.decode('utf-8')}")
                except Exception as e:
                    print(f"Connection error: {e}")

        def scan_loop():
            """
            Continuously scan for servers and allow user interaction.
            """
            while True:
                # Start the server discovery thread
                discover_thread = threading.Thread(target=discover_servers, daemon=True)
                discover_thread.start()

                # Wait for some time to discover servers
                time.sleep(10)

                # Display discovered servers and let the user select one
                if servers:
                    print("\nAvailable servers:")
                    for idx, (server, name) in enumerate(servers):
                        print(f"{idx}: {name} at {server}")

                    try:
                        choice = int(input("Select a server by number: "))
                        if 0 <= choice < len(servers):
                            selected_server, _ = servers[choice]
                            print(f"Connecting to server at {selected_server}...")
                            connect_to_server(selected_server)
                        else:
                            print("Invalid choice.")
                    except ValueError:
                        print("Invalid input. Please enter a number.")
                else:
                    print("No servers found.")

                # Wait before scanning again
                time.sleep(10)

        # Start the scanning loop thread
        scan_thread = threading.Thread(target=scan_loop, daemon=True)
        scan_thread.start()

        # Add a loop to keep the script running
        while True:
            time.sleep(1)

if __name__ == "__main__":
    mode = input("Enter 'server' to start a server or 'client' to start scanning for servers: ")
    if mode == 'server':
        server_name = input("Enter server name: ")
        conn = Connection()
        conn.create_server(server_name)
    elif mode == 'client':
        conn = Connection()
        conn.scan()
    else:
        print("Invalid mode. Please enter 'server' or 'client'.")
