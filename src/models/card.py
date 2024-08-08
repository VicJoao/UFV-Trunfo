import pygame
from PIL import Image
class Card(pygame.sprite.Sprite):
    def __init__(self, name, intelligence, charisma, sport, humor, creativity, appearance, image=Image.open("assets/igor_nascimento_profile.jpeg"), controller=None):
        pygame.sprite.Sprite.__init__(self)
        self.name = name
        self.intelligence = self._validate_stat(intelligence, "intelligence")
        self.charisma = self._validate_stat(charisma, "charisma")
        self.sport = self._validate_stat(sport, "sport")
        self.humor = self._validate_stat(humor, "humor")
        self.creativity = self._validate_stat(creativity, "creativity")
        self.appearance = self._validate_stat(appearance, "appearance")

        self.image = self.gen_card_img(image)
        # self.image = pygame.transform.scale(self.image, (200, 300))

        # Obter o retângulo da imagem
        self.rect = self.image.get_rect()
        self.rect.center = (50, 50)  # Posição inicial da carta

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

        card_image = self.write_text_on_image(card_image, self.atributes["name"], (130, 45), 25)
        card_image = self.write_text_on_image(card_image, str(self.atributes["intelligence"]), (208, 287), 10, color="W")
        card_image = self.write_text_on_image(card_image, str(self.atributes["charisma"]), (208, 311), 10, color="W")
        card_image = self.write_text_on_image(card_image, str(self.atributes["sport"]), (208, 335), 10, color="W")
        card_image = self.write_text_on_image(card_image, str(self.atributes["humor"]), (208, 359), 10, color="W")
        card_image = self.write_text_on_image(card_image, str(self.atributes["creativity"]), (208, 383), 10, color="W")
        card_image = self.write_text_on_image(card_image, str(self.atributes["appearance"]), (208, 407), 10, color="W")

        card_arr = np.asarray(card_image)
        self.show_img_from_arr(card_arr)

        return Image.fromarray(card_arr)


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
