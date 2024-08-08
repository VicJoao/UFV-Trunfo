from ..models.card import Card

class Deck:
    def __init__(self):
        self.cards = []

    def create(self, cards):
        self.cards = cards

    def add_card(self, card):
        try:
            if not isinstance(card, Card):
                raise TypeError("The object is not a Card instance.")
            self.cards.append(card)
        except TypeError as e:
            print(f"Error: {e}")

    def remove_card(self, name):
        try:
            if not self.cards:
                raise ValueError("The deck is empty. Cannot remove a card.")
            self.cards = [card for card in self.cards if card.get_name() != name]
        except ValueError as e:
            print(f"Error: {e}")

    def swap_cards(self, name, card):
        try:
            if not self.cards:
                raise ValueError("The deck is empty. Cannot swap a card.")
            if not isinstance(card, Card):
                raise TypeError("The object is not a Card instance.")
            self.cards = [card if card.get_name() == name else card for card in self.cards]
        except ValueError as e:
            print(f"Error: {e}")

    def display(self):
        try:
            if not self.cards:
                raise ValueError("The deck is empty.")
            for card in self.cards:
                print(card)
        except ValueError as e:
            print(f"Error: {e}")

    def get_cards(self):
        return self.cards

    def set_cards(self, cards):
        self.cards = cards
