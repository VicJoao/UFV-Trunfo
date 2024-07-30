import random
class Player:
    def __init__(self):
        self.deck = []
        self.hand = []
        self.score = 0
        self.ip = ""

    def draw_cards(self):
        self.hand = random.sample(self.deck, 3)

    def play(self):
        choice = server.get_player_choice(self.ip)
        return self.hand.pop(choice)