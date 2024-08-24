import Pyro5.api

from server.pyro_server_connection import GameServer


def main():
    server = GameServer()

    daemon = Pyro5.api.Daemon()

    uri = daemon.register(server)

    ns = Pyro5.api.locate_ns()
    ns.register("Server", uri)

    print(f"Server está rodando com URI: {uri}")
    daemon.requestLoop()


if __name__ == "__main__":
    main()
