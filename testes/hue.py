import Pyro5.api
from server_classes import Client


def main():
    server_uri = "PYRONAME:Servidor"

    # Conecte-se ao servidor para obter o proxy do servidor
    with Pyro5.api.Proxy(server_uri) as server_proxy:
        # Cria e expõe a instância do cliente
        client = Client()
        client_uri = Pyro5.api.Daemon().register(client)  # Registra o cliente no daemon

        # Registra o proxy do cliente no servidor
        server_proxy.register_client(client_uri)

        # Aguarda mensagens do servidor
        print("Cliente registrado. Aguardando mensagens...")
        import time
        while True:
            time.sleep(1)  # Simula um cliente ativo


if __name__ == "__main__":
    main()
