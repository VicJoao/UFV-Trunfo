import tkinter as tk
from tkinter import messagebox
import threading
import socket
import time
from server2.message import Message

# Defina as portas globalmente
CLI_PORT = 4096
DISCOVERY_PORT = 4242
COMM_PORT = None


class ServerScanner:
    def __init__(self, root):
        self.user_list=[]
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
            self.check_discovery_port(DISCOVERY_PORT)
            time.sleep(5)

    def check_discovery_port(self, port):
        hosts = ['localhost']
        for host in hosts:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                    s.settimeout(5)
                    s.sendto(Message(Message.HANDSHAKE, {}).to_bytes(), (host, port))
                    data, addr = s.recvfrom(1024)
                    message = Message.from_bytes(data)
                    if message.message_type == Message.HANDSHAKE:
                        server_name = message.data
                        self.servers[host] = server_name
                        self.update_server_list(server_name)
                    else:
                        print(f"Resposta inesperada do servidor {host}: {message.data}")
            except Exception as e:
                print(f"Erro ao escanear servidor {host}: {e}")

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
        self.connect_to_host(host)

    def connect_to_host(self, host):
        #conecta a porta Discovery enviando a mensagem de CONNECT recebe resposta com a porta de comunicação do tipo CONNECT
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                s.settimeout(5)
                s.sendto(Message(Message.CONNECT, {}).to_bytes(), (host, DISCOVERY_PORT))
                data, addr = s.recvfrom(1024)
                message = Message.from_bytes(data)
                if message.message_type == Message.CONNECT:
                    global COMM_PORT
                    COMM_PORT = message.data
                    print(f"Conectado ao servidor {host} na porta {COMM_PORT}")
                    self.stop_scanning()
                    self.send_player_data(host)
                else:
                    messagebox.showerror("Erro", f"Resposta inesperada do servidor {host}: {message.data}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor {host}: {e}")

    def send_player_data(self, host):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, COMM_PORT))
                s.sendall(Message(Message.PLAYER_DATA, {'player_name': self.nome_jogador, 'deck': self.deck}).to_bytes())
                data = s.recv(1024)
                message = Message.from_bytes(data)
                if message.message_type == Message.PLAYER_DATA:
                    print(f"Data recebida do servidor {host}: {message.data}")
                    self.show_game()
                else:
                    messagebox.showerror("Erro", f"Resposta inesperada do servidor {host}: {message.data}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados para o servidor {host}: {e}")

    def show_game(self):
        self.frame.destroy()
        print("Iniciando jogo...")
        pass


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerScanner(root)
    root.mainloop()
