import Pyro5.api
import threading
import time

@Pyro5.api.expose
class Server:
    def ping(self, message):
        """Recebe uma mensagem do cliente e responde com um ping."""
        print(f"Recebido do cliente: {message}")
        return "Mensagem recebida"

def send_message_to_client():
    while True:
        try:
            time.sleep(5)
            print("Enviando mensagem para o cliente...")
            client_proxy = Pyro5.api.Proxy("PYRONAME:Cliente")
            response = client_proxy.ping("Olá, cliente!")
            print(response)
        except Pyro5.errors.PyroError as e:
            print(f"Erro ao enviar mensagem para o cliente: {e}")

def main():
    global client_proxy
    daemon = Pyro5.api.Daemon()
    server = Server()
    uri = daemon.register(server)
    name_server = Pyro5.api.Proxy("PYRONAME:Pyro.NameServer")
    name_server.register("Servidor", uri)

    print(f"Servidor registrado no Name Server: {uri}")

    # Inicia uma thread para enviar mensagens ao cliente
    threading.Thread(target=send_message_to_client, daemon=True).start()

    print("Servidor pronto. Aguardando mensagens...")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
