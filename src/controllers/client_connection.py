import copy
import socket
import sys
import threading
import tkinter as tk
from tkinter import messagebox
import os

from models.client_model import ClientModel
from server2.game import Game
from server2.message import Message

# Defina as portas globalmente
DISCOVERY_PORT = 4242
COMM_PORT = None
LISTEN_PORT = 4255


# Escanear IPS
def get_local_ips():
    local_ips = []
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        s.connect(('8.8.8.8', 1))
        local_ip = s.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        s.close()

    base_ip = '.'.join(local_ip.split('.')[:-1])

    for i in range(1, 255):
        local_ips.append(f"{base_ip}.{i}")

    return local_ips


class ServerScanner:
    def __init__(self, root):
        self.bd_id = None
        self.board = None
        self.scan_thread = None
        self.root = root
        self.is_scanning = False
        self.servers = {}
        self.nome_jogador = ""
        self.deck = None
        self.listen_port = None
        self.game = None
        self.host = None
        self.players_list = []
        self.porta_de_escuta = None
        self.original_indices = []
        # Tkinter
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

        #self.players_label = tk.Label(self.frame, text="Jogadores conectados:")
        #self.players_label.pack(pady=5)

        self.players_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.DISABLED)

        self.disconnect_button = tk.Button(self.frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)
        self.disconnect_button.config(state=tk.DISABLED)

    def atribute_user_id(self, user_id):
        self.bd_id = user_id

    def get_random_free_port(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            self.porta_de_escuta = s.getsockname()[1]
        return self.porta_de_escuta

    def show_game(self):
        if self.frame and self.frame.winfo_exists():
            self.frame.destroy()

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.players_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.NORMAL)
        self.players_listbox.insert(tk.END, f"Você está conectado! {self.nome_jogador}")
        self.players_listbox.config(state=tk.DISABLED)

        self.players_label = tk.Label(self.frame, text="Aguardando jogadores...")
        self.players_label.pack(pady=5)

        self.disconnect_button = tk.Button(self.frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)

        self.root.geometry("400x400")
        self.root.title("Jogo")

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
        ips = get_local_ips()
        threads = []

        for ip in ips:
            if not self.is_scanning:
                break
            thread = threading.Thread(target=self.check_discovery_port, args=(ip, DISCOVERY_PORT))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()  # Aguarda todas as threads terminarem

    def check_discovery_port(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                s.settimeout(1)
                s.sendto(Message(Message.HANDSHAKE, {}).to_bytes(), (host, port))
                data, addr = s.recvfrom(4096)
                message = Message.from_bytes(data)
                if message.message_type == Message.HANDSHAKE:
                    server_name = message.data
                    self.servers[addr[0]] = server_name
                    self.root.after(0, lambda: self.update_server_list(server_name))
                else:
                    print(f"Resposta inesperada do servidor {addr[0]}: {message.data}")
        except Exception as e:
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
        self.host = host
        self.connect_to_host(host)

    def handle_server_messages(self, port):
        print("Iniciando a escuta de mensagens do servidor...")
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
            s.bind(('0.0.0.0', port))  # Bind na porta de comunicação

            print(f"Minha porta de escuta é {port}")
            print(self.servers)

            while True:
                try:
                    data, addr = s.recvfrom(4096)
                    message = Message.from_bytes(data)

                    if message.message_type == Message.NEW_PLAYER:
                        self.process_new_player_message(message)
                    elif message.message_type == Message.START_GAME:
                        players_data = message.data['players_data']  # Certifique-se de que isso é um dicionário ou
                        # lista de dicionários
                        player_id = message.data['player_id']

                        self.game = Game(players_data, player_id)
                        self.original_indices = [(index, card) for index, card in enumerate(
                            copy.deepcopy(self.game.players_hands[self.game.my_id]['hand']))]
                        self.render_game_screen()

                    elif message.message_type == Message.PLAY:
                        print("Jogadas recebidas dos 3 jogadores, turno começando...")
                        winner = self.game.play_turn(message.data['plays'], message.data['atribute'])
                        if winner != -1:
                            print(f"Vencedor: {winner}!")
                            if self.game.my_id == winner:
                               print("Você ganhou, selecione uma carta: ")
                               self.win_card()
                            elif winner == -2:
                                print(f"Empate, ninguém ganha nada!")
                            else:
                                print("Infelizmente você perdeu!")
                            print("Aguardando server encerrar partida...")
                            message = Message(Message.WINNER, {'winner': winner})
                            s.sendto(message.to_bytes(), (self.host, COMM_PORT))

                        else:
                            self.render_game_screen()


                    elif message.message_type == Message.WINNER:
                        # Disconnect from server
                        print("Fim de jogo, vencedor: ", message.data['winner'])
                        sys.exit(0)

                    else:
                        print("MENSAGEM NAO CONHECIDA")

                except socket.error as e:
                    print(f"Erro ao receber mensagem: {e}")
                    break

                except Exception as e:
                    print(f"Erro inesperado: {e}")
                    break

    def win_card(self):
        print("--------ESCOLHA UMA CARTA PARA GANHAR--------")
        for index, card in enumerate(self.game.board.pile):
            print(f"------> CARTA {index}")
            card.print_card()
        option = int(input("DIGITE O NUMERO DA CARTA DESEJADO:"))
        #Conecta ao BD e adiciona a carta a colecao do jogador
        selected_card = self.game.board.pile[option]
        client_db = os.getenv("CLIENT_DB")
        banco_de_dados_cliente = ClientModel(client_db)
        banco_de_dados_cliente.create_card(selected_card.name, selected_card.intelligence, selected_card.charisma, selected_card.sport, selected_card.humor, selected_card.creativity, selected_card.appearance, self.bd_id)

        return
    def process_new_player_message(self, message):

        print(f"Novo jogador entrou, bem vindo, {message.data['Nome']}")
        print(f"Jogadores conectados aguardando partida: {message.data['Jogadores']}")
        self.players_list = message.data['Jogadores']
        self.root.after(0, self.update_players_listbox)

    def update_players_listbox(self):
        self.players_listbox.config(state=tk.NORMAL)
        self.players_listbox.delete(0, tk.END)
        for player in self.players_list:
            self.players_listbox.insert(tk.END, player)
        self.players_listbox.config(state=tk.DISABLED)

    def connect_to_host(self, host):
        self.start_countdown(3, host)

    def start_countdown(self, count, host):
        if count > 0:
            self.update_status(f"Conectando servidor, aguarde {count} segundos...")
            self.root.after(1000, self.start_countdown, count - 1, host)
        else:
            self.update_status("Conexão estabelecida!")
            self.finalize_connection(host)

    def update_status(self, message):
        self.server_listbox.delete(0, tk.END)
        self.server_listbox.insert(tk.END, message)

    def finalize_connection(self, host):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP) as s:
                s.settimeout(1)
                s.sendto(Message(Message.CONNECT, {}).to_bytes(), (host, DISCOVERY_PORT))
                data, addr = s.recvfrom(4096)
                message = Message.from_bytes(data)
                if message.message_type == Message.CONNECT:
                    global COMM_PORT
                    COMM_PORT = message.data
                    print(f"Conectado ao servidor {host} na porta {COMM_PORT}")

                    self.get_random_free_port()

                    threading.Thread(target=self.handle_server_messages, args=(self.porta_de_escuta,),
                                     daemon=True).start()

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
                    Message(Message.PLAYER_DATA, {'player_name': self.nome_jogador, 'deck': self.deck,
                                                  'player_port': self.porta_de_escuta}).to_bytes())
                data = s.recv(4096)
                message = Message.from_bytes(data)
                if message.message_type == Message.PLAYER_DATA:
                    self.show_game()
                else:
                    messagebox.showerror("Erro", f"Resposta inesperada do servidor {host}: {message.data}")

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados para o servidor {host}: {e}")

    def disconnect_from_server(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect(('localhost', COMM_PORT))
                s.sendall(Message(Message.DISCONNECT, {}).to_bytes())
                print("Desconectado do servidor.")
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao desconectar do servidor: {e}")

    def render_game_screen(self):
        # Acessa a lista de cartas usando a chave 'hand'
        my_hand = self.game.players_hands[self.game.my_id]['hand']

        # Exibe as cartas e seus índices originais
        for index, card in self.original_indices:
            # Verifica se a carta original está na mão do jogador
            if card in my_hand:
                print("_____________________________")
                print(f"------> SELECIONE: {index}")
                card.print_card()  # Chama o método para imprimir informações detalhadas da carta
        option = int(input("DIGITE A OPÇÃO DESEJADA:"))

        self.send_play(option, self.game.my_id)

    def send_play(self, option, id):
        print("____________________________")
        print("O MEU ID É: ", id)
        print("____________________________")
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, COMM_PORT))
                s.sendall(
                    Message(Message.PLAY, {'opcao': option, 'player_id': id}).to_bytes())

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados para o servidor {self.host}: {e}")

    def render_round_winner(self):
        # render round winner on screen for 3 seconds and all 3 played cards
        pass

    def stop_all_threads(self):
        # Implementar a lógica para parar todas as threads
        self.is_scanning = False  # Parar a varredura se estiver em andamento
        if self.scan_thread:
            self.scan_thread.join()  # Aguardar a thread de escaneamento parar
        # Adicione lógica adicional aqui para parar outras threads, se necessário


if __name__ == "__main__":
    root = tk.Tk()
    app = ServerScanner(root)
    root.mainloop()
