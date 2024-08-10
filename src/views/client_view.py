# client_view.py
from models.deck import Deck
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pygame
import os
from views.textbox_view import TextBox
from views.button import Button
from models.card import Card
import sys
from PIL import Image


class ClientView:
    def __init__(self):
        self.all_users = None
        pygame.font.init()
        self.normal_font = pygame.font.Font(os.getenv("FONT"), 25)
        self.small_font = pygame.font.Font(os.getenv("FONT"), 20)
        self.super_small_font = pygame.font.Font(os.getenv("FONT"), 10)

        self.screen = pygame.display.set_mode((1280, 720))
        self.clock = pygame.time.Clock()
        pygame.display.set_caption("Menu Inicial do Jogo")

        self.current_state = "NOT INITIALIZED"
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
        self.all_cards = [
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/igor_nascimento_profile.jpeg")),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/selfie.jpg")),
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/igor_nascimento_profile.jpeg")),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/selfie.jpg")),
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/igor_nascimento_profile.jpeg")),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/selfie.jpg")),
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/igor_nascimento_profile.jpeg")),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/selfie.jpg")),
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/igor_nascimento_profile.jpeg")),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/selfie.jpg")),
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/igor_nascimento_profile.jpeg")),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3,
                 image=pygame.image.load("src/assets/selfie.jpg")),

        ]

        self.all_sprites = pygame.sprite.Group()
        for card in self.all_cards:
            self.all_sprites.add(card)

        self.buttons = []
        self.textboxes = []
        self.main_menu_text = []

    def create_button(self, text, x, y, width, height, action=None, screen_name=None):
        button = Button(text, x, y, width, height, self.normal_font, action, screen_name)
        self.buttons.append(button)

    def create_textbox(self, x, y, width, height, font, placeholder, limit):
        textbox = TextBox(int(x), int(y), int(width), int(height), font, placeholder=placeholder, limit=limit)
        self.textboxes.append(textbox)

    def change_state(self, state):
        print(f"[!] Changing State: {self.current_state} -> {state}")
        self.buttons.clear()
        self.textboxes.clear()
        self.all_sprites.empty()
        self.all_cards.clear()
        print("Buttons: ", self.buttons)
        print("Textboxes: ", self.textboxes)
        self.current_state = state

    def main_menu_screen(self, users, update_screen):
        print("[!] Main Menu Screen: ClientView.main_menu_screen()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.main_menu_text.append(self.normal_font.render("Welcome to Florestrunfo!", True, (255, 255, 255)))
        self.main_menu_text.append(self.normal_font.render("Please select an user:", True, (255, 255, 255)))

        for i, name in users: # @FIXME: Se forem muitos usuários, a tela vai ficar bugada
            width = screen_width / 2
            height = screen_height / 2 - 300 + i * 60

            print(name)
            self.create_button(name, width, height, 300, 50,
                               update_screen, "CLIENT MAIN SCREEN")

        self.create_button("Create new user", screen_width / 2, screen_height / 2 + 150, 300, 50,
                            lambda: update_screen("CREATE USER"))

        self.create_button("Exit", screen_width / 2, screen_height / 2 + 210, 300, 50,
                            sys.exit)

    def client_menu_screen(self, update_screen):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.create_button("Create a new card", screen_width / 2, screen_height / 2 - 150, 300, 50,
                           lambda: update_screen("CREATE CARD DIALOG"))

        self.create_button("Show all cards", screen_width/2, screen_height/2 - 90, 300, 50,
                            lambda: update_screen("DISPLAY USER CARDS"))

        self.create_button("Edit Deck", screen_width/2, screen_height/2 - 30, 300, 50,
                           lambda: update_screen("EDIT DECK DIALOG"))

        self.create_button("Find a match", screen_width/2, screen_height/2 + 30, 300, 50,
                           lambda: self.find_match()) # @TODO: Implementar a chamada da tela de busca de partidas

        self.create_button("Create a match", screen_width/2, screen_height/2 + 90, 300, 50,
                           lambda: self.create_match_dialog()) # @TODO: Implementar a chamada da tela de criação de partidas

        self.create_button("Back", screen_width / 2, screen_height / 2 + 150, 100, 50,
                           lambda: update_screen("MAIN MENU"))

    def create_card_dialog(self, update_screen):
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
                           lambda : update_screen("CLIENT MAIN SCREEN"))
        self.create_button("Submit", screen_width / 2 + 100, screen_height / 2 + 280, 150, 50,
                           lambda: self.call_submit_card(update_screen))

    def display_user_cards(self, user, update_screen):
        print("[!] Display User Cards: ClientView.display_user_cards()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        print(user.get_user_cards())



        self.create_button("Back", screen_width - 50, 50, 100, 50,
                           lambda: update_screen("CLIENT MAIN SCREEN"))

    def edit_deck_dialog(self, update_screen):
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
                             lambda: update_screen("CLIENT MAIN SCREEN"))

    def find_match(self, ):
        print("[!] Find Match: ClientView.find_match()")

    def create_match_dialog(self, ):
        print("[!] Create Match Dialog: ClientView.create_match_dialog()")

    def add_card_to_deck(self, ):
        print("[!] Add Card to Deck: ClientView.add_card_to_deck()")

    def display_user_deck(self, ):
        print("[!] Display User Deck: ClientView.display_user_deck()")

    def remove_card_from_deck(self, ):
        print("[!] Remove Card from Deck: ClientView.remove_card_from_deck()")

    def create_new_user(self, ):
        print("[!] Create New User: ClientView.create_new_user()")

    def draw_cards(self, user_cards, posx=0, posy=200):

        for i in range (0,len(user_cards)):
            card = user_cards[i]
            print(card)
            if posx < 1000:
                posx += 180
            else:
                posx = 180
                posy += 300

            card.set_card_pos((posx, posy))

            self.all_cards.append(card)


    def draw_widgets(self):
        while True:
            self.screen.fill((0, 77, 0))
            for button in self.buttons:
                button.draw(self.screen)

            for textbox in self.textboxes:
                textbox.draw(self.screen)

            if self.current_state == "DISPLAY USER CARDS":
                self.draw_cards(self.all_cards)

            elif self.current_state == "CREATE CARD DIALOG":
                if self.img:
                    screen_info = pygame.display.Info()
                    screen_width = screen_info.current_w
                    screen_height = screen_info.current_h

                    self.screen.blit(self.txt, (screen_width / 2 + 200, screen_height / 2 - 220))

            self.handle_events()

            pygame.display.flip()
            self.clock.tick(60)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.handle_event(event)

            for textbox in self.textboxes:
                textbox.handle_event(event)

    def upload_img(self):
        # @TODO: Implementar a seleção de arquivo
        # Integrar com Tkinter para seleção de arquivo
        # tk.Tk().withdraw()  # Esconder a janela principal do Tkinter
        # filename = askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        filename = "src/assets/selfie.jpg"

        if filename:  # Se o usuário escolheu um arquivo
            self.img = pygame.image.load(filename)  # Carregar a imagem
            self.txt = self.super_small_font.render(f"Selected: {filename}", True, (255, 255, 255))

    def call_submit_card(self, update_screen):
        print("Submitting...")

        try:
            for i in range(1, len(self.textboxes)):
                self.submission[list(self.submission.keys())[i]] = int(self.textboxes[i].get_text())
        except ValueError:
            print("Invalid number. Please try again.") # @TODO: Implementar notificação de erro
            update_screen("CREATE CARD DIALOG")
            return
        self.submission["name"] = self.textboxes[0].get_text()
        self.submission["image"] = self.img

        print("Submission complete! Please check:\n", self.submission) # @TODO: Implementar notificação de erro

        # @TODO: Colocar no banco de dados
        update_screen("CLIENT MAIN SCREEN")

