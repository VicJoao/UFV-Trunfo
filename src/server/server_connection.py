import socket
import threading
import pickle

# Defina as portas
DISCOVERY_PORT = 4242
COMM_PORT_START = 4243
COMM_PORT_END = 4245
MAX_CLIENTS_PER_PORT = 1

class Message:
    HANDSHAKE = 1
    CONNECT = 2
    PLAYERDATA = 3
    DISCONNECT = 4

    def __init__(self, message_type, data):
        self.message_type = message_type
        self.data = data

    def to_bytes(self):
        data_bytes = pickle.dumps(self.data)
        message_length = len(data_bytes)
        return self.message_type.to_bytes(1, byteorder='big') + message_length.to_bytes(4, byteorder='big') + data_bytes

    @staticmethod
    def from_bytes(message_bytes):
        message_type = message_bytes[0]
        message_length = int.from_bytes(message_bytes[1:5], byteorder='big')
        data_bytes = message_bytes[5:5 + message_length]
        data = pickle.loads(data_bytes)
        return Message(message_type, data)

class Server:
    def __init__(self):
        self.port_map = {}  # Guarda a porta alocada para cada cliente
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server_socket.bind(('localhost', DISCOVERY_PORT))
        print(f"Servidor de descoberta iniciado na porta {DISCOVERY_PORT}")

    def start(self):
        threading.Thread(target=self.handle_discovery).start()
        threading.Thread(target=self.accept_connections).start()

    def handle_discovery(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            if data.decode('utf-8') == "Discovery":
                response = "Server Name:MyServer"
                self.server_socket.sendto(response.encode('utf-8'), addr)

    def accept_connections(self):
        for port in range(COMM_PORT_START, COMM_PORT_END + 1):
            threading.Thread(target=self.listen_on_port, args=(port,)).start()

    def listen_on_port(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind(('localhost', port))
            server_socket.listen(MAX_CLIENTS_PER_PORT)
            print(f"Escutando na porta {port}...")
            while True:
                conn, addr = server_socket.accept()
                threading.Thread(target=self.handle_client, args=(conn, addr)).start()

    def handle_client(self, conn, addr):
        try:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                message = Message.from_bytes(data)
                if message.message_type == Message.CONNECT:
                    port = self.allocate_port(addr)
                    response = f"Connected to port {port}" if port else "No available ports."
                    conn.sendall(response.encode('utf-8'))
                elif message.message_type == Message.DISCONNECT:
                    self.free_port(self.port_map.get(addr))
                    conn.sendall(b"Disconnected.")
                    break
        finally:
            conn.close()

    def allocate_port(self, addr):
        with self.lock:
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                if port not in self.port_map.values():
                    self.port_map[addr] = port
                    return port
            return None

    def free_port(self, port):
        with self.lock:
            for key, value in list(self.port_map.items()):
                if value == port:
                    del self.port_map[key]

if __name__ == "__main__":
    server = Server()
    server.start()
