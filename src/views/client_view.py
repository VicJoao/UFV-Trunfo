import pygame
import os

from views.utils.button import Button
from views.utils.input_box import InputBox
from views.utils.card_selector import CardSelector
from views.utils.screen import ScreenView
class ClientView:
    def __init__(self):
        pygame.font.init()
        self.screen = None
        self.normal_font = pygame.font.Font(os.getenv("FONT"), 25)
        self.small_font = pygame.font.Font(os.getenv("FONT"), 20)
        self.super_small_font = pygame.font.Font(os.getenv("FONT"), 10)

        self.root_width = 1920
        self.root_height = 1080
        self.root = pygame.display.set_mode((self.root_width, self.root_height), pygame.FULLSCREEN)

        self.sum = 0

    def create_button(self, text, x, y, width, height, action=None, screen_name=None):

        return Button(text, x, y, width, height, action, screen_name)
        # self.buttons.append(button)

    def create_inputbox(self, x, y, width, height, font=None, placeholder="", limit=10):
        if font is None:
            font = self.normal_font
        return InputBox(int(x), int(y), int(width), int(height), font, placeholder=placeholder, limit=limit)
        # self.textboxes.append(textbox)

    def create_card_selector(self, pos, size, image):
        x, y = pos
        width, height = size
        return CardSelector(x, y, width, height, image)
        # self.card_selectors.append(card_selector)

    def main_menu(self, update=None, background_path=None):
        print("[!] Main Menu: ClientView.main_menu()")
        buttons = []


        # Create buttons
        buttons.append(Button("Sign Up", self.root_width/2, 887.5, 240, 70,
                           action=update, screen_name="2 - CREATE NEW USER"))

        self.screen = ScreenView(self.root, background=background_path, buttons=buttons)

    def create_user(self, update=None, background_path=None):
        print("[!] Create User: ClientView.create_user()")
        buttons = []
        input_boxes = [
            InputBox(self.root_width/2, 203, 552, 77, placeholder="Username",limit=15),
            InputBox(self.root_width / 2 - 433, 438, 552, 75, placeholder="First and Last Name", limit=15),
            InputBox(self.root_width / 2 - 300, 595, 450, 77, placeholder="Intelligence", limit=2, type="number"),
            InputBox(self.root_width / 2 - 300, 685, 450, 77, placeholder="Charisma", limit=2, type="number"),
            InputBox(self.root_width / 2 - 300, 775, 450, 77, placeholder="Sport", limit=2, type="number"),
            InputBox(self.root_width / 2 + 300, 595, 450, 77, placeholder="Humor", limit=2, type="number"),
            InputBox(self.root_width / 2 + 300, 685, 450, 77, placeholder="Creativity", limit=2, type="number"),
            InputBox(self.root_width / 2 + 300, 775, 450, 77, placeholder="Appearance", limit=2, type="number"),
        ]

        # Create buttons
        buttons.append(Button("Cancel", self.root_width/2 - 155, 1010, 200, 70,
                           action=update, screen_name="1 - MAIN MENU"))
        buttons.append(Button("Submit", self.root_width/2 + 155, 1010, 200, 70,
                            action=update, screen_name="3 - SUBMIT NEW USER"))

        self.screen = ScreenView(self.root, background=background_path, buttons=buttons,
                                 input_boxes=input_boxes)
        self.screen.labels.append("Create card")
        self.screen.get_sum_text()

    # def set_sum(self):
    #     for input_box in self.screen.input_boxes:
    #         print(input_box.text)
    #         if input_box.type == "number" and input_box.text != "":
    #             # input_box.text = input_box.text.replace(" ", "")
    #             # print(input_box.text)
    #             self.sum += input_box.text
