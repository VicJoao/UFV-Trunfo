import tkinter as tk
from tkinter import simpledialog, messagebox

from models.client_model import ClientModel
from models.user import User
from controllers.client_connection import ServerScanner


def get_card_attributes():
    attributes = {
        "Intelligence": simpledialog.askinteger("Card Attribute", "Enter Intelligence:"),
        "Charisma": simpledialog.askinteger("Card Attribute", "Enter Charisma:"),
        "Sport": simpledialog.askinteger("Card Attribute", "Enter Sport:"),
        "Humor": simpledialog.askinteger("Card Attribute", "Enter Humor:"),
        "Creativity": simpledialog.askinteger("Card Attribute", "Enter Creativity:"),
        "Appearance": simpledialog.askinteger("Card Attribute", "Enter Appearance:")
    }
    return [attributes[key] for key in ["Intelligence", "Charisma", "Sport", "Humor", "Creativity", "Appearance"]]


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
        self.server_scanner = ServerScanner(self.root, )
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
            messagebox.showinfo("Info", "No cards available.")
            return

        card_info = "\n".join(
            f"ID: {card.id}\n"
            f"Name: {card.name}\n"
            f"  Intelligence: {card.intelligence}\n"
            f"  Charisma: {card.charisma}\n"
            f"  Sport: {card.sport}\n"
            f"  Humor: {card.humor}\n"
            f"  Creativity: {card.creativity}\n"
            f"  Appearance: {card.appearance}\n"
            f"{'-' * 20}"
            for card in cards
        )
        messagebox.showinfo("Cards", card_info)

    def edit_deck_dialog(self):
        option = simpledialog.askinteger("Edit Deck",
                                         "Enter option:\n0 - Return to menu\n1 - Add card to deck\n2 - Remove card "
                                         "from deck\n3 - Print deck")
        if option == 0:
            self.user_menu_frame.pack_forget()
            self.menu_frame.pack()
        elif option == 1:
            self.add_card_to_deck()
        elif option == 2:
            self.remove_card_from_deck()
        elif option == 3:
            self.display_user_deck()
        else:
            messagebox.showinfo("Info", "Returning to menu.")

    def add_card_to_deck(self):
        self.display_user_cards()
        card_option = simpledialog.askinteger("Add Card to Deck", "Enter card option:")
        self.add_card_to_deck_op(card_option)
        messagebox.showinfo("Info", "Card added to deck.")

    def remove_card_from_deck(self):
        self.display_user_deck()
        card_option = simpledialog.askinteger("Remove Card from Deck", "Enter card option:")
        self.remove_card_from_deck_op(card_option)
        messagebox.showinfo("Info", "Card removed from deck.")

    def add_card_to_deck_op(self, card_option):
        if card_option is not None:
            self.client_model.add_card_to_deck(self.user.id, card_option)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))

    def remove_card_from_deck_op(self, card_option):
        if card_option is not None:
            self.client_model.remove_card_from_deck(self.user.id, card_option)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))

    def display_user_deck(self):
        deck = self.user.get_deck()
        if not deck:
            messagebox.showinfo("Deck", "Deck not found.")
            return

        cards = deck.get_cards()
        if not cards:
            messagebox.showinfo("Deck", "Deck is empty.")
            return

        deck_info = "\n".join(
            f"ID : {card.id}\n"
            f"Name: {card.name}\n"
            f"  Intelligence: {card.intelligence}\n"
            f"  Charisma: {card.charisma}\n"
            f"  Sport: {card.sport}\n"
            f"  Humor: {card.humor}\n"
            f"  Creativity: {card.creativity}\n"
            f"  Appearance: {card.appearance}\n"
            f"{'-' * 20}"
            for card in cards
        )
        messagebox.showinfo("Deck", deck_info)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    client_db = "path_to_your_database_file"  # Atualize isso com o caminho correto do banco de dados
    controller = ClientController(client_db)
    controller.run()
