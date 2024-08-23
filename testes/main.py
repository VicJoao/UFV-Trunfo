import Pyro5.api
from client import Client  # Importa a classe Client do módulo client

def main(server_uri):
    with Pyro5.api.Proxy(server_uri) as server_proxy:
        client = Client()
        server_proxy.register_client(client)
        print("Cliente registrado no servidor.")
        # Manter o cliente ativo para receber mensagens
        input("Pressione Enter para finalizar o cliente...")

if __name__ == "__main__":
    server_uri = "PYRONAME:Servidor"  # URI do servidor

    # Inicia 3 clientes conectando ao mesmo servidor
    for _ in range(3):
        main(server_uri)
