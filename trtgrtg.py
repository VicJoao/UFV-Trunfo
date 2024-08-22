import Pyro5.api

def hi_name_server():
    try:
        with Pyro5.api.Proxy("PYRONAME:Pyro.NameServer") as ns:
            objects = ns.list()
            print(f"Objetos registrados no Name Server: {objects}")
            if "example.game_server" not in objects:
                print("Nome 'example.game_server' não encontrado no Name Server.")
            else:
                print(f"Nome 'example.game_server' encontrado com URI {objects['example.game_server']}")
    except Exception as e:
        print(f"Erro ao conectar com o Name Server: {e}")

if __name__ == "__main__":
    hi_name_server()
