import tkinter as tk
from tkinter import messagebox
from models.board import Board
from models.card import Card

NUMERO_TURNOS = 5


class Game:
    class Play:
        def __init__(self, player_id: int, card: int):
            self.player_id = player_id
            self.card_id = card

    def __init__(self, data, index: int):
        self.my_id = index

        max_id = max(player['id'] for player in data)
        self.players_hands = [None] * (max_id + 1)

        for player in data:
            self.players_hands[player['id']] = {
                'hand': player['hand'],
                'name': player['name']
            }

        self.board = Board(self.players_hands[self.my_id])
        self.turn = 0

    def remove_card(self, player_id: int, card_index: int):
        if player_id >= len(self.players_hands):
            raise IndexError(f"ID do jogador {player_id} é inválido.")
        player_hand = self.players_hands[player_id].get('hand', [])
        if card_index >= len(player_hand):
            raise IndexError(f"Índice da carta {card_index} é inválido para o jogador {player_id}.")
        card_played = player_hand[card_index]
        card_backup = Card(
            card_played['id'],
            card_played['name'],
            card_played['intelligence'],
            card_played['charisma'],
            card_played['sport'],
            card_played['humor'],
            card_played['creativity'],
            card_played['appearance'],
            card_played['image_path']
        )

        player_hand[card_index]['name'] = "Removed"
        player_hand[card_index]['intelligence'] = 0
        player_hand[card_index]['charisma'] = 0
        player_hand[card_index]['sport'] = 0
        player_hand[card_index]['humor'] = 0
        player_hand[card_index]['creativity'] = 0
        player_hand[card_index]['appearance'] = 0
        player_hand[card_index]['image_path'] = "assets/photos/default.jpg"

        return card_backup

    def play_turn(self, plays: list, attribute: str):
        message = ["__________________________________________", f"Atributo da rodada: {attribute}"]
        for play in plays:
            print(f"Jogador {play[0]} jogou a carta {play[1]}")
            player_id = play[0]
            card_index = play[1]

            # Remove a carta jogada
            card_played = self.remove_card(player_id, card_index)

            # Adiciona a carta ao tabuleiro
            self.board.add_card(card_played, player_id)

            card_info = (f"Carta jogada: {card_played.name}, pelo jogador {player_id}\n"
                         f"Inteligência: {card_played.intelligence}\n"
                         f"Carisma: {card_played.charisma}\nEsporte: {card_played.sport}\n"
                         f"Humor: {card_played.humor}\nCriatividade: {card_played.creativity}\n"
                         f"Aparência: {card_played.appearance}\n")
            message.append(card_info)

        # Declara o vencedor da rodada e adiciona à mensagem
        winner_info = self.board.declare_round_winner(attribute)

        if self.my_id in winner_info:
            winner_round_message = "Você ganhou 1 ponto. Boa escolha!"
        else:
            winner_round_message = "Você perdeu!"

        message.append(winner_round_message)

        self.turn += 1

        # Verifica se o jogo deve terminar e adiciona à mensagem
        if self.turn == NUMERO_TURNOS:
            winner = self.board.declare_winner()
            messagebox.showinfo("Resultado da Rodada", "\n".join(message))
            return winner

        # Mostra a mensagem em um único popup
        messagebox.showinfo("Resultado da Rodada", "\n".join(message))
        return -1


def start_gui():
    root = tk.Tk()
    root.withdraw()
    root.mainloop()


if __name__ == "__main__":
    start_gui()
