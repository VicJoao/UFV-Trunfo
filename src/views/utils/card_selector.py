import pygame
class CardSelector:
    def __init__(self, x, y, width, height, image):
        # self.image = pygame.image.load(image)
        self.image = image
        self.card_rect = self.image.get_rect()
        self.card_rect.x = x - (width / 2)
        self.card_rect.y = y - (height / 2)
        self.solid_rect = pygame.Rect(self.card_rect.x, self.card_rect.y, width, height)

        self.bigger_rect = self.card_rect.inflate(5, 20)

        self.active = False
        # print("Card Selector created: ", self.card_rect)

    def handle_event(self, event):
        # Verifica se o evento é um clique do mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Verifica se o clique do mouse está dentro da área da caixa de texto
            if self.card_rect.collidepoint(event.pos):
                # Ativa ou desativa a caixa de texto
                x, y = self.card_rect.center
                self.active = not self.active
                if self.active:
                    self.card_rect = self.bigger_rect
                else:
                    self.card_rect = self.image.get_rect()
                    self.card_rect.center = (x, y)


                print("Active: ", self.active)

        # Verifica se o evento é uma tecla pressionada
        if event.type == pygame.KEYDOWN:
            print("Key pressed: ", event.key)
            # Se a caixa de texto está ativa
            if self.active:
                if event.key == pygame.K_RETURN:
                    self.active = False


    def draw(self, screen):
        pygame.draw.rect(screen, (0, 51, 0), self.solid_rect)
        screen.blit(self.image, (self.card_rect.x, self.card_rect.y))