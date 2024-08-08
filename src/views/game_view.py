import pygame
import threading
from models.card import Card

class GameView:
    def __init__(self, controller):
        self.controller = controller
        self.running = False
        self.all_cards = [
            Card(name="Miguel Ribeiro", intelligence=4, charisma=3, sport=2, humor=5, creativity=3, appearance=3),
        ]
        self.all_sprites = pygame.sprite.Group()
        for card in self.all_cards:
            self.all_sprites.add(card)

    def create_card(self, name, intelligence, charisma, sport, humor, creativity, appearance):
        self.all_cards.append(
            Card(name, intelligence, charisma, sport, humor, creativity, appearance)
        )

        self.all_sprites.add(self.all_cards[-1])

    def start_game(self):
        self.running = True
        game_thread = threading.Thread(target=self.run_game)
        game_thread.start()

    def run_game(self):
        pygame.init()
        screen = pygame.display.set_mode((800, 600))
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
            pygame.mouse.set_cursor(*pygame.cursors.arrow)
            pygame.display.flip()

        pygame.quit()


