import copy
import threading
import time
import tkinter as tk
from tkinter import messagebox
import os

import psutil
from PIL import ImageTk

import Pyro5.api


from models.client_model import ClientModel
from models.game import Game
from models.message import Message



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

        # Tkinter
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)

        self.server_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.server_listbox.pack()

        self.start_button = tk.Button(self.frame, text="Iniciar Conexão", command=self.start_scanning)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(self.frame, text="Parar Conexão", command=self.stop_scanning)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)

        self.connect_button = tk.Button(self.frame, text="Conectar ao Servidor", command=self.connect_to_server)
        self.connect_button.pack(pady=5)
        self.connect_button.config(state=tk.DISABLED)

        self.players_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.players_listbox.pack()
        self.players_listbox.config(state=tk.DISABLED)

        self.disconnect_button = tk.Button(self.frame, text="Desconectar", command=self.disconnect_from_server)
        self.disconnect_button.pack(pady=5)
        self.disconnect_button.config(state=tk.DISABLED)

    def atribute_user_id(self, user_id):
        self.bd_id = user_id

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

    def scan_for_servers(self):
        # Utiliza o Name Server do Pyro para descobrir servidores
        try:
            with Pyro5.api.Proxy("PYRONAME:Pyro.NameServer") as ns:
                # Recupera todos os objetos registrados
                print("Escaneando servidores...")
                objects = ns.list()
                print(f"Objetos encontrados: {objects}")
                for name, uri in objects.items():
                    print(f"Verificando objeto {name}...")
                    if not self.is_scanning:
                        break
                    # Adiciona os servidores encontrados à lista
                    print(f"Adicionando servidor {name} à lista...")
                    self.servers[name] = uri
                    self.root.after(0, lambda: self.update_server_list(name))
        except Exception as e:
            print(f"Erro ao escanear servidores: {e}")

    def update_server_list(self, server_name):
        self.server_listbox.insert(tk.END, server_name)
        self.connect_button.config(state=tk.NORMAL)

    def connect_to_server(self):
        selected_index = self.server_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Aviso", "Selecione um servidor para conectar.")
            return

        server_name = self.server_listbox.get(selected_index[0])
        uri = self.servers.get(server_name)
        if uri:
            self.host = uri
            with Pyro5.api.Proxy(uri) as server_proxy:
                self.handle_server_messages(server_proxy)

    def handle_server_messages(self, server_proxy):
        print("Iniciando a escuta de mensagens do servidor...")
        while True:
            try:
                # Chama métodos no servidor Pyro5 para obter atualizações
                message = server_proxy.get_message()  # Supondo que o servidor tenha um método `get_message`

                if message.message_type == Message.NEW_PLAYER:
                    self.process_new_player_message(message)
                elif message.message_type == Message.START_GAME:
                    players_data = message.data['players_data']
                    player_id = message.data['player_id']
                    self.game = Game(players_data, player_id)
                    self.original_indices = [(index, card) for index, card in enumerate(
                        copy.deepcopy(self.game.players_hands[self.game.my_id]['hand']))]
                    self.render_game_screen()
                elif message.message_type == Message.PLAY:
                    winner = self.game.play_turn(message.data['plays'], message.data['atribute'])
                    if winner != -1:
                        if winner == -2:
                            pass
                        else:
                            print("Vencedor: ", winner)
                        if self.game.my_id == winner:
                            messagebox.showinfo("", "Você ganhou! Escolha uma carta para sua coleção:")
                            self.win_card()
                        elif winner == -2:
                            messagebox.showinfo("", "Empate, ninguém ganha nada!")
                            self.encerrar_partida()
                        else:
                            messagebox.showinfo("", "Infelizmente você perdeu!")
                elif message.message_type == Message.WINNER:
                    os._exit(0)
                elif message.message_type == Message.ATRIBUTO:
                    atributo_ingles = message.data["atribute"]
                    atributo_dict = {
                        "intelligence": "Inteligência",
                        "charisma": "Carisma",
                        "sport": "Esporte",
                        "humor": "Humor",
                        "creativity": "Criatividade",
                        "appearance": "Aparência"
                    }
                    self.atributo_atual = atributo_dict.get(atributo_ingles, "Desconhecido")
                    time.sleep(1)
                    messagebox.showinfo("", f"Atributo da rodada: {self.atributo_atual}")
                else:
                    print("MENSAGEM NAO CONHECIDA")
            except Exception as e:
                print(f"Erro inesperado: {e}")
                break

    def win_card(self):
        print("--------ESCOLHA UMA CARTA PARA GANHAR--------")

        # Create a new top-level window
        self.win_card_window = tk.Toplevel(self.root)
        self.win_card_window.title("Escolha uma Carta")
        self.win_card_window.attributes("-fullscreen", True)
        self.win_card_window.grab_set()  # Make the new window modal

        # Create a frame for winning card selection within the new window
        self.win_card_frame = tk.Frame(self.win_card_window)
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

        # Ensure the window has been fully rendered
        self.win_card_window.update_idletasks()
        print("Window title set to 'Escolha uma Carta'")

        # Wait for card selection before proceeding
        self.win_card_window.after(100, self.check_selection)

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
        if not self.server_proxy:
            messagebox.showerror("Erro", "Não há conexão com o servidor.")
            return

        try:
            # Chama o método remoto para encerrar a partida
            self.server_proxy.end_game()
            print("Partida encerrada com sucesso.")
        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao comunicar com o servidor: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

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
            self.update_status(f"Conectando ao servidor, aguarde {count} segundos...")
            self.root.after(1000, self.start_countdown, count - 1, host)
        else:
            self.update_status("Conexão estabelecida!")
            self.finalize_connection(host)

    def update_status(self, message):
        self.server_listbox.delete(0, tk.END)
        self.server_listbox.insert(tk.END, message)

    def finalize_connection(self, host):
        try:
            # Conectar-se ao servidor Pyro5
            server_uri = f"PYRO:example.server@{host}:12345"  # Substitua pelo URI real
            self.server_proxy = Pyro5.api.Proxy(server_uri)

            # Chamar método remoto para conectar e obter porta
            self.server_proxy.connect(self.nome_jogador, self.deck, self.porta_de_escuta)
            COMM_PORT = self.server_proxy.get_comm_port()
            print(f"Conectado ao servidor {host} na porta {COMM_PORT}")

            self.get_random_free_port()

            threading.Thread(target=self.handle_server_messages, args=(self.porta_de_escuta,), daemon=True).start()

            self.send_player_data()
        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao conectar ao servidor {host}: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def send_player_data(self):
        try:
            # Enviar dados do jogador ao servidor Pyro5
            self.server_proxy.send_player_data(self.nome_jogador, self.deck, self.porta_de_escuta)
            self.show_game()
        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao enviar dados para o servidor: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def disconnect_from_server(self):
        try:
            if self.server_proxy:
                self.server_proxy.disconnect()
                print("Desconectado do servidor.")
                self.root.destroy()
        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao desconectar do servidor: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def render_game_screen(self):
        try:
            # Chamar método remoto para obter dados da tela do jogo
            my_hand = self.server_proxy.get_game_data(self.nome_jogador)
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

        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao renderizar a tela do jogo: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

    def handle_card_selection(self, index):
        try:
            # Enviar a jogada ao servidor Pyro5
            self.server_proxy.play_card(index, self.game.my_id)
            # Disable all card buttons after a selection
            for button in self.buttons:
                button.config(state=tk.DISABLED)
        except Pyro5.errors.PyroError as e:
            messagebox.showerror("Erro", f"Erro ao enviar jogada para o servidor: {e}")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro inesperado: {e}")

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