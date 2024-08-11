import random
from models.card import Card
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
        # Certifica-se de que todos os itens em self.cards são realmente objetos Card
        if not all(isinstance(card, Card) for card in self.cards):
            raise TypeError("Todos os itens em self.cards devem ser objetos do tipo Card.")

        # Obtém os valores do atributo especificado para cada carta
        values = [getattr(card, attribute) for card in self.cards]

        # Encontra o valor máximo do atributo
        max_value = max(values)

        # Identifica os índices das cartas com o valor máximo
        winners = [index for index, value in enumerate(values) if value == max_value]

        print("WINNER, jogador(es) de ID: ", winners)  # Exibe os vencedores para depuração

        # Adiciona pontos a todos os vencedores
        for winner in winners:
            self.add_points(winner)
        print("PLACAR: ", self.points)

        # Limpa o tabuleiro
        self.clear_board()

        # Retorna os índices dos vencedores (podem ser vários)
        return winners

