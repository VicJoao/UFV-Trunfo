import tkinter as tk
from tkinter import messagebox
import threading
import socket
import pickle


class Message:
    HANDSHAKE = 1
    CONNECT = 2
    PLAYER_DATA = 3
    DISCONNECT = 4
    TYPO_ERROR = 5

    def __init__(self, message_type, data):
        self.message_type = message_type
        self.data = data

    def to_bytes(self):
        data_bytes = pickle.dumps(self.data)
        length = len(data_bytes)
        return self.message_type.to_bytes(1, byteorder='big') + length.to_bytes(4, byteorder='big') + data_bytes

    @classmethod
    def from_bytes(cls, byte_data):
        message_type = byte_data[0]
        length = int.from_bytes(byte_data[1:5], byteorder='big')
        data = pickle.loads(byte_data[5:])
        return cls(message_type, data)


# Defina as portas globalmente
DISCOVERY_PORT = 4242
COMM_PORT = None


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

        self.connect_button = tk.Button(self.frame, text="Conectar ao Servidor", command=self.connect_to_server)
        self.connect_button.pack(pady=5)
        self.connect_button.config(state=tk.DISABLED)

        self.nome_jogador = ""
        self.deck = None

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
        ips = self.get_local_ips()
        threads = []

        for ip in ips:
            if not self.is_scanning:
                break
            thread = threading.Thread(target=self.check_discovery_port, args=(ip, DISCOVERY_PORT))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()  # Aguarda todas as threads terminarem

    def get_local_ips(self):
        local_ips = []

        # Obtém o IP local real da interface de rede
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(0)
        try:
            # Conecta a um endereço remoto para descobrir o IP local
            s.connect(('8.8.8.8', 1))
            local_ip = s.getsockname()[0]
        except Exception:
            local_ip = '127.0.0.1'
        finally:
            s.close()

        # Extrai a base do IP (três primeiros octetos)
        base_ip = '.'.join(local_ip.split('.')[:-1])

        # Gera os IPs na mesma sub-rede
        for i in range(1, 255):
            local_ips.append(f"{base_ip}.{i}")

        print(local_ips)
        return local_ips

    def check_discovery_port(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                s.settimeout(1)  # Reduza o tempo limite
                s.sendto(Message(Message.HANDSHAKE, {}).to_bytes(), (host, port))
                data, addr = s.recvfrom(1024)
                message = Message.from_bytes(data)
                if message.message_type == Message.HANDSHAKE:
                    server_name = message.data
                    self.servers[addr[0]] = server_name
                    self.update_server_list(server_name)
                else:
                    print(f"Resposta inesperada do servidor {addr[0]}: {message.data}")
        except Exception as e:
            # Apenas exibe erro se o problema não for relacionado ao timeout
            if 'timed out' not in str(e):
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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                s.settimeout(1)
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
                s.sendall(
                    Message(Message.PLAYER_DATA, {'player_name': self.nome_jogador, 'deck': self.deck}).to_bytes())
                data = s.recv(1024)
                print(self.deck)
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
        # Código para iniciar o jogo pode ser adicionado aqui


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerScanner(root)
    root.mainloop()
