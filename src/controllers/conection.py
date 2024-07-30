import socket
import threading
import time


class Connection:
    def __init__(self, host='0.0.0.0', server_port=5002, broadcast_port=6002):
        self.host = host
        self.server_port = server_port
        self.broadcast_port = broadcast_port

    def create_server(self):
        """
        Create a server to handle incoming connections and broadcast its presence.
        """

        def broadcast():
            """
            Broadcast a message to announce the server's presence.
            """
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as sock:
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
                message = b'SERVER_DISCOVERY'
                print("Broadcast thread started")
                while True:
                    try:
                        sock.sendto(message, ('<broadcast>', self.broadcast_port))
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
                try:
                    sock.bind(('', self.broadcast_port))
                    print("Listening for servers...")
                    while True:
                        try:
                            data, addr = sock.recvfrom(1024)
                            if data == b'SERVER_DISCOVERY':
                                print(f"Discovered server at {addr}")
                                servers.append(addr)
                        except Exception as e:
                            print(f"Error receiving data: {e}")
                except OSError as e:
                    print(f"Error binding to port {self.broadcast_port}: {e}")

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

        # Start the server discovery thread
        discover_thread = threading.Thread(target=discover_servers, daemon=True)
        discover_thread.start()

        # Wait for some time to discover servers
        time.sleep(10)

        # Display discovered servers and let the user select one
        if servers:
            print("\nAvailable servers:")
            for idx, server in enumerate(servers):
                print(f"{idx}: {server}")

            choice = int(input("Select a server by number: "))
            if 0 <= choice < len(servers):
                selected_server = servers[choice]
                print(f"Connecting to server at {selected_server}...")
                connect_to_server(selected_server)
            else:
                print("Invalid choice.")
        else:
            print("No servers found.")


if __name__ == "__main__":
    # To create a server
    conn = Connection()
    conn.create_server()

    # To scan for servers (comment out the above line and uncomment the below line if you want to scan)
    # conn = Connection()
    # conn.scan()
