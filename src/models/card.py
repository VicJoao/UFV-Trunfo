from dotenv import load_dotenv
import pygame
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from matplotlib import pyplot as plt
import os

# Load environment variables
load_dotenv()

# Load image using pygame
image_path = os.path.join("assets", "default.jpg")
IMG = pygame.image.load(image_path)

# Get rectangle and size from IMG
RECT = IMG.get_rect()
SIZE = IMG.get_size()

class Card:
    def __init__(self, id, name, intelligence, charisma, sport, humor, creativity, appearance, image="assets/default.jpg", pos=(120, 180)):
        self.id = id
        self.name = name
        self.intelligence = self._validate_stat(intelligence, "intelligence")
        self.charisma = self._validate_stat(charisma, "charisma")
        self.sport = self._validate_stat(sport, "sport")
        self.humor = self._validate_stat(humor, "humor")
        self.creativity = self._validate_stat(creativity, "creativity")
        self.appearance = self._validate_stat(appearance, "appearance")

    def get_card_pos(self):
        return RECT.center

    def set_card_pos(self, pos):
        RECT.center = pos

    def gen_card_img(self):
        try:
            # Load images and ensure RGBA format
            card_image = Image.open("assets/teste.png").convert("RGBA")
            name_tag = Image.open("assets/name_tag.png").convert("RGBA")

            # Convert images to numpy arrays
            card_arr = np.asarray(card_image)
            name_tag_arr = np.asarray(name_tag)

            # Debugging: Check the shape and mode of images
            print(f"Card image shape: {card_arr.shape}")
            print(f"Name tag shape: {name_tag_arr.shape}")

            if IMG is not None:
                # Convert Pygame image to PIL and ensure RGBA format
                selfie_image = self.crop_picture(self.pygame_to_pil(IMG)).convert("RGBA")

                # Convert selfie to numpy array
                selfie_arr = np.asarray(selfie_image)
                print(f"Selfie array shape: {selfie_arr.shape}")

                # Ensure that selfie image fits within the card
                posy, posx = 62, 25
                if (posy + selfie_arr.shape[0] > card_arr.shape[0]) or (posx + selfie_arr.shape[1] > card_arr.shape[1]):
                    raise ValueError("Selfie image exceeds card dimensions at the given position")

                # Create a copy of card_arr to avoid modifying read-only arrays
                card_arr_copy = card_arr.copy()
                # Add selfie to card
                card_arr_copy[posy:posy + selfie_arr.shape[0], posx:posx + selfie_arr.shape[1]] = selfie_arr

                # Overlay images
                card_arr_copy = self.overlay_images(card_arr_copy, name_tag_arr)
                card_image = Image.fromarray(card_arr_copy, mode="RGBA")
            else:
                # If IMG is None, just use the card image and name tag
                card_image = Image.fromarray(card_arr, mode="RGBA")
                card_image = Image.fromarray(self.overlay_images(np.asarray(card_image), name_tag_arr), mode="RGBA")

            # Add text to the card
            card_image = self.write_text_on_image(card_image, self.get_name(), (130, 45), 15)
            card_image = self.write_text_on_image(card_image, str(self.get_intelligence()), (208, 287), 15, color="W")
            card_image = self.write_text_on_image(card_image, str(self.get_charisma()), (208, 311), 15, color="W")
            card_image = self.write_text_on_image(card_image, str(self.get_sport()), (208, 334), 15, color="W")
            card_image = self.write_text_on_image(card_image, str(self.get_humor()), (208, 358), 15, color="W")
            card_image = self.write_text_on_image(card_image, str(self.get_creativity()), (208, 381), 15, color="W")
            card_image = self.write_text_on_image(card_image, str(self.get_appearance()), (208, 405), 15, color="W")

            # Resize image
            card_image = card_image.resize((200, int(card_image.height * (200 / card_image.width))))
            return card_image

        except Exception as e:
            print(f"Error generating card image: {e}")
            return None

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

        if mode == "RGB":
            return pygame.image.fromstring(data, size, "RGB")
        else:
            raise ValueError("Unsupported image mode")

    def pygame_to_pil(self, img):
        mode = "RGB"
        size = img.get_size()
        data = pygame.image.tostring(img, mode)
        return Image.frombytes(mode, size, data)

    def crop_picture(self, img):
        new_width, new_height = 200, 200

        width, height = img.size
        img = img.resize((200, int(height * (200 / width))))

        width, height = img.size

        left = (width - new_width) / 2
        top = (height - new_height) / 2
        right = (width + new_width) / 2
        bottom = (height + new_height) / 2

        img = img.crop((left, top, right, bottom))
        return img

    def show_img_from_arr(self, img_arr):
        plt.imshow(img_arr)
        plt.axis('off')
        plt.show()

    def show(self):
        img_arr = np.asarray(self.pygame_to_pil(IMG))
        self.show_img_from_arr(img_arr)

    def overlay_images(self, background_arr, overlay_arr, top=0, left=0):
        overlay_height, overlay_width = overlay_arr.shape[:2]
        background_height, background_width = background_arr.shape[:2]

        if overlay_height + top > background_height or overlay_width + left > background_width:
            raise ValueError("Overlay image exceeds background dimensions at the given position")

        mask = overlay_arr[:, :, 3] > 0

        for c in range(3):
            background_arr[top:top + overlay_height, left:left + overlay_width, c][mask] = overlay_arr[:, :, c][mask]

        return background_arr

    def write_text_on_image(self, image, text, position, font_size, color="B"):
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
