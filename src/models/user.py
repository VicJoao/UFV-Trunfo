from src.models.card import Card

class User:
    def __init__(self):
        self.name = ""
        self.cards = []
        self.deck = []
        self.id = 0
    def rename(self, id, name):
        self.name = name
        self.id = id

    def initialize(self, cards, deck):
        self.deck = deck
        self.cards = cards

    def add_card(self, card):
        try:
            if not isinstance(card, Card):
                raise TypeError("The object is not a Card instance.")
            self.cards.append(card)
        except TypeError as e:
            print(f"Error: {e}")

    def display_cards(self):
        try:
            if not self.cards:
                raise ValueError("The user has no cards.")
            for card in self.cards:
                print(card)

        except ValueError as e:
            print(f"Error: {e}")

    def get_name(self):
        return self.name

    def get_cards(self):
        return self.cards

    def get_deck(self):
        return self.deck

    def set_name(self, name):
        self.name = name

    def set_cards(self, cards):
        self.cards = cards

    def set_deck(self, deck):
        self.deck = deck
