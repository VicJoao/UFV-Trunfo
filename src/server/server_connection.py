import socket
import threading

SERVER_NAME = "Server01"

def handle_client(conn):
    try:
        # Envia uma mensagem de boas-vindas ao cliente
        conn.sendall(f"Bem-vindo ao {SERVER_NAME}!".encode('utf-8'))
        msg = conn.recv(1024).decode('utf-8')
        if msg == "CONNECT":
            conn.sendall(f"Conectado com sucesso ao {SERVER_NAME}!".encode('utf-8'))
            print(f"Cliente conectado com sucesso!")
        else:
            conn.sendall("Comando inválido. Conexão encerrada.".encode('utf-8'))
    except Exception as e:
        print(f"Erro: {e}")
    finally:
        conn.close()

def main():
    print("Server is starting...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 4242))
        s.listen()
        print("Server is listening for connections...")
        while True:
            conn, addr = s.accept()
            thread = threading.Thread(target=handle_client, args=(conn,))
            thread.start()

if __name__ == "__main__":
    main()
