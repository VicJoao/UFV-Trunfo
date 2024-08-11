from server2.board import Board
from server2.game_data import GameData
from models.card import Card

NUMERO_TURNOS = 5

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

        # Obtém a carta a ser removida e cria uma cópia dela
        card_played = player_hand[card_index]
        card_backup = Card(
            card_played.id,
            card_played.name,
            card_played.intelligence,
            card_played.charisma,
            card_played.sport,
            card_played.humor,
            card_played.creativity,
            card_played.appearance
        )

        # Marca a carta como removida (ou inativa) definindo seus atributos como 0
        player_hand[card_index].set_name("Removed")
        player_hand[card_index].set_intelligence(0)
        player_hand[card_index].set_charisma(0)
        player_hand[card_index].set_sport(0)
        player_hand[card_index].set_humor(0)
        player_hand[card_index].set_creativity(0)
        player_hand[card_index].set_appearance(0)

        # Retorna a cópia da carta com seus atributos originais
        return card_backup

    def play_turn(self, plays: list, attribute: str):
        print("__________________________________________")
        print("Atributo da rodada: ", attribute)
        print("______________________________________________________ ")
        print("COMPARANDO AS CARTAS: ")
        for play in plays:
            player_id = play[0]  # ID do jogador
            card_index = play[1]  # Índice da carta na mão do jogador

            # Remove a carta jogada
            card_played = self.remove_card(player_id, card_index)
            print(f"Carta jogada: {card_played}, pelo jogador {player_id}")


            # Adiciona a carta ao tabuleiro
            self.board.add_card(card_played, player_id)

        print("______________________________________________________ ")
        # Declara o vencedor da rodada
        self.board.declare_round_winner(attribute)
        self.turn += 1

        # Verifica se o jogo deve terminar
        if self.turn == NUMERO_TURNOS:
            return self.board.declare_winner()

        return -1
