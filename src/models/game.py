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
        # Concatena todas as mensagens em uma única string com quebras de linha
        message = []
        message.append("__________________________________________")
        message.append(f"Atributo da rodada: {attribute}")
        message.append("COMPARANDO AS CARTAS:")

        for play in plays:
            player_id = play[0]  # ID do jogador
            card_index = play[1]  # Índice da carta na mão do jogador

            # Remove a carta jogada
            card_played = self.remove_card(player_id, card_index)

            # Adiciona a carta ao tabuleiro
            self.board.add_card(card_played, player_id)

            # Adiciona informações sobre a carta jogada na mensagem
            # Convertendo card_played em string se não for string
            card_info = f"Carta jogada: {card_played.name}, pelo jogador {player_id}\nInteligência: {card_played.intelligence}\nCarisma: {card_played.charisma}\nEsporte: {card_played.sport}\nHumor: {card_played.humor}\nCriatividade: {card_played.creativity}\nAparência: {card_played.appearance}\n"
            message.append(card_info)


        # Declara o vencedor da rodada e adiciona à mensagem
        winner_info = self.board.declare_round_winner(attribute)
        # Acessa o primeiro elemento da lista winner_info
        winner_id = winner_info[0]

        # Compara winner_id com self.my_id
        # Verifica se self.my_id está dentro de winner_info
        if self.my_id in winner_info:
            winner_roud_message = "Você ganhou 1 ponto"
        else:
            winner_roud_message = "Você não ganhou 1 ponto"

        # Adiciona a mensagem à lista de mensagens
        message.append(winner_roud_message)

        # Incrementa o turno
        self.turn += 1


        # Verifica se o jogo deve terminar e adiciona à mensagem
        if self.turn == NUMERO_TURNOS:
            winner = self.board.declare_winner()
            # Mostra a mensagem em um único popup
            messagebox.showinfo("Resultado da Rodada", "\n".join(message))
            return winner

        # Mostra a mensagem em um único popup
        messagebox.showinfo("Resultado da Rodada", "\n".join(message))
        return -1


# Função para iniciar o Tkinter
def start_gui():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal, pois não precisamos dela

    # Aqui você pode iniciar o jogo e passar o Tkinter root para a classe Game, se necessário
    # Exemplo: game_instance = Game(data, id)

    root.mainloop()


if __name__ == "__main__":
    start_gui()
