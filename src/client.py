from controllers.client_controller import ClientController
from controllers.card_controller import CardController
from PIL import Image

if __name__ == "__main__":
    host = "localhost"
    port = 12345
    name = "UsuárioTeste"
    app = ClientController(host, port, name)

    app.run()
