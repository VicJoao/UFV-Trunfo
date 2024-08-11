import random
from models.card import Card
class Board:
    def __init__(self, my_cards):
        self.round_stat = ''
        self.my_cards = my_cards
        self.cards = [None, None, None]
        self.pile = []
        self.points = [0, 0, 0]

    def randomize(self):
        round_stat = random.choice(['intelligence', 'charisma', 'sport', 'humor', 'creativity', 'appearance'])
        self.round_stat = round_stat
        return round_stat

    def add_card(self, card, player):
        self.cards[player] = card
        print("CARDDS" , self.cards)  # Exibe o dicionário de cartas para depuração

    def add_pile(self, cards):
        for card in cards:
            self.pile.append(card)
            print(self.pile)

    def add_points(self, player):
        self.points[player] += 1
        print(self.points)

    def clear_board(self):
        self.add_pile(self.cards)
        self.cards = [None, None, None]

    def declare_winner(self):
        return self.points.index(max(self.points))

    def declare_round_winner(self, attribute: str):
        print(self.cards)  # Exibe as cartas no tabuleiro para depuração

        # Certifica-se de que todos os itens em self.cards são realmente objetos Card
        if not all(isinstance(card, Card) for card in self.cards):
            raise TypeError("Todos os itens em self.cards devem ser objetos do tipo Card.")

        # Obtém os valores do atributo especificado para cada carta
        values = [getattr(card, attribute) for card in self.cards]

        # Encontra o índice do vencedor
        winner = max(range(len(values)), key=values.__getitem__)

        print("EWINNER", winner)

        # Adiciona pontos ao vencedor e limpa o tabuleiro
        self.add_points(winner)
        self.clear_board()

        return winner

    def get_pile(self):
        return self.pile