import os
from dotenv import load_dotenv
import socket
import threading
from controllers.client_controller import ClientController  # Certifique-se de que o ClientController está no mesmo diretório ou no PYTHONPATH

# Carregar variáveis de ambiente
load_dotenv()
db_path = os.getenv("CLIENT_DB")

# Inicializar o ClientController com o caminho do banco de dados
app = ClientController(db_path)

def handle_client(client_socket):
    print("Cliente conectado")
    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print("Cliente desconectado")
                break

            print(f"Recebido do cliente: {message}")

            # Delegar a operação com o banco de dados para o ClientController
            response = app.process_message(message)

            print(f"Enviando para o cliente: {response}")
            client_socket.send(response.encode('utf-8'))
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client_socket.close()

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5000))
    server.listen(5)
    print("Servidor iniciado e aguardando conexões...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexão de {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()


if __name__ == "__main__":
    main()
