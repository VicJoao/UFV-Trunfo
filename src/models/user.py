from models.card import Card

class User:
    def __init__(self):
        self.name = ""
        self.cards = []
        self.deck = []
        self.id = 0
        self.did_create_card = False
    def rename(self, id, name, did_create_card=False):
        self.name = name
        self.id = id
        self.did_create_card = did_create_card

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

    def get_id(self):
        return self.id

    def get_deck(self):
        return self.deck

    def get_did_create_card(self):
        return self.did_create_card

    def set_name(self, name):
        self.name = name

    def set_cards(self, cards):
        self.cards = cards

    def set_deck(self, deck):
        self.deck = deck

    def set_did_create_card(self, did_create_card):
        self.did_create_card = did_create_card