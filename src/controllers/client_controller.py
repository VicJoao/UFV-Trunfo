import sys
from models.client_model import ClientModel
from views.client_view import ClientView
from models.user import User
class ClientController:
    def __init__(self, client_db):
        self.client_db = client_db
        self.user = User()
        self.view = ClientView()

        try:
            self.client_model = ClientModel(self.client_db)
        except Exception as e:
            self.view.display_message(f"Error initializing model: {e}")
            sys.exit(1)

    def run(self):
        self.load_user_menu()
        self.menu()

    def menu(self):
        self.view.display_menu()
        option = self.view.get_option()
        if option == 0:
            self.load_user_menu()
        elif option == 1:
            self.create_card(self.view.get_card_name())
        elif option == 2:
            self.view.display_user_cards(self.user.get_cards())
        elif option == 3:
            self.edit_deck()
        else:
            self.view.display_message("Invalid option")
        self.menu()

    def edit_deck(self):
        self.view.display_edit_deck()
        option = self.view.get_option()
        if option == 0:
            self.menu()
        elif option == 1:
            self.add_card_to_deck()
        elif option == 2:
            self.remove_card_from_deck()
        elif option == 3:
            self.view.display_user_deck(self.user.get_deck())
        else:
            self.view.display_message("Invalid option")
        self.edit_deck()

    def add_card_to_deck(self):
        self.view.display_user_cards(self.user.get_cards())
        card_option = self.view.get_card_option()
        self.add_card_to_deck_op(card_option)
        self.edit_deck()

    def remove_card_from_deck(self):
        self.view.display_user_deck(self.user.get_deck())
        card_option = self.view.get_card_option()
        self.remove_card_from_deck_op(card_option)
        self.edit_deck()

    def load_user_menu(self):
        self.view.display_user_selection(self.client_model.get_all_users())
        user_option = self.view.get_user_option()
        if user_option == 0:
            sys.exit(0)
        elif user_option == 1:
            self.create_user()
        elif user_option < 0:
            self.view.display_message("Invalid option")
        else:
            try:
                self.user = self.client_model.get_user_by_name(self.client_model.get_all_users()[user_option - 2][1])
                self.view.display_message(f"User {self.user.get_name()} loaded")
            except IndexError:
                self.view.display_message("Invalid option")
                self.load_user_menu()

    def create_user(self):
        name = self.view.get_username()
        id = self.client_model.create_user(name)
        self.user.rename(id, name)
        self.create_user_card()

    def create_user_card(self):
        self.view.display_message("Creating user card, Every user has a card")
        intelligence, charisma, sport, humor, creativity, appearance = self.view.get_card_attributes()
        self.client_model.create_card(self.user.id, self.user.name, intelligence, charisma, sport, humor, creativity,
                                      appearance)
        self.user.initialize(self.client_model.get_user_cards(self.user.id), self.client_model.get_user_deck(self.user.id))

    def create_card(self, name):
        intelligence, charisma, sport, humor, creativity, appearance = self.view.get_card_attributes()
        self.client_model.create_card(self.user.id, name, intelligence, charisma, sport, humor, creativity, appearance)
        self.user.initialize(self.client_model.get_user_cards(self.user.id), self.client_model.get_user_deck(self.user.id))

    def get_deck(self):
        try:
            return self.user.get_deck()
        except AttributeError:
            self.view.display_message("No deck found")
            self.menu()

    def add_card_to_deck_op(self, card_option):
        try:
            card = self.user.get_cards()[card_option - 1]
            self.client_model.add_card_to_deck(self.user.id, card.name)
            self.user.initialize(self.client_model.get_user_cards(self.user.id), self.client_model.get_user_deck(self.user.id))
        except IndexError:
            self.view.display_message("Invalid option")
            self.edit_deck()

    def remove_card_from_deck_op(self, card_option):
        try:
            cards = self.user.get_deck().get_cards()  # Use o método apropriado para obter a lista de cartas
            card = cards[card_option - 1]
            self.client_model.remove_card_from_deck(self.user.id, card.name)
            self.user.initialize(self.client_model.get_user_cards(self.user.id),
                                 self.client_model.get_user_deck(self.user.id))
        except IndexError:
            self.view.display_message("Invalid option")
            self.edit_deck()

    def process_message(self, message):
        print(message + "Foi recebida no DB")

        return message
