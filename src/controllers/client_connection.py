import tkinter as tk
from tkinter import messagebox
import threading
import socket
import time
from server2.message import Message
from models.deck import Deck

class ServerScanner:
    def __init__(self, root):
        self.root = root
        self.is_scanning = False
        self.servers = {}
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)
        self.server_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.server_listbox.pack()
        self.start_button = tk.Button(self.frame, text="Iniciar Escaneamento", command=self.start_scanning)
        self.start_button.pack(pady=5)
        self.stop_button = tk.Button(self.frame, text="Parar Escaneamento", command=self.stop_scanning)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)
        self.nome_jogador = ""
        self.deck = None

        self.connect_button = tk.Button(self.frame, text="Conectar ao Servidor", command=self.connect_to_server)
        self.connect_button.pack(pady=5)
        self.connect_button.config(state=tk.DISABLED)

    def set_user_info(self, player_name, deck):
        self.nome_jogador = player_name
        self.deck = deck

    def start_scanning(self):
        self.is_scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.server_listbox.delete(0, tk.END)
        self.servers.clear()
        self.scan_thread = threading.Thread(target=self.scan_for_servers)
        self.scan_thread.start()

    def stop_scanning(self):
        self.is_scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def scan_for_servers(self):
        while self.is_scanning:
            for port in [4242]:
                self.check_port(port)
            time.sleep(5)

    def check_port(self, port):
        hosts = ['localhost']
        for host in hosts:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                try:
                    result = s.connect_ex((host, port))
                    if result == 0:
                        # Envia uma mensagem de HANDSHAKE
                        s.sendall(Message(Message.HANDSHAKE, {}).to_bytes())
                        s.settimeout(1)  # Redefine o timeout para o recebimento
                        name = s.recv(1024).decode('utf-8')
                        if not name:
                            name = f"{host}:{port}"
                        if host not in self.servers:
                            self.servers[host] = name
                            self.update_server_list(name)
                except socket.timeout:
                    pass  # Ignore timeout errors

    def update_server_list(self, server_name):
        self.server_listbox.insert(tk.END, server_name)
        self.connect_button.config(state=tk.NORMAL)

    def connect_to_server(self):
        selected_index = self.server_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Aviso", "Selecione um servidor para conectar.")
            return

        server_name = self.server_listbox.get(selected_index[0])
        host = next(key for key, value in self.servers.items() if value == server_name)
        port = 4242

        self.connect_to_host(host, port, self.nome_jogador, self.deck)

    def connect_to_host(self, host, port, player_name, deck: Deck):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                # Envia a mensagem HANDSHAKE
                handshake_message = Message(Message.HANDSHAKE, {})
                s.sendall(handshake_message.to_bytes())
                response = s.recv(1024).decode('utf-8')
                if "Hello from" in response:
                    # Envia a mensagem CONNECT
                    connect_message = Message(Message.CONNECT, {})
                    s.sendall(connect_message.to_bytes())
                    response = s.recv(1024).decode('utf-8')
                    print(response)
                    if "confirm." in response:
                        self.send_player(s, player_name, deck)
                    else:
                        #sempre vem pra ca
                        messagebox.showerror("Erro", "Resposta inesperada ao tentar conectar.")
                else:
                    messagebox.showerror("Erro", "Resposta inesperada do servidor.")
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor {host}:{port}. Erro: {e}")

    def send_player(self, conn, player_name, deck: Deck):
        try:
            player_ip = conn.getsockname()[0]


            player = {"name": player_name, "deck": deck, "ip": player_ip}
            message = Message(Message.PLAYERDATA, player)
            conn.sendall(message.to_bytes())
            print(f"Jogador {player_name} enviado para o servidor com sucesso!")
            print(f"Endereço IP do jogador: {player_ip}")
            print(f"Deck do jogador: {deck}")

            response = conn.recv(1024).decode('utf-8')
            messagebox.showinfo("Conexão", response)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar jogador para o servidor. Erro: {e}")

def main():
    root = tk.Tk()
    root.title("Cliente de Conexão de Servidor")
    app = ServerScanner(root)
    root.mainloop()

if __name__ == "__main__":
    main()
