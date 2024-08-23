import Pyro5.api
import threading
import time

@Pyro5.api.expose
class Client:
    def ping(self, message):
        """Recebe uma mensagem do servidor e responde com um ping."""
        print(f"Recebido do servidor: {message}")
        return "Mensagem recebida"

def send_message_to_server():
    while True:
        try:
            time.sleep(5)
            print("Enviando mensagem para o servidor...")
            server_proxy = Pyro5.api.Proxy("PYRONAME:Servidor")
            response = server_proxy.ping("Olá, servidor!")
            print(response)
        except Pyro5.errors.PyroError as e:
            print(f"Erro ao enviar mensagem para o servidor: {e}")

def main():
    global server_proxy
    daemon = Pyro5.api.Daemon()
    client = Client()
    client_uri = daemon.register(client)
    print(f"URI do cliente: {client_uri}")

    # Registra o cliente no Name Server
    name_server = Pyro5.api.locate_ns()
    name_server.register("Cliente", client_uri)

    print("Cliente registrado no Name Server")

    # Inicia uma thread para enviar mensagens ao servidor
    threading.Thread(target=send_message_to_server, daemon=True).start()

    print("Cliente pronto. Aguardando mensagens...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
