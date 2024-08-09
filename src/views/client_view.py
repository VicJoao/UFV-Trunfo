# client_view.py
from models.deck import Deck
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pygame
import os
from views.textbox_view import TextBox
from views.button_view import Button
import sys
class ClientView:
    def __init__(self):
        pygame.font.init()
        self.normal_font = pygame.font.Font(os.getenv("FONT"), 25)
        self.small_font = pygame.font.Font(os.getenv("FONT"), 20)
        self.supersmall_font = pygame.font.Font(os.getenv("FONT"), 10)

        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Menu Inicial do Jogo")
        self.states = {
            "NOT INITIALIZED": "NOT INITIALIZED",
            "MAIN MENU": "MAIN MENU",
            "CLIENT MAIN SCREEN": "CLIENT MAIN SCREEN",
            "CREATE CARD DIALOG": "CREATE CARD DIALOG",
            "DISPLAY USER CARDS": "DISPLAY USER CARDS",
            "EDIT DECK DIALOG": "EDIT DECK DIALOG",
            "FIND MATCH": "FIND MATCH",
            "CREATE MATCH DIALOG": "CREATE MATCH DIALOG",
            "ADD CARD TO DECK": "ADD CARD TO DECK",
            "DISPLAY USER DECK": "DISPLAY USER DECK",
            "REMOVE CARD FROM DECK": "REMOVE CARD FROM DECK",

        }

        self.current_state = 0
        self.img = None
        self.txt = None
        self.submission = {
            "name": None,
            "intelligence": None,
            "charisma": None,
            "sport": None,
            "humor": None,
            "creativity": None,
            "appearance": None,
            "image": None
        }
        self.buttons = []
        self.textboxes = []

    def create_button(self, text, x, y, width, height, action):
        button = Button(text, x, y, width, height, self.normal_font, action)
        self.buttons.append(button)

    def create_textbox(self, x, y, width, height, font, placeholder, limit):
        textbox = TextBox(int(x), int(y), int(width), int(height), font, placeholder=placeholder, limit=limit)
        self.textboxes.append(textbox)

    def run(self):
        # Inicializar o Pygame
        pygame.init()
        self.change_state(self.states["CLIENT MAIN SCREEN"])
        self.load_state()
        # self.teste_login()

    def change_state(self, state):
        print(f"[!] Changing State: {self.current_state} -> {state}")
        self.buttons = []
        self.textboxes = []
        self.current_state = state

    def load_state(self):
        #while True:
        # print(f"[!] Current State: {self.current_state}")
        if self.current_state == "NOT INITIALIZED":
            pass
        elif self.current_state == "MAIN MENU":
            self.main_menu_screen()
        elif self.current_state == "CLIENT MAIN SCREEN":
            # print("[!] Client Main Screen: ClientView.client_main_screen()")
            self.client_main_screen()
        elif self.current_state == "CREATE CARD DIALOG":
            # print("[!] Create Card Dialog: ClientView.create_card_dialog()")
            self.create_card_dialog()
        elif self.current_state == "DISPLAY USER CARDS":
            self.display_user_cards()
        elif self.current_state == "EDIT DECK DIALOG":
            # print("[!] Edit Deck Dialog: ClientView.edit_deck_dialog()")
            self.edit_deck_dialog()
        elif self.current_state == "FIND MATCH":
            self.find_match()
        elif self.current_state == "CREATE MATCH DIALOG":
            self.create_match_dialog()
        elif self.current_state == "ADD CARD TO DECK":
            self.add_card_to_deck()
        elif self.current_state == "DISPLAY USER DECK":
            self.display_user_deck()
        elif self.current_state == "REMOVE CARD FROM DECK":
            self.remove_card_from_deck()

        self.draw_widgets()

    def main_menu_screen(self):
        print("[!] Create Widgets: ClientView.create_widgets()")

    def client_main_screen(self):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.create_button("Create a new card", screen_width / 2, screen_height / 2 - 150, 300, 50,
                           lambda: self.call_create_card_screen()) # @TODO: Implementar a chamada da tela de criação de cartas

        self.create_button("Show all cards", screen_width/2, screen_height/2 - 90, 300, 50,
                            lambda: self.display_user_cards()) # @TODO: Implementar a chamada da tela de exibição de cartas

        self.create_button("Edit Deck", screen_width/2, screen_height/2 - 30, 300, 50,
                           lambda: self.call_edit_deck_screen())

        self.create_button("Find a match", screen_width/2, screen_height/2 + 30, 300, 50,
                           lambda: self.find_match()) # @TODO: Implementar a chamada da tela de busca de partidas
        self.create_button("Create a match", screen_width/2, screen_height/2 + 90, 300, 50,
                           lambda: self.create_match_dialog()) # @TODO: Implementar a chamada da tela de criação de partidas
        self.create_button("Back", screen_width / 2, screen_height / 2 + 150, 100, 50,
                           lambda: self.main_menu_screen()) # @TODO: Implementar a chamada da tela de menu principal

    def draw_widgets(self):
        while True:
            self.screen.fill((0, 77, 0))
            self.handle_events()
            for button in self.buttons:
                button.draw(self.screen)

            for textbox in self.textboxes:
                textbox.draw(self.screen)

            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for button in self.buttons:
                button.handle_event(event)

            for textbox in self.textboxes:
                textbox.handle_event(event)

    def create_card_dialog(self):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.create_button("Upload selfie", screen_width / 2, screen_height / 2 - 210, 350, 50,
                                 lambda : self.upload_img()) # @TODO: Implementar a chamada da tela de upload de imagem
        self.create_textbox(screen_width / 2, screen_height / 2 - 150, 350, 50, self.small_font,
                                placeholder='Name', limit=15)
        self.create_textbox(screen_width / 2, screen_height / 2 - 90, 350, 50, self.small_font,
                                placeholder='Intelligence', limit=2)
        self.create_textbox(screen_width / 2, screen_height / 2 - 30, 350, 50, self.small_font,
                                placeholder='Charisma', limit=2)
        self.create_textbox(screen_width / 2, screen_height / 2 + 30, 350, 50, self.small_font,
                                placeholder='Sport', limit=2)
        self.create_textbox(screen_width / 2, screen_height / 2 + 90, 350, 50, self.small_font,
                                placeholder='Humor', limit=2)
        self.create_textbox(screen_width / 2, screen_height / 2 + 150, 350, 50, self.small_font,
                                placeholder='Creativity', limit=2)
        self.create_textbox(screen_width / 2, screen_height / 2 + 210, 350, 50, self.small_font,
                                placeholder='Appearance', limit=2)

        self.create_button("Cancel", screen_width / 2 - 100, screen_height / 2 + 280, 150, 50,
                           lambda : self.call_client_main_screen())
        self.create_button("Submit", screen_width / 2 + 100, screen_height / 2 + 280, 150, 50,
                           lambda: self.call_submit_card())


    def display_user_cards(self):
        print("[!] Display User Cards: ClientView.display_user_cards()")


    def edit_deck_dialog(self):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.create_button("Add card to deck", screen_width / 2, screen_height / 2 - 90, 300, 50,
                           lambda:self.add_card_to_deck()) # @TODO: Implementar a chamada da tela de adição de cartas ao deck
        self.create_button("Remove card from deck", screen_width / 2, screen_height / 2 - 30,
                                              300, 50, lambda: self.remove_card_from_deck()) # @TODO: Implementar a chamada da tela de remoção de cartas do deck
        self.create_button("Show deck", screen_width / 2, screen_height / 2 + 30, 300, 50,
                                  lambda: self.display_user_deck()) # @TODO: Implementar a chamada da tela de exibição do deck

        self.create_button("Back", screen_width / 2, screen_height / 2 + 90, 100, 50,
                             lambda: self.call_client_main_screen())


    def find_match(self):
        print("[!] Find Match: ClientView.find_match()")

    def create_match_dialog(self):
        print("[!] Create Match Dialog: ClientView.create_match_dialog()")

    def add_card_to_deck(self):
        print("[!] Add Card to Deck: ClientView.add_card_to_deck()")

    def display_user_deck(self):
        print("[!] Display User Deck: ClientView.display_user_deck()")

    def remove_card_from_deck(self):
        print("[!] Remove Card from Deck: ClientView.remove_card_from_deck()")

    def upload_img(self):
        # @TODO: Implementar a seleção de arquivo
        # Integrar com Tkinter para seleção de arquivo
        # tk.Tk().withdraw()  # Esconder a janela principal do Tkinter
        # filename = askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        filename = "src/assets/selfie.jpg"

        if filename:  # Se o usuário escolheu um arquivo
            self.img = pygame.image.load(filename)  # Carregar a imagem
            self.txt = self.supersmall_font.render(f"Selected: {filename}", True, (255, 255, 255))


    def call_create_card_screen(self):
        print("Calling...")
        self.change_state("CREATE CARD DIALOG")
        self.load_state()

    def call_edit_deck_screen(self):
        print("Calling...")
        self.change_state("EDIT DECK DIALOG")
        self.load_state()

    def call_client_main_screen(self):
        print("Calling...")
        self.change_state("CLIENT MAIN SCREEN")
        self.load_state()

    def call_submit_card(self):
        print("Submitting...")

        for i in range(len(self.textboxes)):
            self.submission[list(self.submission.keys())[i]] = self.textboxes[i].get_text()
        self.submission["image"] = self.img

        print("Submission complete! Please check:\n", self.submission)

        # @TODO: Colocar no banco de dados
        self.change_state("CLIENT MAIN SCREEN")
        self.load_state()