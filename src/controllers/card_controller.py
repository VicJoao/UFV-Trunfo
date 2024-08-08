from models.card import Card

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from matplotlib import pyplot as plt

class CardController:
    def __init__(self, client_db=None,host=None, port=None, name=None):
        self.client_db = client_db
        self.card = Card()


