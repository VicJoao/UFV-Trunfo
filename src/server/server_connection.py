import socket
import threading
import pickle

from models.deck import Deck


class Message:
    HANDSHAKE = 1
    CONNECT = 2
    PLAYER_DATA = 3
    DISCONNECT = 4
    TYPO_ERROR = 5

    def __init__(self, message_type, data):
        self.message_type = message_type
        self.data = data

    def to_bytes(self):
        data_bytes = pickle.dumps(self.data)
        length = len(data_bytes)
        return self.message_type.to_bytes(1, byteorder='big') + length.to_bytes(4, byteorder='big') + data_bytes

    @classmethod
    def from_bytes(cls, byte_data):
        message_type = byte_data[0]
        length = int.from_bytes(byte_data[1:5], byteorder='big')
        data = pickle.loads(byte_data[5:])
        return cls(message_type, data)


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
        self.server_socket.bind(('0.0.0.0', DISCOVERY_PORT))
        self.server_name = "Bucetona"
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
            s.bind(('0.0.0.0', port))
            s.listen(MAX_CLIENTS_PER_PORT)
            print(f"Servidor de comunicação iniciado na porta {port}")
            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Conexão estabelecida com {addr}")
                    try:
                        message = Message.from_bytes(conn.recv(1024))

                        if message.message_type == Message.PLAYER_DATA:
                            print("DADOS DO JOGADOR RECEBIDOS!!\n\n")
                            print(f"JOGADOR 1:\n {message.data['player_name']}")
                            deck = message.data['deck']  # Supondo que deck é parte dos dados
                            if isinstance(deck, Deck):
                                for card in deck.get_cards():
                                    print(f"\n\nNome da carta: {card.name}")
                                    print(f"Inteligência: {card.intelligence}")
                                    print(f"Carisma: {card.charisma}")
                                    print(f"Esporte: {card.sport}")
                                    print(f"Humor: {card.humor}")
                                    print(f"Criatividade: {card.creativity}")
                                    print(f"Aparência: {card.appearance}")

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
