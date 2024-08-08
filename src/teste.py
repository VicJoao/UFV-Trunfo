from PIL import Image
from controllers.card_controller import CardController
import matplotlib.pyplot as plt
import numpy as np

img = Image.open("assets/igor_nascimento_profile.jpeg")
card_arr = np.asarray(CardController().gen_card(img))
card_img = Image.fromarray(card_arr)
Image.save(card_img, "assets/para_testar.png")
CardController().show_img_from_arr(card_arr)