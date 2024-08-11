from server2.board import Board
from server2.game_data import GameData


class Game:
    class Play:
        def __init__(self, player_id: int, card: int):
            self.player_id = player_id
            self.card_id = card

    def __init__(self, data, id: int):
        self.my_id = id

        # Inicializa a lista com um tamanho suficiente para armazenar todos os jogadores
        max_id = max(player.id for player in data)
        self.players_hands = [None] * (max_id + 1)

        for player in data:
            self.players_hands[player.id] = {
                'hand': player.hand,
                'name': player.name
            }

        self.board = Board(self.players_hands[self.my_id])
        self.turn = 0

    def remove_card(self, player_id: int, card_index: int):
        # Verifica se o ID do jogador é válido
        if player_id >= len(self.players_hands):
            raise IndexError(f"ID do jogador {player_id} é inválido.")

        # Obtém a mão do jogador
        player_hand = self.players_hands[player_id].get('hand', [])

        # Verifica se o índice da carta é válido
        if card_index >= len(player_hand):
            raise IndexError(f"Índice da carta {card_index} é inválido para o jogador {player_id}.")

        # Remove e retorna a carta jogada
        card_played = player_hand.pop(card_index)
        return card_played

    def play_turn(self, plays: list, attribute: str):
        for play in plays:
            player_id = play[0]  # ID do jogador
            card_index = play[1]  # Índice da carta na mão do jogador

            # Remove a carta jogada
            card_played = self.remove_card(player_id, card_index)
            print(f"Carta jogada: {card_played}, pelo jogador {player_id}")

            # Adiciona a carta ao tabuleiro
            self.board.add_card(card_played, player_id)

        # Declara o vencedor da rodada
        self.board.declare_round_winner(attribute)
        self.turn += 1

        # Verifica se o jogo deve terminar
        if self.turn == 3:
            return self.board.declare_winner()

        return -1
