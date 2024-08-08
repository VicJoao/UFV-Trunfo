import tkinter as tk
from tkinter import messagebox
import threading
import socket
import time
import pickle

# Defina as portas globalmente
DISCOVERY_PORT = 4242
COMM_PORT = None  # Inicialmente não definido

class Message:
    HANDSHAKE = 1
    CONNECT = 2
    PLAYERDATA = 3
    DISCONNECT = 4

    def __init__(self, message_type, data):
        self.message_type = message_type
        self.data = data

    def to_bytes(self):
        data_bytes = pickle.dumps(self.data)
        message_length = len(data_bytes)
        return self.message_type.to_bytes(1, byteorder='big') + message_length.to_bytes(4, byteorder='big') + data_bytes

    @staticmethod
    def from_bytes(message_bytes):
        message_type = message_bytes[0]
        message_length = int.from_bytes(message_bytes[1:5], byteorder='big')
        data_bytes = message_bytes[5:5 + message_length]
        data = pickle.loads(data_bytes)
        return Message(message_type, data)

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
            self.check_discovery_port(DISCOVERY_PORT)
            time.sleep(5)

    def check_discovery_port(self, port):
        hosts = ['localhost']
        for host in hosts:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                s.settimeout(1)
                try:
                    s.sendto(b"Discovery", (host, port))
                    s.settimeout(2)
                    try:
                        response, _ = s.recvfrom(1024)
                        response = response.decode('utf-8')
                        if response.startswith("Server Name:"):
                            name = response[len("Server Name:"):]
                            if host not in self.servers:
                                self.servers[host] = name
                                self.update_server_list(name)
                    except socket.timeout:
                        print(f"Timeout ao esperar resposta do servidor em {host}:{port}")
                except Exception as e:
                    print(f"Erro ao verificar porta de descoberta em {host}:{port}: {e}")

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
        global COMM_PORT
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, DISCOVERY_PORT))
                handshake_message = Message(Message.HANDSHAKE, {})
                s.sendall(handshake_message.to_bytes())
                response = s.recv(1024).decode('utf-8')
                if "Connected to port" in response:
                    COMM_PORT = int(response.split()[-1])
                    self.establish_connection(host)
                else:
                    messagebox.showerror("Erro", "Resposta inesperada ao tentar conectar.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor: {e}")

    def establish_connection(self, host):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, COMM_PORT))
                handshake_message = Message(Message.HANDSHAKE, {})
                s.sendall(handshake_message.to_bytes())
                response = s.recv(1024).decode('utf-8')
                messagebox.showinfo("Conectado", response)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao estabelecer conexão com o servidor: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerScanner(root)
    root.mainloop()
