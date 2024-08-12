import random
import socket
import threading
import time

from models.game_data import GameData
from models.message import Message
import os

# Define as portas e variáveis globais
MAX_CLIENTS = 3
DISCOVERY_PORT = 4242
COMM_PORT_START = 4243
COMM_PORT_END = COMM_PORT_START + MAX_CLIENTS
MAX_CLIENTS_PER_PORT = 1


def send_message(ip, server_client_port, mensagem_a_ser_enviada):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as enviar:
        enviar.sendto(mensagem_a_ser_enviada.to_bytes(), (ip, server_client_port))


def select_random_attribute():
    attributes = ["intelligence", "charisma", "sport", "humor", "creativity", "appearance"]
    return random.choice(attributes)


class Server:
    def __init__(self):
        self.porta_receber_cliente = {}  # Guarda a porta que os clientes usam para enviar
        self.porta_enviar_cliente = {}  # Mapeia o IP do cliente para a(s) porta(s) que deve(m) ser usada(s) para
        # enviar mensagens
        self.lock = threading.Lock()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind(('0.0.0.0', DISCOVERY_PORT))
        self.server_name = "Server UFV"
        self.num_players = 0
        self.jogadas_no_turno = 0
        self.plays = []
        self.players_name = []  # Lista com os nomes dos jogadores
        self.players_data = []  # Lista de dados dos jogadores
        print(f"Servidor de descoberta iniciado na porta {DISCOVERY_PORT}")
        self.game_data = GameData()
        self.server_connection_message = []
        self.atributo_da_rodada = ''
        self.jogadas_de_atributo = 0

    def start(self):
        try:
            threading.Thread(target=self.handle_discovery, daemon=True).start()
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                threading.Thread(target=self.comunicar_com_clientes, args=(port,), daemon=True).start()
                print("Servidor iniciado, Aguardando conexões na porta:", port)
            input("Pressione Enter para encerrar o servidor...")
        finally:
            self.server_socket.close()
            print("Servidor fechado e porta liberada.")

    # Thread usada para o server ficar escutando os clientes, na hora de conectar
    def handle_discovery(self):
        while True:
            data, addr = self.server_socket.recvfrom(1024)
            client_ip = addr[0]  # Extrai apenas o IP do cliente

            message = Message.from_bytes(data)
            if message.message_type == Message.HANDSHAKE:

                response = Message(Message.HANDSHAKE,
                                   self.server_name + "-" + str(self.num_players) + "/" + str(MAX_CLIENTS))
                self.server_socket.sendto(response.to_bytes(), addr)
                print(f"Handshake com {addr}")

            elif message.message_type == Message.CONNECT:
                port = self.get_available_port()
                if self.num_players < MAX_CLIENTS and port:
                    # Adiciona a entrada para o novo IP, sem sobrescrever IPs diferentes
                    self.porta_receber_cliente[client_ip] = port
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

            # Função para enviar mensagem aos clientes

            while True:
                conn, addr = s.accept()
                client_ip = addr[0]  # Extrai apenas o IP do cliente

                with conn:
                    print(f"Conexão estabelecida com {addr}")
                    try:
                        message = Message.from_bytes(conn.recv(1024))

                        # Recebe os dados do cliente, como nome e deck e porta, salva, além disso, verifica se já
                        # pode começar uma partida
                        if message.message_type == Message.PLAYER_DATA:
                            print("DADOS DO JOGADOR RECEBIDOS, JOGADOR : ", {message.data['player_name']},
                                  {message.data['deck']})

                            response = Message(Message.PLAYER_DATA, "Player data received")
                            conn.sendall(response.to_bytes())

                            # Salva o dado dos jogadores conectados
                            self.players_data.append(message.data)

                            # Se o IP já existe no dicionário, adiciona a nova porta à lista
                            if client_ip in self.porta_enviar_cliente:
                                self.porta_enviar_cliente[client_ip].append(message.data['player_port'])
                            else:
                                self.porta_enviar_cliente[client_ip] = [message.data['player_port']]

                            nome = message.data['player_name']
                            self.players_name.append(nome)

                            # Recebe a porta para poder enviar mensagens ao cliente
                            self.game_data.add_player(nome, message.data['deck'], message.data['player_port'])

                            # Envia a mensagem para todos os clientes que um novo jogador entrou
                            for client_ip, client_ports in self.porta_enviar_cliente.items():
                                # Cria a mensagem com o nome do novo jogador e a lista de jogadores conectados
                                message = Message(Message.NEW_PLAYER, {"Nome": nome, "Jogadores": self.players_name})
                                for client_port in client_ports:
                                    send_message(client_ip, client_port, message)

                            # Verifica se o número de jogadores é 3
                            if len(self.players_data) == 3:
                                self.start_game(self.porta_enviar_cliente)

                        elif message.message_type == Message.PLAY:
                            self.jogadas_no_turno += 1
                            # Recebendo dados
                            opcao = message.data["opcao"]
                            player_id = message.data["player_id"]

                            # Adicionando uma lista contendo id e opcao à lista plays
                            self.plays.append([player_id, opcao])

                            if self.jogadas_no_turno == 3:

                                # Envia a mensagem para todos os clientes que um novo jogador entrou
                                for client_ip, client_ports in self.porta_enviar_cliente.items():
                                    # Cria a mensagem com o nome do novo jogador e a lista de jogadores conectados
                                    message = Message(Message.PLAY,
                                                      {"plays": self.plays, "atribute": self.atributo_da_rodada})
                                    for client_port in client_ports:
                                        send_message(client_ip, client_port, message)

                                self.plays = []
                                self.jogadas_no_turno = 0
                            else:
                                continue

                        elif message.message_type == Message.WINNER:
                            for client_ip, client_ports in self.porta_enviar_cliente.items():
                                message_winner = Message(Message.WINNER, {})
                                for client_port in client_ports:
                                    time.sleep(2)
                                    send_message(client_ip, client_port, message_winner)

                            os._exit(0)


                        elif message.message_type == Message.ATRIBUTO:
                            self.jogadas_de_atributo += 1
                            if self.jogadas_de_atributo == 3:
                                self.atributo_da_rodada = select_random_attribute()
                                for client_ip, client_ports in self.porta_enviar_cliente.items():
                                    message_winner = Message(Message.ATRIBUTO, {"atribute": self.atributo_da_rodada})
                                    for client_port in client_ports:
                                        print(self.atributo_da_rodada)
                                        send_message(client_ip, client_port, message_winner)

                                self.jogadas_de_atributo = 0
                            else:
                                continue

                        elif message.message_type == Message.DISCONNECT:
                            response = Message(Message.DISCONNECT, "Disconnect")
                            conn.sendall(response.to_bytes())
                            print(f"Desconexão com {addr}")
                            self.disconnect(client_ip, message.data['player_port'])

                            # Envia mensagem de desconexão para todos os clientes
                            for client_ip, client_ports in self.porta_enviar_cliente.items():
                                message_disconnect = Message(Message.DISCONNECT, "A user has disconnected.")
                                for client_port in client_ports:
                                    send_message(client_ip, client_port, message_disconnect)

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

    def disconnect(self, client_ip, player_port):
        with self.lock:
            if client_ip in self.porta_receber_cliente:
                if player_port in self.porta_enviar_cliente.get(client_ip, []):
                    self.porta_enviar_cliente[client_ip].remove(player_port)
                    if not self.porta_enviar_cliente[client_ip]:  # Remove o IP se não tiver mais portas associadas
                        del self.porta_enviar_cliente[client_ip]
                    print(f"Cliente {client_ip}:{player_port} desconectado")

    def start_game(self, ips_e_portas):

        # Associaar aos jogadores

        # Envia a mensagem de início do jogo para todos os IPs e portas
        for client_ip, client_ports in ips_e_portas.items():
            for client_port in client_ports:
                # Cria a mensagem de início do jogo com dados compactados
                message_data_compact = Message(Message.START_GAME, self.game_data.compact(client_port))
                # Envia a mensagem compactada para o cliente
                send_message(client_ip, client_port, message_data_compact)
