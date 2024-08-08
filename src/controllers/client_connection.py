import tkinter as tk
from tkinter import messagebox
import threading
import socket
from server2.message import Message

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

        self.players_label = tk.Label(self.frame, text="Jogadores conectados:")
        self.players_label.pack(pady=5)

        self.players_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.DISABLED)

        self.disconnect_button = tk.Button(self.frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)
        self.disconnect_button.config(state=tk.DISABLED)

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
                message = Message.from_bytes(data)
                if message.message_type == Message.PLAYER_DATA:
                    print(f"Data recebida do servidor {host}: {message.data}")
                    self.show_game()
                else:
                    messagebox.showerror("Erro", f"Resposta inesperada do servidor {host}: {message.data}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados para o servidor {host}: {e}")

    def show_game(self):
        # Checa se a tela já foi destruída para evitar erros
        if self.frame.winfo_exists():
            self.frame.destroy()

        self.players_frame = tk.Frame(self.root)
        self.players_frame.pack(padx=10, pady=10)

        self.players_listbox = tk.Listbox(self.players_frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.NORMAL)
        self.players_listbox.insert(tk.END, self.nome_jogador)
        self.players_listbox.config(state=tk.DISABLED)

        self.players_label = tk.Label(self.players_frame, text="Jogadores conectados:")
        self.players_label.pack(pady=5)

        self.disconnect_button = tk.Button(self.players_frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)

        self.root.geometry("400x400")
        self.root.title("Jogo")

        # Cria um novo thread para escutar o servidor
        self.listen_thread = threading.Thread(target=self.listen_to_server)
        self.listen_thread.start()

    def listen_to_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('0.0.0.0', self.comm_port))
                s.listen(1)
                conn, addr = s.accept()
                with conn:
                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break
                        message = Message.from_bytes(data)
                        if message.message_type == Message.START_GAME:
                            self.start_game()
                        elif message.message_type == Message.NEW_PLAYER:
                            player_name = message.data
                            self.players_listbox.config(state=tk.NORMAL)
                            self.players_listbox.insert(tk.END, player_name)
                            self.players_listbox.config(state=tk.DISABLED)
                        elif message.message_type == Message.DISCONNECT:
                            messagebox.showinfo("Desconectado", "Você foi desconectado do servidor.")
                            self.root.destroy()
                        else:
                            print(f"Mensagem desconhecida recebida: {message.message_type}")
        except Exception as e:
            print(f"Erro ao escutar o servidor: {e}")

    def disconnect_from_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', COMM_PORT))
                s.sendall(Message(Message.DISCONNECT, {}).to_bytes())
                print("Desconectado do servidor.")
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao desconectar do servidor: {e}")

    def start_game(self):
        # Aqui você pode implementar a lógica para iniciar o jogo
        print("O jogo começou!")


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerScanner(root)
    root.mainloop()
