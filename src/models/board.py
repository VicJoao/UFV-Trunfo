import random

ATTRIBUTE_MAP = {
    'Inteligência': 1,
    'Carisma': 2,
    'Esporte': 3,
    'Humor': 4,
    'Criatividade': 5,
    'Aparência': 6
}


class Board:
    def __init__(self, my_cards):
        self.round_stat = ''
        self.my_cards = my_cards
        self.cards = [None, None, None]
        self.pile = []
        self.points = [0, 0, 0]

    def get_pile(self):
        return self.pile

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
        self.cards = [None, None, None]

    def declare_winner(self):
        max_points = max(self.points)
        # Verifica se há múltiplos jogadores com a pontuação máxima
        if self.points.count(max_points) > 1:
            return -2  # Empate
        else:
            return self.points.index(max_points)  # Índice do vencedor

    def declare_round_winner(self, attribute: str):

        if attribute not in ATTRIBUTE_MAP:
            raise ValueError(f"Atributo '{attribute}' não é reconhecido.")

        attribute_index = ATTRIBUTE_MAP[attribute]

        values = [card.get_stat(attribute_index) for card in self.cards]

        max_value = max(values)

        winners = [index for index, value in enumerate(values) if value == max_value]

        for winner in winners:
            self.add_points(winner)

        self.clear_board()
        print(f"Vencedor(es) do turno: {winners}")

        return winners
