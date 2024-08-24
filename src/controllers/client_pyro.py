import copy
import threading
import os
import random

import Pyro5.api

from PIL import ImageTk
import tkinter as tk
from tkinter import messagebox

from models.card import Card
from models.client_model import ClientModel
from models.game import Game

def transform_to_card_objects(hand_data):
    return [Card(**card) for card in hand_data]


@Pyro5.api.expose
class ServerScanner:
    def __init__(self, root):
        self.bd_id = None
        self.board = None
        self.scan_thread = None
        self.root = root
        self.is_scanning = False
        self.servers = {}  # Para armazenar serviços Pyro
        self.nome_jogador = ""
        self.deck = None
        self.game = None
        self.host = None
        self.players_list = []
        self.porta_de_escuta = None
        self.original_indices = []
        self.selected_card = None
        self.atributo_atual = ''
        self.server_proxy = None
        self.client_id = "client1"
        self.status_queue = []

        # Tkinter
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

        self.connect_client_to_daemon()

    # Funções do Tkinter
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
        self.scan_for_servers()

    def stop_scanning(self):
        self.is_scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def update_server_list(self, server_name):
        print(f"Adicionando servidor {server_name} à lista...")
        self.server_listbox.insert(tk.END, server_name)
        self.connect_button.config(state=tk.NORMAL)

    def update_status(self, message):
        self.server_listbox.delete(0, tk.END)
        self.server_listbox.insert(tk.END, message)
        return True

    def render_game_screen(self, attribute):
        my_hand = self.game.players_hands[self.game.my_id]['hand']
        print("Rendering game screen")
        print(f"Player hand: {my_hand}")

        my_hand = transform_to_card_objects(my_hand)

        # Destrua o frame existente, se existir
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            print("Destroying existing frame")
            self.frame.destroy()
        else:
            print("No existing frame to destroy")

        self.frame = tk.Frame(self.root)
        self.frame.pack(padx=10, pady=10)

        self.players_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.NORMAL)
        self.players_listbox.insert(tk.END, f"Você está conectado! {self.nome_jogador}")
        self.players_listbox.config(state=tk.DISABLED)

        self.players_label = tk.Label(self.frame, text=f"Escolha uma carta...")
        self.players_label.pack(pady=5)

        self.disconnect_button = tk.Button(self.frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)

        self.buttons = []
        self.images = []
        print([card.name for card in my_hand])
        for index, card in enumerate(my_hand):
            if card.name == 'Removed':
                continue
            card_img = card.gen_card_img()
            img = ImageTk.PhotoImage(card_img)
            self.images.append(img)

            button = tk.Button(self.frame, image=img, command=lambda i=index: self.handle_card_selection(i),
                               cursor='hand2')
            button.pack(side=tk.LEFT, padx=5, pady=5)  # Use pack for buttons
            self.buttons.append(button)

        self.root.geometry("600x400")
        self.root.title("Jogo")

        self.atributo_atual = attribute
        self.players_label.config(text=f"Aributo da rodada: {attribute}")

    def win_card(self):

        self.win_card_window = tk.Toplevel(self.root)
        self.win_card_window.title("Escolha uma Carta")
        self.win_card_window.attributes("-fullscreen", True)
        self.win_card_window.grab_set()

        self.win_card_frame = tk.Frame(self.win_card_window)
        self.win_card_frame.pack(expand=True, fill=tk.BOTH)

        pile = self.game.board.pile

        self.card_buttons = []
        self.card_images = []

        bottom_row_cols = 7
        top_row_cols = 8

        self.win_card_frame.grid_rowconfigure(0, weight=1)
        self.win_card_frame.grid_rowconfigure(1, weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(top_row_cols)), weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(bottom_row_cols)), weight=1)

        for index, card in enumerate(pile):
            card_img = card.gen_card_img()
            img = ImageTk.PhotoImage(card_img)
            self.card_images.append(img)

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

        self.win_card_frame.grid_rowconfigure(0, weight=1)
        self.win_card_frame.grid_rowconfigure(1, weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(top_row_cols)), weight=1)
        self.win_card_frame.grid_columnconfigure(tuple(range(bottom_row_cols)), weight=1)

        self.win_card_window.update_idletasks()

        self.win_card_window.after(100, self.check_selection)

    def reset_to_main_menu(self):
        if hasattr(self, 'frame') and self.frame.winfo_exists():
            self.frame.destroy()

        self.frame = tk.Frame(self.root)
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

        self.root.geometry("400x300")
        self.root.title("Menu Principal")

    '''
    Pyro5 API
    
    Funções:
    
    - connect_client_to_deamon: Conecta o cliente ao daemon Pyro5
    - atribute_user_id: Atribui o ID do usuário ao objeto
    - scan_for_servers: Escaneia os servidores disponíveis
    - connect_to_server: Conecta-se a um servidor
    - connect_to_host: Conecta-se ao host
    - start_countdown: Inicia a contagem regressiva para a conexão com o servidor
    - process_status_queue: Processa a fila de atualizações de status do cliente
    - finalize_connection: Finaliza a conexão com o servidor
    - set_server_proxy: Define o proxy do servidor
    - send_player_data: Envia os dados do jogador ao servidor
    - receive_game_data: Recebe os dados do jogo
    - handle_card_selection: Manipula a seleção de cartas
    - receive_round_results: Recebe os resultados da rodada
    - win_card: Exibe a tela de vitória
    - select_card: Seleciona a carta caso o jogador vença
    - end_game: Encerra o jogo
    - check_selection: Verifica a seleção do jogador
    - encerrar_partida: Encerra a partida
    - disconnect_from_server: Desconecta-se do servidor
    - stop_all_threads: Para todas as threads
    
    '''

    def connect_client_to_daemon(self):
        """Conecta o cliente ao daemon Pyro5."""

        daemon = Pyro5.api.Daemon()
        client_uri = daemon.register(self)
        print(f"URI do cliente: {client_uri}")
        name_server = Pyro5.api.locate_ns()
        self.client_id = random.randint(1, 1000)
        cliente_name_server = "Cliente" + str(self.client_id)
        name_server.register(cliente_name_server, client_uri)
        print("Cliente registrado no Name Server")

        def run_daemon():
            daemon.requestLoop()

        threading.Thread(target=run_daemon, daemon=True).start()

    def atribute_user_id(self, user_id):
        self.bd_id = user_id

    def scan_for_servers(self):
        """Utiliza o Name Server do Pyro para descobrir servidores."""
        try:
            with Pyro5.api.Proxy("PYRONAME:Pyro.NameServer") as ns:
                print("Escaneando servidores...")
                objects = ns.list()
                for name, uri in objects.items():
                    if name.startswith("Server"):
                        self.servers[name] = uri
                        server_name = name
                        self.root.after(0, lambda: self.update_server_list(server_name))
        except Exception as e:
            print(f"Erro ao escanear servidores: {e}")

    def connect_to_server(self):
        """Conecta-se ao servidor selecionado."""
        selected_index = self.server_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Aviso", "Selecione um servidor para conectar.")
            return

        server_name = self.server_listbox.get(selected_index[0])
        uri = self.servers.get(server_name)
        if uri:
            self.host = uri
            with Pyro5.api.Proxy(uri) as server_proxy:
                self.connect_to_host(server_proxy)

    def connect_to_host(self, server_proxy):
        """Inicia a conexão com o servidor."""
        self.start_countdown(0, server_proxy)

    def start_countdown(self, count, server_proxy):
        """Exibe uma contagem regressiva antes de conectar-se ao servidor."""
        if count > 0:
            self.update_status(f"Conectando ao servidor, aguarde {count} segundos...")
            self.root.after(1000, self.start_countdown, count - 1, server_proxy)
        else:
            # Use uma fila para garantir que o update_status seja chamado antes de finalize_connection
            self.status_queue.append(lambda: self.update_status("Conexão estabelecida!"))
            self.status_queue.append(lambda: self.finalize_connection(server_proxy))
            self.process_status_queue()

    def process_status_queue(self):
        """Processa a fila de atualizações de status."""
        if self.status_queue:
            action = self.status_queue.pop(0)
            action()
            self.root.after(100, self.process_status_queue)  # Agendando a próxima ação na fila

    def finalize_connection(self, server_proxy):
        """Finaliza a conexão com o servidor e realiza registro e comunicação inicial."""
        try:
            print("Conectando ao servidor...")

            print(f"Enviando ping")
            response = server_proxy.ping(self.nome_jogador, f"Cliente{self.client_id}")
            print(f"Resposta do servidor: {response}")
            if response == "pong":
                self.connected = True
                self.server_proxy = server_proxy  # Guardar a instância do proxy
                self.stop_scanning()
                self.show_game()
                self.send_player_data()
            else:
                self.update_status("Conexão falhou. Resposta inesperada do servidor.")
                self.connected = False
        except Exception as e:
            self.update_status(f"Erro durante a conexão: {e}")
            self.connected = False

    def set_server_proxy(self, server_proxy):
        """Define o proxy do servidor."""
        self.server_proxy = server_proxy

    def send_player_data(self):
        """Envia os dados do jogador ao servidor."""
        try:
            if not self.server_proxy:
                raise Exception("Não há proxy do servidor disponível.")
            player_data = {
                "Nome": self.nome_jogador,
                "Deck": self.deck,
                "pyroname": f"Cliente{self.client_id}",
            }
            self.server_proxy.send_player_data(player_data)
            print("Dados do jogador enviados com sucesso.")
        except Pyro5.errors.PyroError as e:
            print(f"Erro ao enviar dados do jogador: {e}")
        except Exception as e:
            print(f"Erro inesperado ao enviar dados: {e}")

    def receive_game_data(self, game_data, attribute):
        print(f"Dados do jogo recebidos: {game_data}")
        players_data = game_data["players_data"]
        player_id = game_data["player_id"]

        self.game = Game(players_data, player_id)

        self.original_indices = [(index, card) for index, card in enumerate(
            copy.deepcopy(self.game.players_hands[self.game.my_id]['hand']))]

        print(f"Original indices: {self.original_indices}")

        self.render_game_screen(attribute)

    def handle_card_selection(self, index):
        try:
            # Enviar a jogada ao servidor Pyro5
            self.server_proxy.play_card(index, self.game.my_id)
            for button in self.buttons:
                button.config(state=tk.DISABLED)
        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao enviar jogada para o servidor: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado ao escolher carta: {e}")

    def receive_round_results(self, round_results, turn_attribute, next_turn_attribute):
        print(f"Resultados da rodada recebidos: {round_results}")
        winner = self.game.play_turn(round_results, turn_attribute)

        if winner != -1:
            if winner == -2:
                pass
            else:
                print("Vencedor: ", winner)
            if self.game.my_id == winner:
                messagebox.showinfo("",
                                    "Você ganhou! Escolha uma carta para sua coleção:")
                self.win_card()
            elif winner == -2:
                messagebox.showinfo("",
                                    "Empate, ninguém ganha nada!")
                self.encerrar_partida()
            else:
                messagebox.showinfo("",
                                    "Infelizmente você perdeu!")
                self.encerrar_partida()
        else:
            self.render_game_screen(next_turn_attribute)

    def select_card(self, index):
        self.selected_card = self.game.board.pile[index]
        client_db = os.getenv("CLIENT_DB")
        banco_de_dados_cliente = ClientModel(client_db)
        banco_de_dados_cliente.create_card(self.selected_card.name, self.selected_card.intelligence,
                                           self.selected_card.charisma, self.selected_card.sport,
                                           self.selected_card.humor, self.selected_card.creativity,
                                           self.selected_card.appearance, self.bd_id)
        print(f"Card {index} selected and added to collection")




        self.win_card_window.destroy()

        print(f"Card {index} selected")
        messagebox.showinfo("Carta Adicionada",
                           f"A carta '{self.selected_card.name}' foi adicionada à coleção. Jogo encerrando...")
        self.server_proxy.end_game()
        self.end_game()

    def end_game(self):
        self.encerrar_partida()

    def check_selection(self):
        if self.selected_card is not None:
            self.end_game()
        else:
            # Continue checking until a card is selected
            self.root.after(100, self.check_selection)  # Check every 100ms

    def encerrar_partida(self):
        self.reset_to_main_menu()

    def disconnect_from_server(self):
        try:
            if self.server_proxy:
                self.server_proxy.disconnect_client(f"Cliente{self.client_id}")
                self.server_proxy = None
            self.reset_to_main_menu()
        except Pyro5.errors.PyroError as e:
            print(f"Erro ao desconectar do servidor: {e}")
        except Exception as e:
            print(f"Erro inesperado ao desconectar: {e}")

    def receive_disconnect(self):
        self.reset_to_main_menu()

if __name__ == "__main__":
    root = tk.Tk()
    app = ServerScanner(root)
    root.mainloop()
