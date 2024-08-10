import random

class GameData:
    class PlayerData:
        def __init__(self, name, player_id, deck, address):
            self.name = name
            self.hand = deck
            self.id = player_id
            self.address = address  # Endereço/porta associado ao jogador

    def __init__(self):
        self.players_data = []

    def add_player(self, name, deck, port):
        player_id = len(self.players_data)
        new_player = self.PlayerData(name, player_id, deck, port)
        self.players_data.append(new_player)

        # Imprime os dados de todos os jogadores
        for player in self.players_data:
            print(f"ID: {player.id}, Nome: {player.name}, Mão: {player.hand}, Porta: {player.address}")

        return 0

    def compact(self, address):
        # Encontra o jogador associado ao endereço fornecido
        for player in self.players_data:
            if player.address == address:
                print(f"Compactando dados para o jogador com ID {player.id}")
                return {"player_id": player.id, "players_data": self.players_data}
        return 0
