import copy
import socket
import threading
import time
import tkinter as tk
from tkinter import messagebox
import os

import psutil
from PIL import ImageTk

from models.client_model import ClientModel
from models.game import Game
from models.message import Message

import socket

# Defina as portas globalmente
DISCOVERY_PORT = 4242
COMM_PORT = None
LISTEN_PORT = 4255

# Escanear IPS
import ipaddress


def get_ip_and_netmask():
    for interface, addresses in psutil.net_if_addrs().items():
        for addr in addresses:
            if addr.family == socket.AF_INET and not addr.address.startswith("127."):
                return addr.address, addr.netmask
    return None, None


def get_local_ips():
    # Obter o IP e a máscara de sub-rede
    local_ip, netmask = get_ip_and_netmask()

    if local_ip and netmask:
        # Criar a rede IPv4 usando o IP e a máscara
        network = ipaddress.IPv4Network(f"{local_ip}/{netmask}", strict=False)

        print(f"Endereço IP local: {local_ip}")
        print(f"Máscara de sub-rede: {netmask}")
        print(f"IP da rede: {network.network_address}")
        print(f"IP de broadcast: {network.broadcast_address}")

        # Retornar uma lista com todos os IPs utilizáveis na faixa (exclui rede e broadcast)
        return [str(ip) for ip in network.hosts()]
    else:
        print("Não foi possível obter o endereço IP e a máscara de sub-rede.")
        return []


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
        self.selected_card = None
        self.atributo_atual = ''
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

        # self.players_label = tk.Label(self.frame, text="Jogadores conectados:")
        # self.players_label.pack(pady=5)

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
                        print("ADJOAJDAODADADD")
                        self.render_game_screen()

                    elif message.message_type == Message.PLAY:
                        print("Jogadas recebidas dos 3 jogadores, turno começando...")
                        winner = self.game.play_turn(message.data['plays'], message.data['atribute'])
                        if winner != -1:

                            if winner == -2:
                                pass
                            else:
                                print("Vencedor: ", winner)
                            if self.game.my_id == winner:
                                messagebox.showinfo("", "Você ganhou! Escolha uma carta para sua coleção:")  # Título vazio, mensagem principal dentro
                                self.win_card()


                            elif winner == -2:
                                messagebox.showinfo("",
                                                    "Empate, ninguém ganha nada!")  # Título vazio, mensagem
                                # principal dentro
                                self.encerrar_partida()
                            else:
                                messagebox.showinfo("",
                                                    "Infelizmente você perdeu!")  # Título vazio, mensagem principal
                                # dentro

                        else:
                            self.render_game_screen()


                    elif message.message_type == Message.WINNER:
                        os._exit(0)


                    elif message.message_type == Message.ATRIBUTO:

                        atributo_ingles = message.data["atribute"]
                        if atributo_ingles == "intelligence":
                            self.atributo_atual = "Inteligência"
                        elif atributo_ingles == "charisma":
                            self.atributo_atual = "Carisma"
                        elif atributo_ingles == "sport":
                            self.atributo_atual = "Esporte"
                        elif atributo_ingles == "humor":
                            self.atributo_atual = "Humor"
                        elif atributo_ingles == "creativity":
                            self.atributo_atual = "Criatividade"
                        elif atributo_ingles == "appearance":
                            self.atributo_atual = "Aparência"
                        time.sleep(1)
                        messagebox.showinfo("",
                                            f"Atributo da rodada: {self.atributo_atual}")  # Título vazio, mensagem



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

        # Destroy the existing frame if it exists
        if hasattr(self, 'win_card_frame') and self.win_card_frame.winfo_exists():
            print("Destroying existing win_card_frame")
            self.win_card_frame.destroy()
        else:
            print("No existing win_card_frame to destroy")

        # Create a new frame for winning card selection
        self.win_card_frame = tk.Frame(self.root)
        self.win_card_frame.pack(expand=True, fill=tk.BOTH)  # Expand the frame to fill the window
        print("New win_card_frame created and packed")

        # Access the pile of cards
        pile = self.game.board.pile

        # Create and pack buttons for each card in the pile
        self.card_buttons = []
        self.card_images = []

        print(f"Number of cards in pile: {len(pile)}")

        # Define the number of columns for each row
        bottom_row_cols = 7
        top_row_cols = 8

        # Configure grid rows and columns for the layout
        self.win_card_frame.grid_rowconfigure(0, weight=1)
        self.win_card_frame.grid_rowconfigure(1, weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(top_row_cols)), weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(bottom_row_cols)), weight=1)

        # Create buttons and place them in the grid
        for index, card in enumerate(pile):
            card_img = card.gen_card_img()
            img = ImageTk.PhotoImage(card_img)
            self.card_images.append(img)
            print(f"Card {index} image generated and added to card_images list")

            button = tk.Button(self.win_card_frame, image=img, command=lambda i=index: self.select_card(i),
                               cursor="hand2")
            if index < top_row_cols:
                row = 0  # Top row
                col = index  # Column index
            else:
                row = 1  # Bottom row
                col = index - top_row_cols  # Adjust column index for the bottom row

            button.grid(row=row, column=col, padx=5, pady=5, sticky="nsew")  # Use grid for button placement
            self.card_buttons.append(button)
            print(f"Button for card {index} created and placed in grid at row {row}, column {col}")

        # Adjust grid weights to ensure proper layout
        self.win_card_frame.grid_rowconfigure(0, weight=1)
        self.win_card_frame.grid_rowconfigure(1, weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(top_row_cols)), weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(bottom_row_cols)), weight=1)

        # Set the window to full screen
        self.root.attributes("-fullscreen", True)
        self.root.update_idletasks()  # Ensure the window has been fully rendered

        # Set the window title for the win card screen
        self.root.title("Escolha uma Carta")
        print("Window title set to 'Escolha uma Carta'")

        # Wait for card selection before proceeding
        self.root.after(100, self.check_selection)

    def select_card(self, index):
        self.selected_card = self.game.board.pile[index]
        client_db = os.getenv("CLIENT_DB")
        banco_de_dados_cliente = ClientModel(client_db)
        banco_de_dados_cliente.create_card(self.selected_card.name, self.selected_card.intelligence,
                                           self.selected_card.charisma, self.selected_card.sport,
                                           self.selected_card.humor, self.selected_card.creativity,
                                           self.selected_card.appearance, self.bd_id)
        print(f"Card {index} selected and added to collection")

        # Show a message box confirming that the card has been added
        messagebox.showinfo("Carta Adicionada", f"A carta '{self.selected_card.name}' foi adicionada à coleção. Jogo encerrando...")

        # Optionally, update the UI or clean up
        if hasattr(self, 'win_card_frame') and self.win_card_frame.winfo_exists():
            self.win_card_frame.destroy()
        print(f"Card {index} selected")

        # Now that a card is selected, call a method to proceed with ending the game
        self.end_game()

    def end_game(self):
        print("Ending the game...")
        self.encerrar_partida()

    def check_selection(self):
        if self.selected_card is not None:
            self.end_game()
        else:
            # Continue checking until a card is selected
            self.root.after(100, self.check_selection)  # Check every 100ms

    def encerrar_partida(self):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, COMM_PORT))
                s.sendall(
                    Message(Message.WINNER, {}).to_bytes())
        except Exception as e:
            messagebox.showerror("Erro",
                                 f"Erro ao enviar dados para o servidor {self.host}: {e}")

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
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((self.host, COMM_PORT))
                s.sendall(Message(Message.ATRIBUTO, {}).to_bytes())

        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados para o servidor {self.host}: {e}")

        # Access the list of cards using the key 'hand'
        my_hand = self.game.players_hands[self.game.my_id]['hand']
        print("Rendering game screen")
        print(f"Player hand: {my_hand}")

        # Destroy the existing frame if it exists
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            print("Destroying existing frame")
            self.frame.destroy()
        else:
            print("No existing frame to destroy")

        # Create a new frame
        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)
        print("New frame created and packed")

        # Create and pack the players listbox
        self.players_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.NORMAL)
        self.players_listbox.insert(tk.END, f"Você está conectado! {self.nome_jogador}")
        self.players_listbox.config(state=tk.DISABLED)
        print(f"Players listbox created and populated with: Você está conectado! {self.nome_jogador}")

        # Create and pack the players label
        self.players_label = tk.Label(self.frame, text=f"Escolha uma carta...")
        self.players_label.pack(pady=5)
        print("Players label created and packed")

        # Create and pack the disconnect button
        self.disconnect_button = tk.Button(self.frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)
        print("Disconnect button created and packed")

        # Add buttons with cards using pack
        self.buttons = []
        self.images = []
        print(f"Number of cards to display: {len(my_hand)}")

        for index, card in enumerate(my_hand):
            if card.name == "Removed":
                continue
            card_img = card.gen_card_img()
            img = ImageTk.PhotoImage(card_img)
            self.images.append(img)
            print(f"Card {index} image generated and added to images list")

            button = tk.Button(self.frame, image=img, command=lambda i=index: self.handle_card_selection(i),
                               cursor='hand2')
            button.pack(side=tk.LEFT, padx=5, pady=5)  # Use pack for buttons
            self.buttons.append(button)
            print(f"Button for card {index} created and packed")

        # Set the window size and title
        self.root.geometry("600x400")
        self.root.title("Jogo")
        print("Window size set to 600x400 and title set to 'Jogo'")

    def handle_card_selection(self, index):
        # Handle card selection
        self.send_play(index, self.game.my_id)
        # Disable all card buttons after a selection
        for button in self.buttons:
            button.config(state=tk.DISABLED)

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
