import Pyro5.api
import threading
import time
import random

from models.game_data import GameData

MAX_CLIENTS = 3


def _convert_to_serializable(game_data_compact):
    serializable_players_data = []
    for player_data in game_data_compact['players_data']:
        serializable_players_data.append({
            'name': player_data.name,
            'id': player_data.id,
            'address': player_data.address,
            'hand': player_data.hand
        })
    return {
        'player_id': game_data_compact['player_id'],
        'players_data': serializable_players_data
    }


@Pyro5.api.expose
class GameServer:
    def __init__(self):
        self.game_started = None
        self.turn_attribute = ''
        self.lock = threading.Lock()
        self.num_players = 0
        self.jogadas_no_turno = 0
        self.plays = []
        self.players_data = []
        self.clients = {}
        self.game_data = GameData()
        self.messages = []

        # Inicia a thread para verificar o número de jogadores
        self.check_players_thread = threading.Thread(target=self.check_players)
        self.check_players_thread.daemon = True
        self.check_players_thread.start()

        # Inicia a thread para verificar as jogadas
        self.check_plays_thread = threading.Thread(target=self.check_plays)
        self.check_plays_thread.daemon = True
        self.check_plays_thread.start()

    def ping(self, nome, pyroname):
        ns = Pyro5.api.locate_ns()
        ns.list(prefix="Client")
        self.clients[nome] = pyroname
        return "pong"

    def send_player_data(self, player_data):
        """Processa os dados do jogador recebidos do cliente."""
        with self.lock:
            self.num_players += 1
            self.players_data.append(player_data)
            self.game_data.add_player(player_data["Nome"], player_data["Deck"], player_data["pyroname"])

        return 0

    def start_game(self):
        """Inicia o jogo."""
        print("Iniciando o jogo...")

        self.turn_attribute = self.select_random_attribute()

        # Compacta os players_data
        for player in self.players_data:
            player_pyroname = player["pyroname"]
            game_data_compact = self.game_data.compact(player_pyroname)

            # Serializa o conteúdo de game_data_compact
            serializable_data = _convert_to_serializable(game_data_compact)

            client_proxy = Pyro5.api.Proxy(f"PYRONAME:{player_pyroname}")
            client_proxy.receive_game_data(serializable_data, self.turn_attribute)

    def check_players(self):
        """Verifica periodicamente o número de jogadores e inicia o jogo quando o número máximo é alcançado."""
        while True:
            time.sleep(1)
            with self.lock:
                if self.num_players >= MAX_CLIENTS:
                    if not hasattr(self, 'game_started') or not self.game_started:
                        print("Número máximo de jogadores alcançado. Iniciando o jogo...")
                        self.start_game()
                        self.game_started = True

    def play_card(self, option, my_id):
        """Processa a jogada do jogador."""
        print(f"Jogador {my_id} jogou a carta {option}")
        self.jogadas_no_turno += 1
        self.plays.append((my_id, option))

        return 0

    def check_plays(self):
        while True:
            time.sleep(1)
            with self.lock:
                if self.jogadas_no_turno == 3:
                    self.process_round()

    def process_round(self):
        """Processa o fim do turno."""
        print("Processando o fim do turno...")
        self.jogadas_no_turno = 0
        turn_attribute = self.get_current_attribute()
        next_turn_attribute = self.select_random_attribute()

        def send_results(client):
            """Envia os resultados para um cliente específico."""
            print(f"Enviando resultados para {client['pyroname']}")
            client_proxy = Pyro5.api.Proxy(f"PYRONAME:{client['pyroname']}")
            client_proxy.receive_round_results(self.plays, turn_attribute, next_turn_attribute)

        threads = []
        for client in self.players_data:
            thread = threading.Thread(target=send_results, args=(client,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

        self.plays = []
        self.jogadas_no_turno = 0

    def get_current_attribute(self):
        """Retorna o atributo da rodada atual."""
        return self.turn_attribute

    def select_random_attribute(self):
        attributes = ["Inteligência", "Carisma", "Esporte", "Humor", "Criatividade", "Aparência"]
        self.turn_attribute = random.choice(attributes)
        return self.turn_attribute

    def end_game(self):
        """Encerra o jogo."""
        print("Encerrando o jogo...")
        self.game_started = False
        self.num_players = 0
        self.players_data = []
        self.game_data = GameData()
        self.plays = []
        self.jogadas_no_turno = 0
        self.turn_attribute = ''
        return 0

    def disconnect_client(self, pyroname):
        def disconnect_and_notify(player):
            try:
                # Remove o player da lista
                self.players_data.remove(player)

                for remaining_player in self.players_data:
                    self.num_players = 0
                    client_proxy = Pyro5.api.Proxy(f"PYRONAME:{remaining_player['pyroname']}")
                    client_proxy.receive_disconnect()

            except Exception as e:
                print(f"Erro ao desconectar o jogador {player['pyroname']}: {e}")

        for player in self.players_data:
            if player['pyroname'] == pyroname:
                thread = threading.Thread(target=disconnect_and_notify, args=(player,))
                thread.start()

                thread.join()
                break
        self.end_game()

        return 0


