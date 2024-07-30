import tkinter as tk
from tkinter import simpledialog, messagebox
from models.deck import Deck
from models.client_model import ClientModel
from models.user import User
from controllers.conection import Connection


class ClientController:
    def __init__(self, client_db):
        self.client_db = client_db
        self.user = None
        self.conection = Connection()
        self.client_model = ClientModel(self.client_db)
        self.root = tk.Tk()
        self.root.title("Client Manager")
        self.create_widgets()
        self.load_user_menu()

    def create_widgets(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()

        self.user_menu_frame = tk.Frame(self.root)
        self.user_menu_frame.pack_forget()  # Initially hide user menu

        # Main Menu Widgets
        self.label = tk.Label(self.menu_frame, text="Select an option:")
        self.label.pack()

        self.create_card_button = tk.Button(self.menu_frame, text="Create new card", command=self.create_card_dialog)
        self.create_card_button.pack()

        self.print_cards_button = tk.Button(self.menu_frame, text="Print all cards", command=self.display_user_cards)
        self.print_cards_button.pack()

        self.edit_deck_button = tk.Button(self.menu_frame, text="Edit Deck", command=self.edit_deck_dialog)
        self.edit_deck_button.pack()

        self.find_match_button = tk.Button(self.menu_frame, text="Find a match", command=self.conection.scan)
        self.find_match_button.pack()

        self.create_match_button = tk.Button(self.menu_frame, text="Create a match", command=self.create_match_dialog)
        self.create_match_button.pack()

        self.select_user_button = tk.Button(self.menu_frame, text="Select a User", command=self.load_user_menu)
        self.select_user_button.pack()

        self.exit_button = tk.Button(self.menu_frame, text="Exit", command=self.root.quit)
        self.exit_button.pack()

        # User Menu Widgets
        self.user_label = tk.Label(self.user_menu_frame, text="Select the username you want to load:")
        self.user_label.pack()

        self.create_user_button = tk.Button(self.user_menu_frame, text="Create new user", command=self.create_user)
        self.create_user_button.pack()

        self.exit_user_button = tk.Button(self.user_menu_frame, text="Exit", command=self.root.quit)
        self.exit_user_button.pack()

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
        attributes = self.get_card_attributes()
        self.client_model.create_card(self.user.id, self.user.name, *attributes)
        self.user.initialize(self.client_model.get_user_cards(self.user.id),
                             self.client_model.get_user_deck(self.user.id))
        messagebox.showinfo("Info", "User card created successfully.")
        self.user_menu_frame.pack_forget()
        self.menu_frame.pack()

    def create_card_dialog(self):
        name = simpledialog.askstring("Card Name", "Enter card name:")
        if name:
            attributes = self.get_card_attributes()
            self.client_model.create_card(self.user.id, name, *attributes)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))
            messagebox.showinfo("Info", "Card created successfully.")

    def display_user_cards(self):
        cards = self.user.get_cards()
        if not cards:
            messagebox.showinfo("Info", "No cards available.")
            return

        card_info = "\n".join(
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
                                         "Enter option:\n0 - Return to menu\n1 - Add card to deck\n2 - Remove card from deck\n3 - Print deck")
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

    def create_match_dialog(self):
        server_name = simpledialog.askstring("Create Match", "Enter server name:")
        if server_name:
            self.conection.create_server(server_name)
            messagebox.showinfo("Info", "Server created successfully.")

    def get_card_attributes(self):
        attributes = {
            "intelligence": simpledialog.askinteger("Card Attributes", "Enter the intelligence value:"),
            "charisma": simpledialog.askinteger("Card Attributes", "Enter the charisma value:"),
            "sport": simpledialog.askinteger("Card Attributes", "Enter the sport value:"),
            "humor": simpledialog.askinteger("Card Attributes", "Enter the humor value:"),
            "creativity": simpledialog.askinteger("Card Attributes", "Enter the creativity value:"),
            "appearance": simpledialog.askinteger("Card Attributes", "Enter the appearance value:")
        }
        return (attributes["intelligence"], attributes["charisma"], attributes["sport"], attributes["humor"],
                attributes["creativity"], attributes["appearance"])

    def display_user_deck(self):
        deck = self.user.get_deck()
        if not isinstance(deck, Deck):
            messagebox.showerror("Error", "Invalid deck object.")
            return

        cards = deck.get_cards()
        if not cards:
            messagebox.showinfo("Info", "Empty deck.")
            return

        deck_info = "\n".join(
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

    def add_card_to_deck_op(self, card_option):
        try:
            card = self.user.get_cards()[card_option - 1]
            self.client_model.add_card_to_deck(self.user.id, card.name)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))
        except IndexError:
            messagebox.showerror("Error", "Invalid option")

    def remove_card_from_deck_op(self, card_option):
        try:
            cards = self.user.get_deck().get_cards()
            card = cards[card_option - 1]
            self.client_model.remove_card_from_deck(self.user.id, card.name)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))
        except IndexError:
            messagebox.showerror("Error", "Invalid option")

