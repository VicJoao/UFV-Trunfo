import sys
from models.client_model import ClientModel
from views.client_view import ClientView
from models.user import User
from controllers.conection import Connection
import pygame

class ClientController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.user = User()
        self.connection = Connection()

    def main_menu(self):
        self.view.change_state("MAIN MENU")
        self.load_state()

    def get_current_state(self):
        return self.view.current_state

    def load_state(self):
        if self.get_current_state() == "NOT INITIALIZED":
            pass

        elif self.get_current_state() == "MAIN MENU":
            self.view.main_menu_screen(self.model.get_all_users(), self.update_screen)

        elif self.get_current_state() == "CLIENT MAIN SCREEN":

            self.view.client_menu_screen(self.update_screen)

        elif self.get_current_state() == "CREATE CARD DIALOG":
            # print("[!] Create Card Dialog: ClientView.create_card_dialog()")
            self.view.create_card_screen(self.user, self.update_screen, self.set_did_create_card)

        elif self.get_current_state() == "DISPLAY USER CARDS":
            self.view.display_user_cards(self.user, self.update_screen)

        elif self.get_current_state() == "EDIT DECK DIALOG":
            # print("[!] Edit Deck Dialog: ClientView.edit_deck_dialog()")
            self.view.edit_deck_dialog(self.update_screen)

        elif self.get_current_state() == "FIND MATCH":
            self.view.find_match()

        elif self.get_current_state() == "CREATE MATCH DIALOG":
            self.view.create_match_dialog()

        elif self.get_current_state() == "ADD CARD TO DECK":
            self.view.add_card_to_deck()

        elif self.get_current_state() == "DISPLAY USER DECK":
            self.view.display_user_deck(self.user, self.update_screen)

        elif self.get_current_state() == "REMOVE CARD FROM DECK":
            self.view.remove_card_from_deck()

        elif self.get_current_state() == "CREATE USER":
            self.view.create_new_user(self.update_screen, self.set_new_user)


        self.view.draw_widgets()

    def update_screen(self, state, username=None):
        if username:
            print(f"Username: {username}")
            self.user = self.model.get_user_by_name(username)
        print("Calling...")
        self.view.change_state(state)
        self.load_state()

    def set_did_create_card(self, user, value):
        self.model.set_did_create_card(user.get_id(), value)

    def set_new_user(self, username):
        id = self.model.create_user(username)
        self.user = self.model.get_user_by_id(id)


    def run(self):
        pygame.init()
        self.view.change_state("MAIN MENU")
        self.load_state()