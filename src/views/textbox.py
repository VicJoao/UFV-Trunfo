import pygame
class TextBox:
    def __init__(self, x, y, width, height, font, placeholder='', limit=10):
        self.rect = pygame.Rect(x-(width/2), y-(height/2), width, height)
        self.color = (0, 0, 0)  # BLACK
        self.bg_color = (255, 255, 255)  # WHITE
        self.text = ''
        self.font = font
        self.active = False
        self.placeholder = placeholder
        self.limit = limit
        self.get_text()


    def handle_event(self, event):
        # Verifica se o evento é um clique do mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Verifica se o clique do mouse está dentro da área da caixa de texto
            if self.rect.collidepoint(event.pos):
                # Ativa ou desativa a caixa de texto
                self.active = not self.active
                print("Active: ", self.active)
            else:
                # Desativa a caixa de texto se o clique estiver fora da área
                self.active = False
            # Muda a cor da borda da caixa de texto com base no estado de atividade
            self.color = (255,255,255) if self.active else (0,0,0) # WHITE if active else BLACK

        # Verifica se o evento é uma tecla pressionada
        if event.type == pygame.KEYDOWN:
            print("Key pressed: ", event.key)
            # Se a caixa de texto está ativa
            if self.active:
                # Se a tecla pressionada é Enter, desativa a caixa de texto
                if event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER or event.key == pygame.K_TAB:
                    self.active = False
                # Se a tecla pressionada é Backspace, remove o último caractere do texto
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif len(self.text) < self.limit:
                    # Adiciona o caractere pressionado ao texto
                    self.text += event.unicode
                    print(self.text)

    def draw(self, screen):
        # Renderiza o texto atual ou o placeholder se o texto estiver vazio
        txt_surface = self.font.render(self.text if self.text else self.placeholder, True, self.color)

        # Ajusta a largura do retângulo da caixa de texto com base na largura do texto
        width = max(self.rect.width, txt_surface.get_width() + 10)
        self.rect.w = width

        # Desenha o texto renderizado na tela
        screen.blit(txt_surface, (self.rect.x + 5, self.rect.y + 5))

        # Desenha o retângulo da caixa de texto com a cor especificada
        pygame.draw.rect(screen, self.color, self.rect, 2)

    def get_text(self):
        return self.text
