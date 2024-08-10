import os
from dotenv import load_dotenv
import pygame
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from matplotlib import pyplot as plt
load_dotenv()
class Card(pygame.sprite.Sprite):
    def __init__(self, id, name, intelligence, charisma, sport, humor, creativity, appearance, image='assets/default.jpg', pos=(120, 180)):
        pygame.sprite.Sprite.__init__(self)
        self.id = id
        self.name = name
        self.intelligence = self._validate_stat(intelligence, "intelligence")
        self.charisma = self._validate_stat(charisma, "charisma")
        self.sport = self._validate_stat(sport, "sport")
        self.humor = self._validate_stat(humor, "humor")
        self.creativity = self._validate_stat(creativity, "creativity")
        self.appearance = self._validate_stat(appearance, "appearance")

        self.image = self.pil_to_pygame(self.gen_card_img(Image.open(image)))
        # self.image = pygame.transform.scale(self.image, (200, 300))

        # Obter o retângulo da imagem
        self.rect = self.image.get_rect()

    def get_card_pos(self):
        return self.rect.center

    def set_card_pos(self, pos):
        self.rect.center = pos

    def gen_card_img(self, selfie):
        card_image = Image.open("assets/teste.png")
        name_tag = Image.open("assets/name_tag.png")

        card_arr = np.asarray(card_image)
        card_arr = card_arr.copy()
        name_tag_arr = np.asarray(name_tag)
        name_tag_arr = name_tag_arr.copy()

        if selfie is not None:
            # Load image
            selfie_image = self.crop_picture(selfie)

            # Add selfie to card at position (25,62.6)
            selfie_arr = np.asarray(selfie_image)
            selfie_arr = selfie_arr.copy()
            posy = 62
            posx = 25

            card_arr[posy:posy + 200, posx:posx + 200, 0] = selfie_arr[:, :, 0]
            card_arr[posy:posy + 200, posx:posx + 200, 1] = selfie_arr[:, :, 1]
            card_arr[posy:posy + 200, posx:posx + 200, 2] = selfie_arr[:, :, 2]

        card_arr = self.overlay_images(card_arr, name_tag_arr)
        card_image = Image.fromarray(card_arr)

        card_image = self.write_text_on_image(card_image, self.get_name(), (130, 45), 15)
        card_image = self.write_text_on_image(card_image, str(self.get_intelligence()), (208, 287), 15, color="W")
        card_image = self.write_text_on_image(card_image, str(self.get_charisma()), (208, 311), 15, color="W")
        card_image = self.write_text_on_image(card_image, str(self.get_sport()), (208, 334), 15, color="W")
        card_image = self.write_text_on_image(card_image, str(self.get_sport()), (208, 358), 15, color="W")
        card_image = self.write_text_on_image(card_image, str(self.get_creativity()), (208, 381), 15, color="W")
        card_image = self.write_text_on_image(card_image, str(self.get_appearance()), (208, 405), 15, color="W")

        card_arr = np.asarray(card_image)

        PADRAO = 150
        width, height = Image.fromarray(card_arr).size  # Get dimensions

        card_image = Image.fromarray(card_arr).resize((PADRAO, int(height * (PADRAO / width))))

        return card_image


    def _validate_stat(self, value, stat_name):
        if not isinstance(value, (int, float)):
            raise TypeError(f"{stat_name.capitalize()} must be a number.")
        if value < 0:
            raise ValueError(f"{stat_name.capitalize()} must be non-negative.")
        return value

    def __repr__(self):
        return (f"Card({self.name}, {self.intelligence}, {self.charisma}, "
                f"{self.sport}, {self.humor}, {self.creativity}, {self.appearance})")

    def get_name(self):
        return self.name

    def get_id(self):
        return self.id

    def get_intelligence(self):
        return self.intelligence

    def get_charisma(self):
        return self.charisma

    def get_sport(self):
        return self.sport

    def get_humor(self):
        return self.humor

    def get_creativity(self):
        return self.creativity

    def get_appearance(self):
        return self.appearance

    def set_name(self, name):
        self.name = name

    def set_intelligence(self, intelligence):
        self.intelligence = self._validate_stat(intelligence, "intelligence")

    def set_charisma(self, charisma):
        self.charisma = self._validate_stat(charisma, "charisma")

    def set_sport(self, sport):
        self.sport = self._validate_stat(sport, "sport")

    def set_humor(self, humor):
        self.humor = self._validate_stat(humor, "humor")

    def set_creativity(self, creativity):
        self.creativity = self._validate_stat(creativity, "creativity")

    def set_appearance(self, appearance):
        self.appearance = self._validate_stat(appearance, "appearance")


    def pil_to_pygame(self, image):
        mode = image.mode
        size = image.size
        data = image.tobytes()

        return pygame.image.fromstring(data, size, mode)

    def pygame_to_pil(self, img):
        # Obter os dados de imagem da superfície
        raw_str = pygame.image.tostring(img, "RGB")
        # Obter as dimensões da superfície
        size = img.get_size()
        # Criar a imagem PIL a partir dos dados
        image = Image.frombytes("RGB", size, raw_str)

        return image

    def crop_picture(self, img):
        new_width = 200
        new_height = 200

        width, height = img.size  # Get dimensions

        img = img.resize((200, int(height * (200 / width))))

        width, height = img.size  # Get new dimensions

        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2

        # Crop the center of the image
        img = img.crop((left, top, right, bottom))
        return img

    def show_img_from_arr(self, img_arr):
        # Alternativamente, você pode usar matplotlib para exibir a imagem
        plt.imshow(img_arr)
        plt.axis('off')  # Oculta os eixos
        plt.show()


    def show(self):
        img_arr = np.asarray(self.pygame_to_pil(self.image))
        self.show_img_from_arr(img_arr)

    def overlay_images(self, background_arr, overlay_arr, top=0, left=0):
        """
        Sobrepõe uma imagem sobre outra apenas onde os pixels da imagem de sobreposição não são 0.

        Args:
            background_arr (np.ndarray): Array da imagem de fundo.
            overlay_arr (np.ndarray): Array da imagem de sobreposição.
            top (int): Coordenada y para posicionar a sobreposição.
            left (int): Coordenada x para posicionar a sobreposição.

        Returns:
            np.ndarray: Array da imagem resultante.
        """
        # Verificar as formas das imagens
        overlay_height, overlay_width = overlay_arr.shape[:2]
        background_height, background_width = background_arr.shape[:2]

        if overlay_height + top > background_height or overlay_width + left > background_width:
            raise ValueError("Overlay image exceeds background dimensions at the given position")

        # Criar a máscara onde os pixels do overlay não são 0
        mask = overlay_arr[:, :, 3] > 0  # Usar o canal alfa para a máscara

        # Copiar os pixels da overlay para a imagem de fundo usando a máscara
        for c in range(3):  # Para cada canal de cor (R, G, B)
            background_arr[top:top + overlay_height, left:left + overlay_width, c][mask] = overlay_arr[:, :, c][
                mask]

        return background_arr

    def write_text_on_image(self, image, text, position, font_size, color="B"):
        """
        Escreve texto em uma imagem usando uma fonte personalizada.

        Args:
            image (PIL.Image.Image): Imagem PIL onde o texto será escrito.
            text (str): Texto a ser escrito na imagem.
            position (tuple): Posição central (x, y) onde o texto será escrito.
            font_path (str): Caminho para a fonte personalizada (.ttf).
            font_size (int): Tamanho da fonte.

        Returns:
            PIL.Image.Image: Imagem resultante com o texto escrito.
        """
        # Criar um objeto de desenho
        draw = ImageDraw.Draw(image)

        # Carregar a fonte personalizada
        font = ImageFont.truetype("assets/fonts/introrust-base.otf", font_size)

        # Calcular a largura e a altura do texto
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

        # text_width = draw.textlength(text, font=font)

        # Calcular a posição para centralizar o texto
        x = position[0] - text_width // 2
        y = position[1] - text_height // 2

        # Escrever o texto na imagem
        if color == "W":
            draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))  # A cor do texto é branca com opacidade total
        else:
            draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))
        return image
