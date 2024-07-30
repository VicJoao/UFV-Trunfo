import socket
import threading

clients = {}  # Armazena o socket do cliente e seu nome

def handle_client(client_socket):
    print("Cliente conectado")

    # Receber o nome do cliente
    client_socket.send("Qual seu nome?".encode('utf-8'))
    name = client_socket.recv(1024).decode('utf-8')
    clients[client_socket] = name

    print(f"{name} entrou no chat")

    try:
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                print(f"{name} desconectado")
                break

            print(f"Recebido de {name}: {message}")
            # Encaminhar a mensagem para todos os clientes conectados
            for client, client_name in clients.items():
                if client != client_socket:
                    try:
                        client.send(f"{name}: {message}".encode('utf-8'))
                    except Exception as e:
                        print(f"Erro ao enviar mensagem para o cliente: {e}")
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        client_socket.close()
        del clients[client_socket]  # Remove o cliente da lista

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 5003))
    server.listen(5)
    print("Servidor iniciado e aguardando conexões...")

    while True:
        client_socket, addr = server.accept()
        print(f"Conexão de {addr}")
        client_handler = threading.Thread(target=handle_client, args=(client_socket,))
        client_handler.start()

if __name__ == "__main__":
    main()
