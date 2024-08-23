import Pyro5.api
import threading
import time
import random

from models.game_data import GameData
from models.message import Message


MAX_CLIENTS = 3

def select_random_attribute():
    attributes = ["intelligence", "charisma", "sport", "humor", "creativity", "appearance"]
    return random.choice(attributes)





@Pyro5.api.expose
class GameServer:
    def __init__(self):
        self.porta_receber_cliente = {}
        self.porta_enviar_cliente = {}
        self.lock = threading.Lock()
        self.server_name = "Server UFV"
        self.num_players = 0
        self.jogadas_no_turno = 0
        self.plays = []
        self.players_name = []
        self.players_data = []
        self.clients = []
        self.players_proxies = []
        self.clients = []
        self.game_data = GameData()
        self.server_connection_message = []
        self.atributo_da_rodada = ''
        self.jogadas_de_atributo = 0
        print("Servidor de descoberta iniciado")
        self.messages = []

    def ping(self):
        ns = Pyro5.api.locate_ns()
        clients = ns.list(prefix="Client")
        self.clients = clients.keys()
        print(f"Clientes conectados: {self.clients}")
        return "pong"


    def send_player_data(self, player_data):
        """Processa os dados do jogador recebidos do cliente."""
        print(f"Dados do jogador recebidos: {player_data}")

        self.send_message_to_clients(player_data["Nome"])

    def send_message_to_clients(self, message):
        print(f"Enviando mensagem para todos os clientes: {message}")
        """Envia uma mensagem para todos os clientes conectados."""

        for client in self.clients:
            try:
                print(f"Enviando mensagem para {client}")
                client_proxy = Pyro5.api.Proxy(f"PYRONAME:{client}")
                client_proxy.receive_player_name(message)
            except Pyro5.errors.PyroError as e:
                print(f"Erro ao enviar mensagem para o cliente: {e}")








    def handle_discovery(self):
        while True:
            # Placeholder: Implement discovery logic here if needed
            time.sleep(1)

    def comunicar_com_clientes(self, port):
        # Placeholder: Implement client communication logic here if needed
        pass

    

    def disconnect(self, client_ip, player_port):
        with self.lock:
            if client_ip in self.porta_receber_cliente:
                if player_port in self.porta_enviar_cliente.get(client_ip, []):
                    self.porta_enviar_cliente[client_ip].remove(player_port)
                    if not self.porta_enviar_cliente[client_ip]:
                        del self.porta_enviar_cliente[client_ip]
                    print(f"Cliente {client_ip}:{player_port} desconectado")

    def start_game(self, ips_e_portas):
        for client_ip, client_ports in ips_e_portas.items():
            for client_port in client_ports:
                message_data_compact = Message(Message.START_GAME, self.game_data.compact(client_port))
                self.send_message(client_ip, client_port, message_data_compact)

    def send_message(self, ip, port, mensagem_a_ser_enviada):
        with Pyro5.api.Proxy(f"PYRO:{ip}:{port}") as proxy:
            proxy.send_message(mensagem_a_ser_enviada.to_bytes())

    def get_message(self):
        if self.messages:
            return self.messages.pop(0)  # Retorna e remove a primeira mensagem
        return None  # Retorna None se não houver mensagens

    # Define outros métodos que você usaria para processar mensagens, similar aos métodos no código original


def main():
    # Cria uma instância do servidor
    server = GameServer()

    # Cria um Daemon Pyro
    daemon = Pyro5.api.Daemon()

    # Registra o servidor no daemon e obtém o URI
    uri = daemon.register(server)

    # (Opcional) Registra o servidor no Nameserver
    ns = Pyro5.api.locate_ns()  # Localiza o Nameserver
    ns.register("Server", uri)  # Registra o servidor no Nameserver

    print(f"Server está rodando com URI: {uri}")

    # Mantém o daemon em execução para processar as requisições dos clientes
    daemon.requestLoop()


if __name__ == "__main__":
    main()
