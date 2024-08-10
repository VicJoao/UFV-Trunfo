from server2.board import Board
from server2.game_data import GameData

class Game:
    class Play:
        def __init__(self, player_id: int, card: int):
            self.player_id = player_id
            self.card_id = card

    def __init__(self, data: GameData, id: int):
        self.my_id = id
        self.players_hands = []
        for player in data.players_data:
            self.players_hands[player.id] = {player.hand, player.name}
        self.board = Board(self.players_hands[self.my_id])
        self.board.randomize()
        self.turn = 0


    def play_turn(self, plays: list):
        for play in plays:
            card_played = self.players_hands[play.player_id][play.card_id]
            self.board.add_card(card_played, play.player_id)
        self.board.declare_round_winner()
        self.turn += 1
        if self.turn == 3:
            return self.board.declare_winner()
        return -1