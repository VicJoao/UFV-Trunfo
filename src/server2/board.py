import random
class Board:
    def __init__(self):
        self.round_stat = ''
        self.cards = []
        self.pile = []
        self.points = []

    def randomize(self):
        round_stat = random.choice(['intelligence', 'charisma', 'sport', 'humor', 'creativity', 'appearance'])
        self.round_stat = round_stat
        return round_stat

    def add_card(self, card, player):
        self.cards[player] = card

    def add_pile(self, cards):
        for card in cards:
            self.pile.append(card)

    def add_points(self, player):
        self.points[player] += 1

    def clear_board(self):
        self.add_pile(self.cards)
        self.cards = []

    def declare_winner(self):
        return self.points.index(max(self.points))

    def declare_round_winner(self):
        values = [getattr(card, self.round_stat) for card in self.cards]
        winner = values.index(max(values))
        self.add_points(winner)
        self.clear_board()
        self.randomize()
        return winner

    def get_pile(self):
        return self.pile