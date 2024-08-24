from models.card import Card


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
            self.cards = [card for card in self.cards if card.get_id() != name]
        except ValueError as e:
            print(f"Error: {e}")

    def swap_cards(self, name, card):
        try:
            if not self.cards:
                raise ValueError("The deck is empty. Cannot swap a card.")
            if not isinstance(card, Card):
                raise TypeError("The object is not a Card instance.")
            self.cards = [card if card.id() == name else card for card in self.cards]
        except ValueError as e:
            print(f"Error: {e}")

    def display(self):
        try:
            if not self.cards:
                raise ValueError("The deck is empty.")
        except ValueError as e:
            print(f"Error: {e}")

    def get_cards(self):
        return self.cards

    def set_cards(self, cards):
        self.cards = cards

    def __getstate__(self):
        # Retorne o estado serializável do objeto (lista de dicionários)
        return {'cards': [card.__getstate__() for card in self.cards]}

    def __setstate__(self, state):
        # Restaure o estado do objeto a partir do estado serializado
        self.cards = [Card(**card_state) for card_state in state['cards']]
