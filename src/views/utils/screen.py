import sys
import pygame

class ScreenView:
    def __init__(self, screen, background=None, buttons=None, input_boxes=None, card_selectors=None, labels=[]):
        self.screen = screen
        self.clock = pygame.time.Clock()

        self.font = pygame.font.Font('assets/fonts/introrust-base.otf', 30)

        self.buttons = buttons
        self.input_boxes = input_boxes
        self.card_selectors = card_selectors
        self.labels = labels
        self.background = background
        self.sum = None

    def draw_widgets(self):
        while True:
            if self.background is not None:
                bg_img = pygame.image.load(self.background)
                if bg_img.get_width() != 1920 or bg_img.get_height() != 1080:
                    bg_img = pygame.transform.scale(bg_img, (1920, 1080))
                self.screen.blit(bg_img, (0, 0))
            else: self.screen.fill((0, 77, 0))

            if self.buttons is not None:
                for button in self.buttons:
                    button.draw(self.screen)

            if self.input_boxes is not None:
                for input_box in self.input_boxes:
                    input_box.draw(self.screen)

            if self.card_selectors is not None:
                for card_selector in self.card_selectors:
                    card_selector.draw(self.screen)

            if self.labels is not None and self.labels != []:
                if self.labels == ['Create card']:
                    self.get_sum_text()
                    for label in self.labels:
                        text, pos = label
                        print (text, pos)
                        text_rect = text.get_rect(center=pos)
                        self.screen.blit(text, text_rect)

            self.handle_events()

            pygame.display.flip()
            self.clock.tick(30)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if self.buttons is not None:
                    for button in self.buttons:
                        button.handle_event(event)
                if self.card_selectors is not None:
                    for card_selector in self.card_selectors:
                        card_selector.handle_event(event)

            if self.input_boxes is not None:
                for input_box in self.input_boxes:
                    input_box.handle_event(event)

    def get_sum_text(self):
        self.sum = 0
        for box in self.input_boxes:  # Acessa todas as InputBoxes da tela
            if box.type == "number" and box.text.isnumeric():  # Verifica se é do tipo número e se o texto é numérico
                self.sum += int(box.text)  # Adiciona o valor ao somatório
        self.labels = [(self.font.render(f"Attributes sum: {self.sum}", True, (255, 255, 255)), (1920 / 2, 850))]
