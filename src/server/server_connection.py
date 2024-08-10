import socket
import threading
from server2.game_data import GameData

from server2.message import Message

# Define as portas e variáveis globais
MAX_CLIENTS = 3
DISCOVERY_PORT = 4242
COMM_PORT_START = 4243
COMM_PORT_END = COMM_PORT_START + MAX_CLIENTS
MAX_CLIENTS_PER_PORT = 1


class Server:
    def __init__(self):
        self.porta_receber_cliente = {}  # Guarda a porta que os clientes usam para enviar
        self.porta_enviar_cliente = []  # Porta que deve ser usada para enviar mensagem aos clientes
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', DISCOVERY_PORT))
        self.server_name = "Server UFV"
        self.num_players = 0
        self.players_name = []  # Lista com os nomes
        self.players_data = []  # Lista de jogadores e seus dados
        print(f"Servidor de descoberta iniciado na porta {DISCOVERY_PORT}")
        self.game_data = GameData()

    def start(self):
        try:
            threading.Thread(target=self.handle_discovery, daemon=True).start()
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                threading.Thread(target=self.comunicar_com_clientes, args=(port,), daemon=True).start()
            input("Pressione Enter para encerrar o servidor...")
        finally:
            self.server_socket.close()
            print("Servidor fechado e porta liberada.")

    # Thread usada para o server ficar escutando os clientes, na hora de conectar
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
                    self.porta_receber_cliente[addr] = port
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

    # Função para receber as mensagens do cliente
    def comunicar_com_clientes(self, port):

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(('0.0.0.0', port))
            s.listen(MAX_CLIENTS_PER_PORT)
            print(f"Servidor de comunicação iniciado na porta {port}")

            # Função para enviar mensagem aos clientes
            def send_message(host, server_client_port, mensagem_a_ser_enviada):
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as enviar:
                    enviar.sendto(mensagem_a_ser_enviada.to_bytes(), (host, server_client_port))

            while True:
                conn, addr = s.accept()
                with conn:
                    print(f"Conexão estabelecida com {addr}")
                    try:
                        message = Message.from_bytes(conn.recv(1024))

                        # Recebe os dados do cliente, como nome e deck, salva, além disso, verifica se já pode começar
                        # uma partida
                        if message.message_type == Message.PLAYER_DATA:
                            print("DADOS DO JOGADOR RECEBIDOS, JOGADOR : ", {message.data['player_name']},
                                  {message.data['deck']})

                            response = Message(Message.PLAYER_DATA, "Player data received")
                            conn.sendall(response.to_bytes())

                            # Salva o dado dos jogadores conectados
                            self.players_data.append(message.data)

                            # self.game_data.add_player({message.data['player_name']}, {message.data['deck']}, addr)

                            # Verifica se o número de jogadores é 3
                            if self.num_players == 3:
                                # Envia a mensagem para todas as portas para iniciar o jogo
                                for port in self.porta_enviar_cliente:
                                    start_game_message = Message(Message.START_GAME, "O jogo está começando!")
                                    send_message(addr[0], port, start_game_message)

                        # Recebe a porta para poder enviar mensagens ao cliente
                        elif message.message_type == Message.CLIENT_PORT:

                            # Atualiza a porta do cliente
                            self.porta_enviar_cliente.append(message.data['player_port'])
                            nome = message.data['nome_jogador']

                            self.players_name.append(nome)

                            # Envia a mensagem para todas as portas que um novo jogador entrou
                            for port in self.porta_enviar_cliente:
                                # Cria a mensagem com o nome do novo jogador e a lista de jogadores conectados
                                message = Message(Message.NEW_PLAYER, {"Nome": nome, "Jogadores": self.players_name})
                                send_message(addr[0], port, message)

                        # Desconecta um cliente e envia para todos os outros
                        elif message.message_type == Message.DISCONNECT:
                            response = Message(Message.DISCONNECT, "Disconnect")
                            conn.sendall(response.to_bytes())
                            print(f"Desconexão com {addr}")
                            self.disconnect(addr)

                            # Envia mensagem de desconexão para todos os clientes

                            for port in self.porta_enviar_cliente:
                                message_disconnect = Message(Message.DISCONNECT, "A user has disconnected.")
                                send_message(addr[0], port, message_disconnect)

                        # Começa de fato, o jogo
                        elif message.message_type == Message.START_GAME:
                            self.start_game()

                        else:
                            response = Message(Message.TYPO_ERROR, "Unknown message type " + str(message.message_type))
                            conn.sendall(response.to_bytes())
                            print(f"Erro de mensagem com {addr}, conexão recusada, com erro {response.data}")
                    except Exception as e:
                        print(f"Erro ao processar mensagem de {addr}: {e}")

    def get_available_port(self):
        with self.lock:
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                if port not in self.porta_receber_cliente.values():
                    return port
        return None

    def disconnect(self, addr):
        with self.lock:
            if addr in self.porta_receber_cliente:
                port = self.porta_receber_cliente[addr]
                del self.porta_receber_cliente[addr]
                print(f"Cliente {addr} desconectado da porta {port}")


    # PRECISA ARRUMAR
    def start_game(self):
        for addr in self.porta_receber_cliente:
            start_game_message = Message(Message.START_GAME, self.game_data.compact(addr))
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as udp_socket:
                    udp_socket.sendto(start_game_message.to_bytes(), addr)
            except Exception as e:
                print(f"Erro ao enviar mensagem de início de jogo para {addr}: {e}")


if __name__ == '__main__':
    server = Server()
    server.start()
