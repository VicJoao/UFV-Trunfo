import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

from PIL import ImageTk, Image

from models.client_model import ClientModel
from models.user import User
from controllers.pyro_client_connection import ClientConnection


def upload_image():
    file_path = filedialog.askopenfilename(
        title="Selecione uma imagem",
        filetypes=[("Image files", "*.jpg *.jpeg *.png")]
    )
    if file_path:
        # Abre a imagem
        img = Image.open(file_path)

        # Salva a imagem na pasta assets
        # @TODO: Seria interessante verificar se a pasta existe, bem como se alguma imagem com o mesmo nome já existe
        new_file_path = "assets/photos/" + file_path.split("/")[-1]
        img.save(new_file_path)

        return new_file_path

def get_card_attributes():
    while True:
        attributes = {}
        total = 0
        for attr in ["Inteligência", "Carisma", "Esporte", "Humor", "Criatividade", "Aparência"]:
            value = simpledialog.askinteger(
                "Atributo da Carta",
                f"Insira {attr} (0-10):\n\nSoma atual dos atributos: {total}/30",
                minvalue=0, maxvalue=10
            )

            # Verifica se o usuário clicou em "Cancelar" ou fechou a janela
            if value is None:
                return None

            attributes[attr] = value
            total += value

        # Verifica se a soma total está dentro do limite
        if total <= 30:
            # Verifica se o usuário deseja adicionar uma imagem à carta
            if messagebox.askyesno("Imagem", "Deseja adicionar uma imagem à carta?"):
                img_path = upload_image()
                attributes["Imagem"] = img_path

            else: attributes["Imagem"] = "assets/photos/default.jpg"

        else:
            messagebox.showerror("Erro",
                                 f"A soma dos atributos é {total}, mas deve ser no máximo 30. Por favor, insira os "
                                 f"valores novamente.")

        # print(f"Attributes: {attributes}")
        return [attributes[key] for key in
                ["Inteligência", "Carisma", "Esporte", "Humor", "Criatividade", "Aparência", "Imagem"]]

class ClientController:
    def __init__(self, banco_de_dados_do_cliente):

        # Tkinter
        self.exit_user_button = None
        self.create_user_button = None
        self.user_label = None
        self.exit_button = None
        self.select_user_button = None
        self.find_match_button = None
        self.edit_deck_button = None
        self.print_cards_button = None
        self.create_card_button = None
        self.label = None
        self.user_menu_frame = None
        self.menu_frame = None

        self.client_db = banco_de_dados_do_cliente
        self.user = None
        self.client_model = ClientModel(self.client_db)
        self.root = tk.Tk()

        self.root.title("Client Manager")

        # Inicializa o Scanner de Servidores
        self.server_scanner = ClientConnection(self.root, )
        self.server_scanner.frame.pack_forget()  # Oculta a tela de escaneamento por padrão

        self.create_widgets()
        self.load_user_menu()

    def create_widgets(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()

        self.user_menu_frame = tk.Frame(self.root)
        self.user_menu_frame.pack_forget()  # Inicialmente oculta o menu de usuário

        # Widgets do Menu Principal
        self.label = tk.Label(self.menu_frame, text="Select an option:")
        self.label.pack()

        self.create_card_button = tk.Button(self.menu_frame, text="Create new card", command=self.create_card_dialog)
        self.create_card_button.pack()

        self.print_cards_button = tk.Button(self.menu_frame, text="Print all cards", command=self.display_user_cards)
        self.print_cards_button.pack()

        self.edit_deck_button = tk.Button(self.menu_frame, text="Edit Deck", command=self.edit_deck_dialog)
        self.edit_deck_button.pack()

        self.find_match_button = tk.Button(self.menu_frame, text="Find Servers", command=self.show_server_scanner)
        self.find_match_button.pack()

        self.select_user_button = tk.Button(self.menu_frame, text="Select a User", command=self.load_user_menu)
        self.select_user_button.pack()

        self.exit_button = tk.Button(self.menu_frame, text="Exit", command=self.root.quit)
        self.exit_button.pack()

        # Widgets do Menu de Usuário
        self.user_label = tk.Label(self.user_menu_frame, text="Select the username you want to load:")
        self.user_label.pack()

        self.create_user_button = tk.Button(self.user_menu_frame, text="Create new user", command=self.create_user)
        self.create_user_button.pack()

        self.exit_user_button = tk.Button(self.user_menu_frame, text="Exit", command=self.root.quit)
        self.exit_user_button.pack()

    def show_server_scanner(self):
        self.menu_frame.pack_forget()
        self.server_scanner.frame.pack()
        self.server_scanner.start_scanning()  # Inicia o escaneamento de servidores

    def load_user_menu(self):
        self.menu_frame.pack_forget()
        self.user_menu_frame.pack()

        users = self.client_model.get_all_users()
        for widget in self.user_menu_frame.winfo_children():
            if widget not in [self.user_label, self.create_user_button, self.exit_user_button]:
                widget.destroy()

        for i, user in enumerate(users):
            tk.Button(self.user_menu_frame, text=user[1], command=lambda u=user: self.load_user(u)).pack()

    def load_user(self, user):
        self.user = self.client_model.get_user_by_name(user[1])
        messagebox.showinfo("Info", f"User {self.user.get_name()} loaded")
        self.server_scanner.set_user_info(self.user.get_name(), self.user.get_deck())
        self.server_scanner.atribute_user_id(self.user.get_id())
        self.user_menu_frame.pack_forget()
        self.menu_frame.pack()

    def create_user(self):
        name = simpledialog.askstring("Create User", "Enter the username:")
        if name:
            user_id = self.client_model.create_user(name)
            self.user = User()
            self.user.rename(user_id, name)
            self.create_user_card()

    def create_user_card(self):
        attributes = get_card_attributes()
        # print(attributes)
        self.client_model.create_card(self.user.name, *attributes, self.user.id)
        self.user.initialize(self.client_model.get_user_cards(self.user.id),
                             self.client_model.get_user_deck(self.user.id))
        messagebox.showinfo("Info", "User card created successfully.")
        self.user_menu_frame.pack_forget()
        self.menu_frame.pack()

    def create_card_dialog(self):
        name = simpledialog.askstring("Card Name", "Enter card name:")
        if name:
            attributes = get_card_attributes()
            self.client_model.create_card(name, *attributes, self.user.id)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))
            messagebox.showinfo("Info", "Card created successfully.")

    def display_user_cards(self):
        cards = self.user.get_cards()
        if not cards:
            tk.messagebox.showinfo("Info", "No cards available.")
            return

        # Hide the menu frame
        self.menu_frame.pack_forget()

        # Create a frame to hold the cards
        self.display_cards_frame = tk.Frame(self.root)
        self.display_cards_frame.pack(expand=True, fill=tk.BOTH)

        # Create a canvas to display the cards
        canvas = tk.Canvas(self.display_cards_frame, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(self.display_cards_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas to hold the card information
        card_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=card_frame, anchor="nw")

        # Center the card_frame within the canvas
        card_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Define the number of columns per row
        columns_per_row = 8
        row = 0
        col = 0

        for index, card in enumerate(cards):
            # Generate card image (or use a placeholder)
            card_img = card.gen_card_img()  # Replace with the appropriate method to get the card image
            img = ImageTk.PhotoImage(card_img)

            # Create label to show the card's image
            card_label = tk.Label(card_frame, image=img, padx=10, pady=10)
            card_label.image = img  # Keep a reference to avoid garbage collection

            # Place the card label in the grid
            card_label.grid(row=row, column=col, padx=5, pady=5)

            # Move to the next column
            col += 1

            # Move to the next row after every `columns_per_row` cards
            if col >= columns_per_row:
                col = 0
                row += 1

        # Create a button to return to the menu with increased size
        back_button = tk.Button(self.display_cards_frame, text="Back to Menu", command=self.return_to_menu, width=26,
                                height=2)
        back_button.pack(pady=10, side=tk.BOTTOM)

        # Set the window to full screen
        self.root.attributes("-fullscreen", True)
        self.root.update_idletasks()

    def return_to_menu(self):
        # Hide the content frames but do not destroy the menu frame
        if hasattr(self, 'display_deck_frame'):
            self.display_deck_frame.pack_forget()
        if hasattr(self, 'display_cards_frame'):
            self.display_cards_frame.pack_forget()

        # Show the menu frame
        self.menu_frame.pack(expand=True, fill=tk.BOTH)

        # Reset the window to default size
        self.root.attributes("-fullscreen", False)
        self.root.update_idletasks()

    def edit_deck_dialog(self):
        # Cria uma nova janela para editar o deck
        edit_deck_window = tk.Toplevel(self.root)
        edit_deck_window.title("Edit Deck")

        # Cria um label explicativo
        label = tk.Label(edit_deck_window, text="Escolha uma opção:")
        label.pack(pady=10)

        # Define as funções dos botões
        def return_to_menu():
            edit_deck_window.destroy()
            self.user_menu_frame.pack_forget()
            self.menu_frame.pack()

        def add_card_to_deck():
            edit_deck_window.destroy()
            self.add_card_to_deck()

        def remove_card_from_deck():
            edit_deck_window.destroy()
            self.remove_card_from_deck()

        def print_deck():
            edit_deck_window.destroy()
            self.display_user_deck()

        # Cria botões para cada opção
        btn_return = tk.Button(edit_deck_window, text="Return to Menu", command=return_to_menu, width=20, height=2)
        btn_return.pack(pady=5)

        btn_add = tk.Button(edit_deck_window, text="Add Card to Deck", command=add_card_to_deck, width=20, height=2)
        btn_add.pack(pady=5)

        btn_remove = tk.Button(edit_deck_window, text="Remove Card from Deck", command=remove_card_from_deck, width=20,
                               height=2)
        btn_remove.pack(pady=5)

        btn_print = tk.Button(edit_deck_window, text="Print Deck", command=print_deck, width=20, height=2)
        btn_print.pack(pady=5)

        # Define o tamanho da nova janela
        edit_deck_window.geometry("400x300")

    def add_card_to_deck(self):
        # Cria uma nova janela para exibir as cartas em tela cheia
        card_selection_window = tk.Toplevel(self.root)
        card_selection_window.title("Select a Card to Add to Deck")

        # Ajusta o tamanho da janela para tela cheia
        card_selection_window.attributes("-fullscreen", True)

        # Cria um canvas e uma scrollbar para a nova janela
        canvas = tk.Canvas(card_selection_window, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(card_selection_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Cria um frame dentro do canvas para exibir as cartas
        card_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=card_frame, anchor="nw")

        # Ajusta a área de rolagem do canvas quando o frame é redimensionado
        card_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Define o número de colunas por linha
        columns_per_row = 8
        row = 0
        col = 0

        def on_card_click(card_id):
            self.add_card_to_deck_op(card_id)
            card_selection_window.destroy()
            messagebox.showinfo("Info", "Card added to deck.")

        for index, card in enumerate(self.user.get_cards()):
            # Gere a imagem da carta (ou use um placeholder)
            card_img = card.gen_card_img()  # Substitua com o método apropriado para obter a imagem da carta
            img = ImageTk.PhotoImage(card_img)

            # Cria um botão para cada carta e define o cursor como uma mão
            card_button = tk.Button(card_frame, image=img, padx=10, pady=10, cursor="hand2",
                                    command=lambda id=card.id: on_card_click(id))
            card_button.image = img  # Mantenha uma referência para evitar coleta de lixo

            # Posiciona o botão no grid
            card_button.grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col >= columns_per_row:
                col = 0
                row += 1

    def add_card_to_deck_op(self, card_id):
        if card_id is not None:
            self.client_model.add_card_to_deck(self.user.id, card_id)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))

    def remove_card_from_deck(self):
        # Cria uma nova janela para exibir as cartas em tela cheia
        card_selection_window = tk.Toplevel(self.root)
        card_selection_window.title("Select a Card to Remove from Deck")

        # Ajusta o tamanho da janela para tela cheia
        card_selection_window.attributes("-fullscreen", True)

        # Cria um canvas e uma scrollbar para a nova janela
        canvas = tk.Canvas(card_selection_window, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(card_selection_window, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        canvas.configure(yscrollcommand=scrollbar.set)

        # Cria um frame dentro do canvas para exibir as cartas
        card_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=card_frame, anchor="nw")

        # Ajusta a área de rolagem do canvas quando o frame é redimensionado
        card_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Define o número de colunas por linha
        columns_per_row = 8
        row = 0
        col = 0

        def on_card_click(card_id):
            self.remove_card_from_deck_op(card_id)
            card_selection_window.destroy()
            messagebox.showinfo("Info", "Card removed from deck.")

        for index, card in enumerate(self.user.get_deck().get_cards()):
            # Gere a imagem da carta (ou use um placeholder)
            card_img = card.gen_card_img()  # Substitua com o método apropriado para obter a imagem da carta
            img = ImageTk.PhotoImage(card_img)

            # Cria um botão para cada carta e define o cursor como uma mão
            card_button = tk.Button(card_frame, image=img, padx=10, pady=10, cursor="hand2",
                                    command=lambda id=card.id: on_card_click(id))
            card_button.image = img  # Mantenha uma referência para evitar coleta de lixo

            # Posiciona o botão no grid
            card_button.grid(row=row, column=col, padx=5, pady=5)

            col += 1
            if col >= columns_per_row:
                col = 0
                row += 1

    def remove_card_from_deck_op(self, card_id):
        if card_id is not None:
            self.client_model.remove_card_from_deck(self.user.id, card_id)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))

    def display_user_deck(self):
        deck = self.user.get_deck()
        if not deck:
            tk.messagebox.showinfo("Deck", "Deck not found.")
            return

        cards = deck.get_cards()
        if not cards:
            tk.messagebox.showinfo("Deck", "Deck is empty.")
            return

        # Hide the menu frame
        self.menu_frame.pack_forget()

        # Create a frame to hold the cards
        self.display_deck_frame = tk.Frame(self.root)
        self.display_deck_frame.pack(expand=True, fill=tk.BOTH)

        # Create a canvas to display the cards
        canvas = tk.Canvas(self.display_deck_frame, bg="white")
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Add a scrollbar to the canvas
        scrollbar = tk.Scrollbar(self.display_deck_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Configure the canvas to work with the scrollbar
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Create a frame inside the canvas to hold the card information
        card_frame = tk.Frame(canvas)
        canvas.create_window((0, 0), window=card_frame, anchor="nw")

        # Center the card_frame within the canvas
        card_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        # Define the number of columns per row
        columns_per_row = 8
        row = 0
        col = 0

        for index, card in enumerate(cards):
            # Generate card image (or use a placeholder)
            card_img = card.gen_card_img()  # Replace with the appropriate method to get the card image
            img = ImageTk.PhotoImage(card_img)

            # Create label to show the card's image
            card_label = tk.Label(card_frame, image=img, padx=10, pady=10)
            card_label.image = img  # Keep a reference to avoid garbage collection

            # Place the card label in the grid
            card_label.grid(row=row, column=col, padx=5, pady=5)

            # Move to the next column
            col += 1

            # Move to the next row after every `columns_per_row` cards
            if col >= columns_per_row:
                col = 0
                row += 1

        # Create a button to return to the menu with increased size
        back_button = tk.Button(self.display_deck_frame, text="Back to Menu", command=self.return_to_menu, width=26,
                                height=2)
        back_button.pack(pady=10, side=tk.BOTTOM)

        # Set the window to full screen
        self.root.attributes("-fullscreen", True)
        self.root.update_idletasks()

        # Set the window title
        self.root.title("Deck do Usuário")

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    client_db = "path_to_your_database_file"  # Atualize isso com o caminho correto do banco de dados
    controller = ClientController(client_db)
    controller.run()
