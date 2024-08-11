# client_view.py
from models.deck import Deck
import tkinter as tk
from tkinter.filedialog import askopenfilename
import pygame
import os
from views.textbox import TextBox
from views.button import Button
from views.card_selector import CardSelector
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
        self.img_filename = None
        self.txt = None
        self.username = None

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
        self.all_cards = []

        self.all_sprites = pygame.sprite.Group()

        self.buttons = []
        self.textboxes = []
        self.card_selectors = []
        self.main_menu_text = []



    def draw_widgets(self):
        while True:
            self.screen.fill((0, 77, 0))
            for button in self.buttons:
                button.draw(self.screen)

            for textbox in self.textboxes:
                textbox.draw(self.screen)

            for card_selector in self.card_selectors:
                # print("Card selector: ", card_selector.card_rect.x, card_selector.card_rect.y)
                card_selector.draw(self.screen)

            if self.current_state == "DISPLAY USER CARDS" or self.current_state == "DISPLAY USER DECK":
                # self.draw_cards(self.all_cards)
                for card in self.all_cards:
                    self.screen.blit(card.image, card.get_card_pos())

            elif self.current_state == "MAIN MENU":
                screen_info = pygame.display.Info()
                screen_width = screen_info.current_w
                screen_height = screen_info.current_h

                text_rect = self.main_menu_text[0].get_rect(center=(screen_width / 2, screen_height / 2 - 330))
                self.screen.blit(self.main_menu_text[0], text_rect)

                text_rect = self.main_menu_text[1].get_rect(center=(screen_width / 2, screen_height / 2 - 280))
                self.screen.blit(self.main_menu_text[1], text_rect)

                text_rect = self.main_menu_text[2].get_rect(center=(screen_width / 2, screen_height / 2 + 170))
                self.screen.blit(self.main_menu_text[2], text_rect)

            elif self.current_state == "CREATE CARD DIALOG":
                if self.img_filename:
                    screen_info = pygame.display.Info()
                    screen_width = screen_info.current_w
                    screen_height = screen_info.current_h

                    self.screen.blit(self.txt, (screen_width / 2 + 200, screen_height / 2 - 220))

            elif self.current_state == "CREATE USER DIALOG":
                screen_info = pygame.display.Info()
                screen_width = screen_info.current_w
                screen_height = screen_info.current_h

                self.screen.blit(self.main_menu_text[2], screen_width / 2, screen_height / 2 - 100)

            elif self.current_state == "ADD CARD TO DECK":
                screen_info = pygame.display.Info()
                screen_width = screen_info.current_w
                screen_height = screen_info.current_h

                self.screen.blit(self.txt, (screen_width / 2 - 200, screen_height / 2 - 350)) # @FIXME: Centralizar texto

            self.handle_events()

            pygame.display.flip()
            self.clock.tick(60)

    def create_button(self, text, x, y, width, height, action=None, screen_name=None):
        button = Button(text, x, y, width, height, self.normal_font, action, screen_name)
        self.buttons.append(button)

    def create_textbox(self, x, y, width, height, font, placeholder, limit):
        textbox = TextBox(int(x), int(y), int(width), int(height), font, placeholder=placeholder, limit=limit)
        self.textboxes.append(textbox)

    def create_card_selector(self, pos, size, image):
        x, y = pos
        width, height = size
        card_selector = CardSelector(x, y, width, height, image)
        self.card_selectors.append(card_selector)

    def change_state(self, state):
        print(f"[!] Changing State: {self.current_state} -> {state} \nVariables reset.")
        self.buttons.clear()
        self.textboxes.clear()
        self.card_selectors.clear()
        self.all_sprites.empty()
        self.all_cards.clear()
        self.current_state = state

    def main_menu_screen(self, users, update_screen):
        print("[!] Main Menu Screen: ClientView.main_menu_screen()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.main_menu_text.append(self.normal_font.render("Welcome to Florestrunfo!", True, (255, 255, 255)))
        self.main_menu_text.append(self.normal_font.render("Please select an user:", True, (255, 255, 255)))

        for i, user in enumerate(users): # @FIXME: Se forem muitos usuários, a tela vai ficar bugada
            width = screen_width / 2
            height = screen_height / 2 - 300 + (i+1) * 60

            self.create_button(user[1], width, height, 300, 50,
                               update_screen, "CLIENT MAIN SCREEN")

        self.main_menu_text.append(self.normal_font.render("Or create a new one:", True, (255, 255, 255)))

        self.create_button("Create new user", screen_width / 2, screen_height / 2 + 210, 300, 50,
                            lambda: update_screen("CREATE USER"))

        self.create_button("Exit", screen_width / 2, screen_height / 2 + 270, 300, 50,
                            sys.exit)

    def client_menu_screen(self, update_screen):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        # self.create_button("Create a new card", screen_width / 2, screen_height / 2 - 150, 300, 50,
        #                    lambda: update_screen("CREATE CARD DIALOG"))

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

    def create_card_screen(self,user, update_screen, set_did_create_card):
        if user.did_create_card:
            print("Card already created.") #@TODO: Implementar notificação de erro
            update_screen("CLIENT MAIN SCREEN")
        else:
            print("[!] Create Card Screen: ClientView.create_card_screen()")
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
                               lambda: self.submit_new_card(user, update_screen, set_did_create_card))

    def display_user_cards(self, user, update_screen):
        print("[!] Display User Cards: ClientView.display_user_cards()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        if not self.all_cards:
            self.draw_cards(user.cards)

        self.create_button("Back", screen_width - 60, 50, 100, 50,
                           lambda: update_screen("CLIENT MAIN SCREEN"))

    def edit_deck_dialog(self, update_screen):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.create_button("Add card to deck", screen_width / 2, screen_height / 2 - 90, 300, 50,
                           lambda: update_screen("ADD CARD TO DECK"))
        self.create_button("Remove card from deck", screen_width / 2, screen_height / 2 - 30,300, 50,
                           lambda: update_screen("REMOVE CARD FROM DECK"))
        self.create_button("Show deck", screen_width / 2, screen_height / 2 + 30, 300, 50,
                            lambda: update_screen("DISPLAY USER DECK"))
        self.create_button("Back", screen_width / 2, screen_height / 2 + 90, 100, 50,
                            lambda: update_screen("CLIENT MAIN SCREEN"))

    def find_match(self, ):
        print("[!] Find Match: ClientView.find_match()")

    def create_match_dialog(self, ):
        print("[!] Create Match Dialog: ClientView.create_match_dialog()")

    def add_card_to_deck(self, user, update_screen, get_not_in_deck_cards, add_card_to_deck):
        print("[!] Add Card to Deck: ClientView.add_card_to_deck()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.txt = self.small_font.render("Select one or more cards to add to your deck:", True, (255, 255, 255))

        self.draw_cards(get_not_in_deck_cards(user), posy = 200)
        for card in self.all_cards:
            self.create_card_selector(card.get_card_pos(), card.size, card.image)


        self.create_button("Back", screen_width - 60, 50, 100, 50,
                            lambda: update_screen("CLIENT MAIN SCREEN"))

        self.create_button("Add", screen_width / 2, screen_height - 60, 100, 50,
                            lambda: self.add_card_to_deck_action(user, update_screen, add_card_to_deck)) #@TODO: mudar a posição??

    def add_card_to_deck_action(self, user, update_screen, add_card_to_deck):
        print("[!] Add Card to Deck Action: ClientView.add_card_to_deck_action()")

        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        print("[!] Adding cards to deck...")

        # print(user.get_deck().get_cards())

        for i, card in enumerate(self.all_cards):
            if self.card_selectors[i].active:
                user.get_deck().add_card(card)
                add_card_to_deck(user, card)
                print(f"Card {card.get_name()} added to deck.")
                self.card_selectors[i].active = False

        update_screen("EDIT DECK DIALOG")


    def display_user_deck(self, user, update_screen):
        print("[!] Display User Deck: ClientView.display_user_deck()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        # print(self.all_cards)
        if not self.all_cards:
            self.draw_cards(user.get_deck().get_cards())

        self.create_button("Back", screen_width - 60, 50, 100, 50,
                           lambda: update_screen("CLIENT MAIN SCREEN"))

    def remove_card_from_deck(self,user, update_screen, remove_card_from_deck):
        print("[!] Remove Card from Deck: ClientView.remove_card_from_deck()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.txt = self.small_font.render("PLEASE, SELECT one or more cards to remove from your deck:", True, (255, 255, 255))

        self.draw_cards(user.get_deck().get_cards(), posy=200)
        for card in self.all_cards:
            self.create_card_selector(card.get_card_pos(), card.size, card.image)

        self.create_button("Back", screen_width - 60, 50, 100, 50,
                            lambda: update_screen("CLIENT MAIN SCREEN"))

        self.create_button("Remove", screen_width / 2, screen_height - 60, 150, 50,
                            lambda: self.remove_card_from_deck_action(user, update_screen, remove_card_from_deck))

    def remove_card_from_deck_action(self,user, update_screen, remove_card_from_deck):
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        print("[!] Removing cards from deck...")

        print(user.get_deck().get_cards())

        for i, card in enumerate(self.all_cards):
            if self.card_selectors[i].active:
                user.get_deck().remove_card(card.get_name())
                remove_card_from_deck(user, card)
                print(f"Card {card.get_name()} removed from deck.")
                self.card_selectors[i].active = False

        print(user.get_deck().get_cards())

        update_screen("EDIT DECK DIALOG")

    def create_new_user(self, update_screen, set_new_user):
        print("[!] Create New User: ClientView.create_new_user()")
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h

        self.create_textbox(screen_width / 2, screen_height / 2 - 50, 350, 50, self.small_font,
                            placeholder='First and last name', limit=15)
        self.create_button("Submit", screen_width / 2 + 100, screen_height / 2 + 50, 150, 50,
                           lambda: self.submit_new_user(update_screen, set_new_user))
        self.create_button("Cancel", screen_width / 2 - 100, screen_height / 2 + 50, 150, 50,
                           lambda: update_screen("MAIN MENU"))

    def draw_cards(self, user_cards, posx=-70, posy=100):
        print("[!] Draw Cards: ClientView.draw_cards()")
        for i in range (0,len(user_cards)):
            card = user_cards[i]
            if posx < 1000:
                posx += 180
            else:
                posx = 110
                posy += 300

            card.set_card_pos((posx, posy))

            self.all_cards.append(card)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                for button in self.buttons:
                    button.handle_event(event)

                for card_selector in self.card_selectors:
                    card_selector.handle_event(event)

            for textbox in self.textboxes:
                textbox.handle_event(event)

    def upload_img(self):
        # @TODO: Implementar a seleção de arquivo
        # Integrar com Tkinter para seleção de arquivo
        # tk.Tk().withdraw()  # Esconder a janela principal do Tkinter
        # filename = askopenfilename(filetypes=[("Image files", "*.png;*.jpg;*.jpeg")])
        filename = "src/assets/selfie.jpg"

        if filename:  # Se o usuário escolheu um arquivo
            self.img_filename = filename  # Carregar a imagem
            self.txt = self.super_small_font.render(f"Selected: {filename}", True, (255, 255, 255))

    def submit_new_card(self, user, update_screen, set_did_create_card):
        print("Submitting card...")
        try:
            for i in range(1, len(self.textboxes)):
                self.submission[list(self.submission.keys())[i]] = int(self.textboxes[i].get_text())
        except ValueError:
            print("Invalid number. Please try again.") # @TODO: Implementar notificação de erro
            update_screen("CREATE CARD DIALOG")
            return
        self.submission["name"] = self.textboxes[0].get_text()
        self.submission["image"] = self.img_filename

        print("Submission complete! Please check:\n", self.submission) # @TODO: Implementar notificação de erro
        user.did_create_card = True
        set_did_create_card(user, True)

        update_screen("MAIN MENU")

    def submit_new_user(self, update_screen, set_new_user):
        print("Submitting user...")
        try:
            for i in range(1, len(self.textboxes)):
                self.submission[list(self.submission.keys())[i]] = str(self.textboxes[i].get_text())
        except ValueError:
            print("Invalid name. Please try again.") # @TODO: Implementar notificação de erro
            update_screen("CREATE USER DIALOG")
            return
        self.username = self.textboxes[0].get_text()

        print("Submission complete! Please check:\n", self.username)  # @TODO: Implementar notificação de erro

        set_new_user(self.username)

        update_screen("CREATE CARD DIALOG")
