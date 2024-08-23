import Pyro5.api
from server_classes import Server

def main():
    daemon = Pyro5.api.Daemon()
    server = Server()
    uri = daemon.register(server)
    name_server = Pyro5.api.Proxy("PYRONAME:Pyro.NameServer")
    name_server.register("Servidor", uri)

    print(f"Servidor pronto. URI: {uri}")
    daemon.requestLoop()

if __name__ == "__main__":
    main()
