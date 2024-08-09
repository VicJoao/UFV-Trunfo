# button_view.py
import pygame

class Button:
    def __init__(self, text, x, y, width, height, font, action=None):
        self.text = text
        self.rect = pygame.Rect(x - (width / 2), y - (height / 2), width, height)
        self.color = (0, 0, 0)  # BLACK
        self.hover_color = (10, 41, 10)  # MIDDLE GREEN
        self.font = font
        self.action = action

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        if self.rect.collidepoint(mouse_pos):
            pygame.draw.rect(screen, self.hover_color, self.rect)
            if mouse_click[0] == 1 and self.action:
                self.action()
        else:
            pygame.draw.rect(screen, self.color, self.rect)

        text_surface = self.font.render(self.text, True, (255, 255, 255))  # WHITE
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                if self.action:
                    self.action()