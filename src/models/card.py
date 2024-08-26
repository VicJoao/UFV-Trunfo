from dotenv import load_dotenv
import pygame
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from matplotlib import pyplot as plt
import os

"""
    Esse módulo contém a classe Card, que representa uma carta do jogo.
    
    Variáveis globais:
    
        IMG: pygame.Surface
            Imagem da carta.
            
        RECT: pygame.Rect
            Retângulo que representa a posição e dimensões da imagem.
            
        SIZE: Tuple[int, int]
            Tamanho da imagem.
            
"""
load_dotenv()


"""

    Funções auxiliares:
    
        get_card_pos() -> Tuple[int, int]
            Retorna a posição da carta.
            
        set_card_pos(pos: Tuple[int, int])
            Define a posição da carta.
            
        _validate_stat(value: Union[int, float], stat_name: str) -> Union[int, float]
            Valida um valor de atributo.
            
        pil_to_pygame(image: Image) -> pygame.Surface
            Converte uma imagem PIL para uma imagem pygame.
            
        pygame_to_pil(img: pygame.Surface) -> Image
            Converte uma imagem pygame para uma imagem PIL.
            
        crop_picture(img: Image) -> Image
            Corta uma imagem para o tamanho 200x200.
            
        show_img_from_arr(img_arr: np.ndarray)
            Mostra uma imagem a partir de um array numpy.
            
        overlay_images(background_arr: np.ndarray, overlay_arr: np.ndarray, top: int, left: int) -> np.ndarray
            Sobrepõem duas imagens.
            
        show()
            Mostra a imagem da carta.
            
        write_text_on_image(image: Image, text: str, position: Tuple[int, int], font_size: int, color: str) -> Image
            Escreve um texto em uma imagem.
            
            
"""


def _validate_stat(value, stat_name):
    if not isinstance(value, (int, float)):
        raise TypeError(f"{stat_name.capitalize()} must be a number.")
    if value < 0:
        raise ValueError(f"{stat_name.capitalize()} must be non-negative.")
    return value


def pil_to_pygame(image):
    mode = image.mode
    size = image.size
    data = image.tobytes()

    if mode == "RGB":
        return pygame.image.fromstring(data, size, "RGB")
    else:
        raise ValueError("Unsupported image mode")


def pygame_to_pil(img):
    mode = "RGB"
    size = img.get_size()
    data = pygame.image.tostring(img, mode)
    return Image.frombytes(mode, size, data)


def crop_picture(img):
    new_width, new_height = 200, 200

    width, height = img.size
    if width > height:
        img = img.resize((int(width * (200 / height)), 200))
    else:
        img = img.resize((200, int(height * (200 / width))))

    width, height = img.size

    left = (width - new_width) / 2
    top = (height - new_height) / 2
    right = (width + new_width) / 2
    bottom = (height + new_height) / 2

    img = img.crop((left, top, right, bottom))
    return img


def show_img_from_arr(img_arr):
    plt.imshow(img_arr)
    plt.axis('off')
    plt.show()


def overlay_images(background_arr, overlay_arr, top=0, left=0):
    overlay_height, overlay_width = overlay_arr.shape[:2]
    background_height, background_width = background_arr.shape[:2]

    if overlay_height + top > background_height or overlay_width + left > background_width:
        raise ValueError("Overlay image exceeds background dimensions at the given position")

    mask = overlay_arr[:, :, 3] > 0

    for c in range(3):
        background_arr[top:top + overlay_height, left:left + overlay_width, c][mask] = overlay_arr[:, :, c][mask]

    return background_arr


def show(image):
    img_arr = np.asarray(pygame_to_pil(image))
    show_img_from_arr(img_arr)


def write_text_on_image(image, text, position, font_size, color="B"):
    draw = ImageDraw.Draw(image)
    font = ImageFont.truetype("assets/fonts/introrust-base.otf", font_size)

    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = position[0] - text_width // 2
    y = position[1] - text_height // 2

    if color == "W":
        draw.text((x, y), text, font=font, fill=(255, 255, 255, 255))
    else:
        draw.text((x, y), text, font=font, fill=(0, 0, 0, 255))

    return image

class Card:
    def __init__(self, id, name, intelligence, charisma, sport, humor, creativity, appearance, image_path="assets/photos/default.jpg"):
        self.id = id
        self.name = name
        self.intelligence = _validate_stat(intelligence, "intelligence")
        self.charisma = _validate_stat(charisma, "charisma")
        self.sport = _validate_stat(sport, "sport")
        self.humor = _validate_stat(humor, "humor")
        self.creativity = _validate_stat(creativity, "creativity")
        self.appearance = _validate_stat(appearance, "appearance")
        self.image_path = image_path
        self.image = pygame.image.load(image_path) if image_path is not None else None
        self.image_rect = self.image.get_rect() if self.image is not None else None


    # def get_card_pos(self):
    #     return RECT.center

    def set_card_pos(self, pos):
        self.image_rect.center = pos

    """
        Métodos relevantes:
        
            gen_card_img() -> Image
                Gera a imagem da carta.
                
            __repr__() -> str
                Representação da carta.
                
            __getstate__() -> Dict[str, Any]
                Retorna o estado do objeto.
                
            __setstate__(state: Dict[str, Any])
                Define o estado do objeto.
                
            get_stat(index: int) -> Union[str, int, float]
                Retorna o valor de um atributo.
                        
    """
    def gen_card_img(self):
        try:
            card_image = Image.open("assets/elements/teste.png").convert("RGBA")
            name_tag = Image.open("assets/elements/name_tag.png").convert("RGBA")

            card_arr = np.asarray(card_image)
            name_tag_arr = np.asarray(name_tag)

            # print("self.image", self.image)

            if self.image is not None:
                if os.path.getsize(self.image_path) > 1000000:
                    self.image = pil_to_pygame(pygame_to_pil(self.image).resize((200, int(self.image_rect.height * (200 / self.image_rect.width)))))
                    # img = pygame_to_pil(self.image).rotate(90)
                    # img.save("assets/photos/" + self.get_name() + "_rezided.png")
                    pygame_to_pil(self.image).save("assets/photos/" + self.get_name() + "_rezided.png")
                    self.image_path = "assets/photos/" + self.get_name() + "_rezided.png"

                selfie_image = crop_picture(pygame_to_pil(self.image)).convert("RGBA")

                selfie_arr = np.asarray(selfie_image)

                posy, posx = 62, 25
                if (posy + selfie_arr.shape[0] > card_arr.shape[0]) or (posx + selfie_arr.shape[1] > card_arr.shape[1]):
                    raise ValueError("Selfie image exceeds card dimensions at the given position")

                card_arr_copy = card_arr.copy()
                card_arr_copy[posy:posy + selfie_arr.shape[0], posx:posx + selfie_arr.shape[1]] = selfie_arr

                card_arr_copy = overlay_images(card_arr_copy, name_tag_arr)
                card_image = Image.fromarray(card_arr_copy, mode="RGBA")
            else:
                card_image = Image.fromarray(card_arr, mode="RGBA")
                card_image = Image.fromarray(overlay_images(np.asarray(card_image), name_tag_arr), mode="RGBA")

            card_image = write_text_on_image(card_image, self.get_name(), (130, 45), 15)
            card_image = write_text_on_image(card_image, str(self.get_intelligence()), (208, 287), 15, color="W")
            card_image = write_text_on_image(card_image, str(self.get_charisma()), (208, 311), 15, color="W")
            card_image = write_text_on_image(card_image, str(self.get_sport()), (208, 334), 15, color="W")
            card_image = write_text_on_image(card_image, str(self.get_humor()), (208, 358), 15, color="W")
            card_image = write_text_on_image(card_image, str(self.get_creativity()), (208, 381), 15, color="W")
            card_image = write_text_on_image(card_image, str(self.get_appearance()), (208, 405), 15, color="W")

            card_image = card_image.resize((200, int(card_image.height * (200 / card_image.width))))

            # Se a imagem ainda não estiver salva, salvar imagem gerada
            if not os.path.isfile(
                    "assets/cards/" + self.get_name() + ".png") and self.image_path != "assets/photos/default.jpg":
                if not os.path.exists("assets/cards/"):
                    os.makedirs("assets/cards/")
                print("Saving card image...")
                card_image.save("assets/cards/" + self.get_name() + ".png")

            return card_image

        except Exception as e:
            print(f"Error generating card image: {e}")
            return None

    def __repr__(self):
        return (f"Card({self.name}, {self.intelligence}, {self.charisma}, "
                f"{self.sport}, {self.humor}, {self.creativity}, {self.appearance}, {self.image_path})")

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
        self.intelligence = _validate_stat(intelligence, "intelligence")

    def set_charisma(self, charisma):
        self.charisma = _validate_stat(charisma, "charisma")

    def set_sport(self, sport):
        self.sport = _validate_stat(sport, "sport")

    def set_humor(self, humor):
        self.humor = _validate_stat(humor, "humor")

    def set_creativity(self, creativity):
        self.creativity = _validate_stat(creativity, "creativity")

    def set_appearance(self, appearance):
        self.appearance = _validate_stat(appearance, "appearance")

    def __getstate__(self):
        return {
            'id': self.id,
            'name': self.name,
            'intelligence': self.intelligence,
            'charisma': self.charisma,
            'sport': self.sport,
            'humor': self.humor,
            'creativity': self.creativity,
            'appearance': self.appearance,
            'image_path': self.image_path,
        }

    def __setstate__(self, state):
        self.id = state['id']
        self.name = state['name']
        self.intelligence = state['intelligence']
        self.charisma = state['charisma']
        self.sport = state['sport']
        self.humor = state['humor']
        self.creativity = state['creativity']
        self.appearance = state['appearance']
        self.image_path = state['image_path']

    def get_stat(self, index):
        stats = [self.name, self.intelligence, self.charisma, self.sport, self.humor, self.creativity, self.appearance, self.image_path]
        if index < 0 or index >= len(stats):
            raise IndexError("Índice fora do intervalo dos atributos")
        return stats[index]
