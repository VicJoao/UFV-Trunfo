from server.board import Board
from server.player import Player
class Game:
    def __init__(self):
        self.player1 = Player()
        self.player2 = Player()
        self.player3 = Player()
        self.player4 = Player()
        self.board = Board()
        self.turn = 0

    def add_player(self, player):
        if not self.player1:
            self.player1 = player
        elif not self.player2:
            self.player2 = player
        elif not self.player3:
            self.player3 = player
        elif not self.player4:
            self.player4 = player
        else:
            return 0

    def start_game(self):
        if not self.player1 or not self.player2 or not self.player3 or not self.player4:
            return 0
        self.board.create_board()
        for player in [self.player1, self.player2, self.player3, self.player4]:
            player.draw_cards()
        self.turn = 1
        return 1

    def turn(self):
        while True:
            for player in [self.player1, self.player2, self.player3, self.player4]:
                card = player.play()
                if not card:
                    return self.board.declare_winner()
                self.board.add_card(card, player)
                self.turn += 1
            if self.turn == 4:
                self.board.declare_round_winner()
                self.turn = 0
