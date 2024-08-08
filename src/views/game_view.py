import pygame
import threading
from models.card import Card
from PIL import Image

class GameView:
    def __init__(self, controller):
        self.controller = controller
        self.running = False
        self.all_cards = [
            Card(name="Igor Nascimento", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3, image=Image.open("assets/igor_nascimento_profile.jpeg"), pos=(300, 300)),
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3, image=Image.open("assets/selfie.jpg"), pos=(600, 300)),
        ]
        self.all_sprites = pygame.sprite.Group()
        for card in self.all_cards:
            self.all_sprites.add(card)

    def create_card(self, name, intelligence, charisma, sport, humor, creativity, appearance, image):
        self.all_cards.append(
            Card(name, intelligence, charisma, sport, humor, creativity, appearance, image, (0, 0))
        )

        self.all_sprites.add(self.all_cards[-1])

    def start_game(self):
        self.running = True
        game_thread = threading.Thread(target=self.run_game)
        game_thread.start()

    def run_game(self):
        pygame.init()
        screen = pygame.display.set_mode((1280, 720)) #,pygame.FULLSCREEN)
        pygame.mouse.set_cursor(*pygame.cursors.arrow)
        pygame.mouse.set_visible(True)
        pygame.display.set_caption("Florestrunfo - Jogo")

        background_color = (0, 77, 0)
        clock = pygame.time.Clock()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            screen.fill(background_color)
            self.all_sprites.update()
            self.all_sprites.draw(screen)

            pygame.display.flip()


        pygame.quit()


