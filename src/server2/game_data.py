import random


class GameData:
    class PlayerData:
        def __init__(self, name, player_id, deck, address):
            self.name = name
            self.hand = []
            for i in range(3):
                self.hand.append(deck.pop(random.randint(0, len(deck) - 1)))
            self.id = player_id
            self.address = address

    def __init__(self):
        self.players_data = []

    def add_player(self, name, deck, address):
        player_id = len(self.players_data)
        self.players_data.append(self.PlayerData(name, player_id, deck, address))
        return 0

    def compact(self, address):
        for player in self.players_data:
            if player.address == address:
                return {player.id, self.players_data}
        return 0
