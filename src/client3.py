import tkinter as tk
import socket
import threading

class ClientApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PAULA CHAT")

        # Criação dos elementos da interface gráfica
        self.text_area = tk.Text(root, height=15, width=50)
        self.text_area.pack()

        self.entry = tk.Entry(root, width=50)
        self.entry.pack()

        self.send_button = tk.Button(root, text="Enviar", command=self.send_message)
        self.send_button.pack()

        # Configuração do cliente de socket
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(('localhost', 5001))

        # Perguntar o nome do cliente
        self.name = tk.simpledialog.askstring("Nome", "Qual seu nome?")
        self.client.send(self.name.encode('utf-8'))

        self.receive_thread = threading.Thread(target=self.receive_message)
        self.receive_thread.start()

    def send_message(self):
        message = self.entry.get()
        self.client.send(message.encode('utf-8'))
        self.entry.delete(0, tk.END)

    def receive_message(self):
        while True:
            try:
                response = self.client.recv(4096).decode('utf-8')
                self.text_area.insert(tk.END, f"{response}\n")
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                break

def main():
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()

if __name__ == "__main__":
    import tkinter.simpledialog  # Import necessário para usar o simpledialog
    main()
