import random

class GameData:
    class PlayerData:
        def __init__(self, name, player_id, deck):
            self.name = name
            self.hand = deck
            self.id = player_id
            self.address = None  # Endereço ainda não associado

    def __init__(self):
        self.players_data = []
        self.ports = []  # Lista para armazenar as portas

    def add_port(self, port):
        # Adiciona a porta à lista de portas
        self.ports.append(port)

    def add_player(self, name, deck):
        player_id = len(self.players_data)
        new_player = self.PlayerData(name, player_id, deck)
        self.players_data.append(new_player)

        # Imprime os dados de todos os jogadores
        for player in self.players_data:
            print(f"ID: {player.id}, Nome: {player.name}, Mão: {player.hand}")

        return 0

    def associate_ports_to_players(self):
        # Associa cada porta ao jogador correspondente
        for i in range(min(len(self.players_data), len(self.ports))):
            self.players_data[i].address = self.ports[i]
            print(f"Jogador {self.players_data[i].name} associado à porta {self.ports[i]}")

    def compact(self, address):
        # Encontra o jogador associado ao endereço fornecido
        for player in self.players_data:
            if player.address == address:
                print(f"Compactando dados para o jogador com ID {player.id}")
                return {"player_id": player.id, "players_data": self.players_data}
        return 0