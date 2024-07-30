from server.board import Board


class Game:
    def __init__(self):
        self.player1 = None
        self.player2 = None
        self.board = Board()
        self.turn = 0

    def add_player(self, player):
        if self.player1 is None:
            self.player1 = player
        elif self.player2 is None:
            self.player2 = player
        else:
            return 0  # Already two players

    def start_game(self):
        if not self.player1 or not self.player2:
            return 0  # Need two players to start the game
        self.player1.draw_cards()
        self.player2.draw_cards()
        self.turn = 1
        return 1


    def play_turn(self):
        while True:
            for player in [self.player1, self.player2]:
                card = player.play()
                if not card:
                    return self.board.declare_winner()
                self.board.add_card(card, player)
                self.turn += 1

            # Assuming you want to declare a round winner every two turns (one full round)
            if self.turn % 2 == 0:
                self.board.declare_round_winner()
