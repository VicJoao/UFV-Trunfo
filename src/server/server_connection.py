import socket
import threading
import pickle

from models.deck import Deck
from server2.message import Message

# Defina as portas
MAX_CLIENTS = 3
DISCOVERY_PORT = 4242
COMM_PORT_START = 4243
COMM_PORT_END = COMM_PORT_START + MAX_CLIENTS
CLI_PORT = 4096
MAX_CLIENTS_PER_PORT = 1


class Server:
    def __init__(self):
        self.port_map = {}  # Guarda a porta alocada para cada cliente
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', DISCOVERY_PORT))
        self.server_name = "Server UFV"
        self.num_players = 0
        self.players = []  # Lista de jogadores
        print(f"Servidor de descoberta iniciado na porta {DISCOVERY_PORT}")

    def start(self):
        try:
            threading.Thread(target=self.handle_discovery, daemon=True).start()
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                threading.Thread(target=self.accept_connections, args=(port,), daemon=True).start()
            input("Pressione Enter para encerrar o servidor...")
        finally:
            self.server_socket.close()
            print("Servidor fechado e porta liberada.")

    def handle_discovery(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            message = Message.from_bytes(data)
            if message.message_type == Message.HANDSHAKE:
                response = Message(Message.HANDSHAKE,
                                   self.server_name + "-" + str(self.num_players) + "/" + str(MAX_CLIENTS))
                self.server_socket.sendto(response.to_bytes(), addr)
                print(f"Handshake com {addr}")
            elif message.message_type == Message.CONNECT:
                port = self.get_available_port()
                if self.num_players < MAX_CLIENTS and port:
                    self.port_map[addr] = port
                    response = Message(Message.CONNECT, port)
                    self.server_socket.sendto(response.to_bytes(), addr)
                    print(f"Conexão com {addr} na porta {port}")
                    self.num_players += 1
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
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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

                            # Atualiza a lista de jogadores e envia para todos os clientes
                            self.players.append(message.data['player_name'])
                            self.send_new_player_to_all_clients(message.data['player_name'])

                        elif message.message_type == Message.DISCONNECT:
                            response = Message(Message.DISCONNECT, "Disconnect")
                            conn.sendall(response.to_bytes())
                            print(f"Desconexão com {addr}")
                            self.disconnect(addr)
                            # Envia mensagem de desconexão para todos os clientes
                            for addr in self.port_map:
                                response = Message(Message.DISCONNECT, "A user has disconnected")
                                self.server_socket.sendto(response.to_bytes(), addr)

                        elif message.message_type == Message.START_GAME:
                            self.start_game()

                        elif message.message_type == Message.NEW_PLAYER:
                            self.add_new_player(message.data)

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

    def disconnect(self, addr):
        with self.lock:
            if addr in self.port_map:
                port = self.port_map[addr]
                del self.port_map[addr]
                print(f"Cliente {addr} desconectado da porta {port}")

    def send_new_player_to_all_clients(self, player_name):
        new_player_message = Message(Message.NEW_PLAYER, player_name)
        for addr in self.port_map:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                    udp_socket.sendto(new_player_message.to_bytes(), addr)
            except Exception as e:
                print(f"Erro ao enviar nova mensagem de jogador para {addr}: {e}")

    def start_game(self):
        start_game_message = Message(Message.START_GAME, "Game is starting")
        for addr in self.port_map:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                    udp_socket.sendto(start_game_message.to_bytes(), addr)
            except Exception as e:
                print(f"Erro ao enviar mensagem de início de jogo para {addr}: {e}")

    def add_new_player(self, player_name):
        new_player_message = Message(Message.NEW_PLAYER, player_name)
        for addr in self.port_map:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                    udp_socket.sendto(new_player_message.to_bytes(), addr)
            except Exception as e:
                print(f"Erro ao enviar nova mensagem de jogador para {addr}: {e}")


if __name__ == '__main__':
    server = Server()
    server.start()
