from controllers.client_controller import ClientController

if __name__ == "__main__":
    host = "localhost"
    port = 12345
    name = "UsuárioTeste"
    app = ClientController(host, port, name)
    app.run()
