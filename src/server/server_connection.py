import socket
import threading
import pickle
from server2.message import Message

SERVER_NAME = "Server 1"

def receive_all(conn, length):
    """Recebe todos os dados da conexão até que o comprimento especificado seja atingido."""
    data = b''
    while len(data) < length:
        packet = conn.recv(length - len(data))
        if not packet:
            raise ConnectionError("Conexão fechada antes que todos os dados fossem recebidos")
        data += packet
    return data


def handle_client(conn):
    try:
        # Envia uma mensagem de boas-vindas ao cliente
        conn.sendall(f"Hello from {SERVER_NAME}".encode('utf-8'))

        # Recebe a mensagem completa (cabeçalho + dados)
        message_header = receive_all(conn, 5)
        message_length = int.from_bytes(message_header[1:5], byteorder='big')
        message_data = receive_all(conn, message_length)
        message = Message.from_bytes(message_header + message_data)

        if message.message_type == Message.HANDSHAKE:
            conn.sendall("Handshake recebido.".encode('utf-8'))
            print("Handshake recebido.")
        elif message.message_type == Message.CONNECT:
            conn.sendall("Conectado com sucesso.".encode('utf-8'))
            print("Cliente conectado.")
        elif message.message_type == Message.PLAYERDATA:
            player = message.data
            player_name = player.get("name")
            player_ip = player.get("ip")
            player_deck = player.get("deck")

            # Processa as informações recebidas
            print(f"Recebido jogador: {player_name}")
            print(f"Endereço IP do jogador: {player_ip}")
            print(f"Deck do jogador: {player_deck}")

            # Envia uma confirmação ao cliente
            conn.sendall(f"Jogador {player_name} recebido com sucesso!".encode('utf-8'))
        else:
            conn.sendall("Tipo de mensagem desconhecido.".encode('utf-8'))

    except pickle.PickleError as e:
        conn.sendall("Erro ao processar dados.".encode('utf-8'))
        print(f"Erro ao desserializar dados: {e}")
    except Exception as e:
        conn.sendall("Erro inesperado no servidor.".encode('utf-8'))
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
