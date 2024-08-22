import Pyro5.api
import random
import threading
import time
import os

from models.game_data import GameData
from models.message import Message

MAX_CLIENTS = 3
COMM_PORT_START = 4243
COMM_PORT_END = COMM_PORT_START + MAX_CLIENTS
MAX_CLIENTS_PER_PORT = 1

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
        self.game_data = GameData()
        self.server_connection_message = []
        self.atributo_da_rodada = ''
        self.jogadas_de_atributo = 0
        print("Servidor de descoberta iniciado")
        self.messages = []

    def start(self):
        print(f"Servidor de descoberta iniciado")
        try:
            threading.Thread(target=self.handle_discovery, daemon=True).start()
            for port in range(COMM_PORT_START, COMM_PORT_END + 1):
                threading.Thread(target=self.comunicar_com_clientes, args=(port,), daemon=True).start()
                print("Servidor iniciado, Aguardando conexões na porta:", port)
            input("Pressione Enter para encerrar o servidor...")
        finally:
            print("Servidor fechado.")

    def handle_discovery(self):
        while True:
            # Placeholder: Implement discovery logic here if needed
            time.sleep(1)

    def comunicar_com_clientes(self, port):
        # Placeholder: Implement client communication logic here if needed
        pass

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
    ns.register("example.game_server", uri)  # Registra o servidor no Nameserver

    print(f"Server está rodando com URI: {uri}")

    # Mantém o daemon em execução para processar as requisições dos clientes
    daemon.requestLoop()

if __name__ == "__main__":
    main()
