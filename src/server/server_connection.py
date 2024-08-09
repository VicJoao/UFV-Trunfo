import socket
import threading

from models.deck import Deck
from server2.message import Message

# Define as portas
MAX_CLIENTS = 3
DISCOVERY_PORT = 4242
COMM_PORT_START = 4243
COMM_PORT_END = COMM_PORT_START + MAX_CLIENTS
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
        self.port = []


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
                            print("DADOS DO JOGADOR RECEBIDOS, JOGADOR : ", {message.data['player_name']},
                                  {message.data['deck']})

                            response = Message(Message.PLAYER_DATA, "Player data received")
                            conn.sendall(response.to_bytes())

                            # Verifica se o número de jogadores é 3
                            if self.num_players == 3:
                                # Envia a mensagem para todas as portas para iniciar o jogo
                                for port in self.port:
                                    start_game_message = Message(Message.START_GAME, "O jogo está começando!")
                                    send_message(addr[0], port, start_game_message)



                        elif message.message_type == Message.CLIENT_PORT:

                            # Atualiza a porta do cliente
                            self.port.append(message.data['player_port'])
                            nome = message.data['nome_jogador']

                            # Função para enviar uma mensagem
                            def send_message(host, server_client_port, message):
                                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                                    s.sendto(message.to_bytes(), (host, server_client_port))

                            # Envia a mensagem para todas as portas
                            for port in self.port:
                                message = Message(Message.NEW_PLAYER, nome)
                                send_message(addr[0], port, message)

                        elif message.message_type == Message.DISCONNECT:
                            response = Message(Message.DISCONNECT, "Disconnect")
                            conn.sendall(response.to_bytes())
                            print(f"Desconexão com {addr}")
                            self.disconnect(addr)
                            # Envia mensagem de desconexão para todos os clientes
                            for client_addr in self.port_map:
                                response = Message(Message.DISCONNECT, "A user has disconnected")
                                self.server_socket.sendto(response.to_bytes(), client_addr)

                        elif message.message_type == Message.START_GAME:
                            self.start_game()



                        else:
                            response = Message(Message.TYPO_ERROR, "Unknown message type " + str(message.message_type))
                            conn.sendall(response.to_bytes())
                            print(f"Erro de mensagem com {addr}, conexão recusada, com erro {response.data}")
                    except Exception as e:
                        print(f"Erro ao processar mensagem de {addr}: {e}")

    def update_client_port(self, addr, port):
        # Atualiza a porta do cliente na sua estrutura de dados
        if addr not in self.client_ports:
            self.client_ports[addr] = port
        else:
            self.client_ports[addr] = port
        print(f"Porta do cliente {addr} atualizada para {port}")

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
