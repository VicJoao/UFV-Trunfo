import os
from dotenv import load_dotenv
from controllers.client_controller import ClientController


def main():
    # Carregar variáveis de ambiente do arquivo .env
    load_dotenv()

    # Obter o caminho do banco de dados da variável de ambiente
    client_db = os.getenv("CLIENT_DB")

    # Inicializar e executar o gerenciador de cliente
    app = ClientController(client_db)
    app.root.mainloop()  # Inicia o loop principal do Tkinter


if __name__ == "__main__":
    main()
