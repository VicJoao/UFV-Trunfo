from models.card import Card

from PIL import Image, ImageDraw, ImageFont
import numpy as np
from matplotlib import pyplot as plt

class CardController:
    def __init__(self, client_db=None,host=None, port=None, name=None):
        self.client_db = client_db
        self.card = Card()
        self.atributes = {
            "name": "Igor",
            "intelligence": 0,
            "charisma": 0,
            "sport": 0,
            "humor": 0,
            "creativity": 0,
            "appearance": 0
        }


