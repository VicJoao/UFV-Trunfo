import socket
import threading


class Client:
    def __init__(self, host='localhost', port=5000):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((host, port))
        print("Conectado ao servidor")
        self.running = True

        # Iniciar thread para receber mensagens do servidor
        self.receive_thread = threading.Thread(target=self.receive_messages)
        self.receive_thread.start()

    def send_message(self, message):
        self.client_socket.send(message.encode('utf-8'))
        response = self.client_socket.recv(4096).decode('utf-8')
        print(f"Resposta do servidor: {response}")

    def receive_messages(self):
        while self.running:
            try:
                response = self.client_socket.recv(4096).decode('utf-8')
                if response:
                    print(f"Recebido do servidor: {response}")
                else:
                    # Conexão fechada pelo servidor
                    print("O servidor encerrou a conexão.")
                    self.running = False
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                self.running = False

    def close(self):
        self.running = False
        self.client_socket.close()


def main():
    client = Client()

    while True:
        message = input("Digite uma mensagem para enviar ao servidor (ou 'sair' para encerrar): ")
        if message.lower() == 'sair':
            break
        client.send_message(message)

    client.close()


if __name__ == "__main__":
    main()
