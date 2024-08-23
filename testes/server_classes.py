import Pyro5.api

@Pyro5.api.expose
class Client:
    def receive_message(self, message):
        """Recebe e processa mensagens do servidor."""
        print(f"Mensagem recebida do servidor: {message}")

@Pyro5.api.expose
class Server:
    def __init__(self):
        self.clients = []

    def register_client(self, client_proxy):
        """Registra o proxy do cliente."""
        if client_proxy not in self.clients:
            self.clients.append(client_proxy)
            print("Cliente registrado.")

    def send_message_to_all_clients(self, message):
        """Envia uma mensagem para todos os clientes registrados."""
        for client in self.clients:
            try:
                client.receive_message(message)
            except Pyro5.errors.PyroError as e:
                print(f"Erro ao enviar mensagem para o cliente: {e}")
