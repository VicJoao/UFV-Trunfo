import socket
import threading
import tkinter as tk
from tkinter import messagebox

class Connection:
    def __init__(self):
        self.sock = None
        self.connected = False

    def connect(self, server_address: str, client_name: str):
        if self.sock:
            self.sock.close()

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(10.0)
        try:
            print(f"Tentando conectar ao servidor: {server_address}")
            self.sock.connect((server_address, 4242))
            self.sock.sendall(client_name.encode("utf8"))
            threading.Thread(target=self._listen_to_server, daemon=True).start()
            self.connected = True
            messagebox.showinfo("Info", "Connected to server.")
        except Exception as e:
            self.connected = False
            print(f"Erro na conexão: {e}")
            messagebox.showerror("Error", f"Failed to connect: {e}")

    def _listen_to_server(self):
        print("Starting to listen to server...")
        while self.connected:
            try:
                msg = self.sock.recv(1024)
                if msg:
                    print(f"Mensagem recebida do servidor: {msg.decode('utf8')}")
                    app.display_message(f"Server: {msg.decode('utf8')}")
                else:
                    print("Conexão fechada pelo servidor.")
                    self.connected = False
            except socket.timeout:
                print("Tempo de espera esgotado ao receber mensagem.")
                self.connected = False
            except Exception as e:
                print(f"Erro ao receber mensagem: {e}")
                self.connected = False

    def send_message(self, message: str):
        if self.connected and self.sock:
            try:
                self.sock.sendall(message.encode("utf8"))
            except Exception as e:
                print(f"Erro ao enviar mensagem: {e}")
                messagebox.showerror("Error", f"Failed to send message: {e}")

    def close(self):
        if self.sock:
            self.sock.close()
            self.connected = False


class ClientApp:
    def __init__(self, root, client_name: str):
        self.root = root
        self.client_name = client_name
        self.connection = Connection()

        self.root.title(f"Client - {client_name}")

        self.message_display = tk.Text(root, wrap=tk.WORD, state=tk.DISABLED, height=10)
        self.message_display.pack(pady=10)

        self.message_entry = tk.Entry(root, width=50)
        self.message_entry.pack(pady=5)

        self.send_button = tk.Button(root, text="Send", command=self.send_message)
        self.send_button.pack(pady=5)

        self.connect_button = tk.Button(root, text="Connect", command=self.connect_to_server)
        self.connect_button.pack(pady=5)

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def display_message(self, message: str):
        self.message_display.config(state=tk.NORMAL)
        self.message_display.insert(tk.END, message + "\n")
        self.message_display.config(state=tk.DISABLED)
        self.message_display.see(tk.END)  # Scroll to the bottom

    def connect_to_server(self):
        server_address = "127.0.0.1"  # Use the server's IP address here
        self.connection.connect(server_address, self.client_name)

    def send_message(self):
        message = self.message_entry.get()
        if message:
            self.connection.send_message(message)
            self.display_message(f"Me: {message}")
            self.message_entry.delete(0, tk.END)

    def on_closing(self):
        self.connection.close()
        self.root.destroy()


def main(client_name: str):
    global app
    root = tk.Tk()
    app = ClientApp(root, client_name)
    root.geometry("400x300")
    root.mainloop()


if __name__ == "__main__":
    import sys
    main(*sys.argv[1:])
