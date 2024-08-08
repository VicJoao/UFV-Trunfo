import socket
import threading
from src.server2.message import Message

# Defina as portas
DISCOVERY_PORT = 4242
COMM_PORT_START = 4243
COMM_PORT_END = 4245
CLI_PORT = 4096
MAX_CLIENTS_PER_PORT = 1

class Server:
    def __init__(self):
        self.port_map = {}  # Guarda a porta alocada para cada cliente
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server_socket.bind(('localhost', DISCOVERY_PORT))
        self.server_name = "Server001"
        self.palyers = []
        print(f"Servidor de descoberta iniciado na porta {DISCOVERY_PORT}")

    def start(self):
        threading.Thread(target=self.handle_discovery, daemon=True).start()
        for port in range(COMM_PORT_START, COMM_PORT_END + 1):
            threading.Thread(target=self.accept_connections, args=(port,), daemon=True).start()

    def handle_discovery(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            message = Message.from_bytes(data)
            if message.message_type == Message.HANDSHAKE:
                response = Message(Message.HANDSHAKE, self.server_name)
                self.server_socket.sendto(response.to_bytes(), addr)
                print(f"Handshake com {addr}")
            elif message.message_type == Message.CONNECT:
                port = self.get_available_port()
                if port:
                    self.port_map[addr] = port
                    response = Message(Message.CONNECT, port)
                    self.server_socket.sendto(response.to_bytes(), addr)
                    print(f"Conexão com {addr} na porta {port}")
                else:
                    response = Message(Message.CONNECT, "No available ports")
                    self.server_socket.sendto(response.to_bytes(), addr)
                    print(f"Sem portas disponíveis para {addr}")
            else:
                response = Message(Message.TYPO_ERROR, "Unknown message type " + str(message.message_type))
                self.server_socket.sendto(response.to_bytes(), addr)
                print(f"Erro de mensagem com {addr}, conexão recusada, com erro {response.data}")

    def accept_connections(self, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            s.listen(MAX_CLIENTS_PER_PORT)
            print(f"Servidor de comunicação iniciado na porta {port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Conexão estabelecida com {addr}")
                    try:
                        message = Message.from_bytes(conn.recv(1024))
                        if message.message_type == Message.PLAYER_DATA:
                            print(f"Dados do jogador {message.data['player_name']} recebidos")
                            response = Message(Message.PLAYER_DATA, "Player data received")
                            conn.sendall(response.to_bytes())

                        elif message.message_type == Message.DISCONNECT:
                            response = Message(Message.DISCONNECT, "Disconnect")
                            conn.sendall(response.to_bytes())
                            print(f"Desconexão com {addr}")
                            self.disconect(addr)
                        else:
                            response = Message(Message.TYPO_ERROR, "Unknown message type " + str(message.message_type))
                            conn.sendall(response.to_bytes())
                            print(f"Erro de mensagem com {addr}, conexão recusada, com erro {response.data}")
                    except Exception as e:
                        print(f"Erro ao processar mensagem de {addr}: {e}")

    def get_available_port(self):
        with self.lock:
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                if port not in self.port_map.values():
                    return port
        return None

    def disconect(self, addr):
        with self.lock:
            if addr in self.port_map:
                port = self.port_map[addr]
                del self.port_map[addr]
                print(f"Cliente {addr} desconectado da porta {port}")

if __name__ == '__main__':
    server = Server()
    server.start()
    input("Pressione Enter para encerrar o servidor...")
    server.server_socket.close()
