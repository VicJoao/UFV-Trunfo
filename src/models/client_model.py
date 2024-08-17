import sqlite3
import random
from models.card import Card
from models.deck import Deck
from models.user import User


class ClientModel:
    def __init__(self, client_db):
        self.database = client_db
        self.create_tables()

    def create_tables(self):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Criar tabela de clientes
            c.execute('''CREATE TABLE IF NOT EXISTS client (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL
                        )''')

            # Criar tabela de cartas
            c.execute('''CREATE TABLE IF NOT EXISTS cards (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            intelligence INTEGER,
                            charisma INTEGER,
                            sport INTEGER,
                            humor INTEGER,
                            creativity INTEGER,
                            appearance INTEGER
                        )''')

            c.execute('''CREATE TABLE IF NOT EXISTS client_id_card_id (
                            user_id INTEGER,
                            card_id INTEGER,
                            FOREIGN KEY(user_id) REFERENCES client(id),
                            FOREIGN KEY(card_id) REFERENCES cards(id),
                            PRIMARY KEY(user_id, card_id)
                        )''')

            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar tabelas: {e}")
        finally:
            conn.close()



    def add_card_to_deck(self, user_id, card_id):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Verificar se a carta existe
            c.execute('SELECT id FROM cards WHERE id = ?', (card_id,))
            result = c.fetchone()

            if result is None:
                print(f"Erro: Nenhuma carta encontrada com o ID '{card_id}'.")
                return

            # Verificar se a carta já está no deck do usuário
            c.execute('SELECT * FROM deck WHERE user_id = ? AND card_id = ?', (user_id, card_id))
            result = c.fetchone()

            if result:
                print(f"A carta com o ID '{card_id}' já está no deck do usuário com o ID '{user_id}'.")
                return

            # Adicionar a carta ao deck do usuário
            c.execute('INSERT INTO deck (user_id, card_id) VALUES (?, ?)', (user_id, card_id))
            conn.commit()

            print(f"Carta com o ID '{card_id}' adicionada ao deck do usuário com o ID '{user_id}'.")

        except sqlite3.Error as e:
            print(f"Erro ao adicionar carta ao deck: {e}")
        finally:
            if conn:
                conn.close()

    def link_cards_to_deck(self, user_id):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Seleciona todas as cartas associadas ao usuário
            c.execute("SELECT card_id FROM client_id_card_id WHERE user_id = ?", (user_id,))
            card_ids = [row[0] for row in c.fetchall()]

            if len(card_ids) < 6:
                raise ValueError("Não há cartas suficientes associadas ao usuário para adicionar ao deck.")

            # Seleciona aleatoriamente 6 cartas do usuário
            selected_card_ids = random.sample(card_ids, 6)

            # Adiciona as cartas selecionadas ao deck do usuário
            for card_id in selected_card_ids:
                c.execute("INSERT INTO deck (user_id, card_id) VALUES (?, ?)", (user_id, card_id))

            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao vincular cartas ao deck do usuário: {e}")
        except ValueError as e:
            print(e)
        finally:
            conn.close()

    def link_cards_to_user(self, user_id, card_ids):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            for card_id in card_ids:
                c.execute("INSERT INTO client_id_card_id (user_id, card_id) VALUES (?, ?)", (user_id, card_id))

            conn.commit()
            self.link_cards_to_deck(user_id)
        except sqlite3.Error as e:
            print(f"Erro ao vincular cartas ao usuário: {e}")

    def create_user(self, name):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("INSERT INTO client (name) VALUES (?)", (name,))
            conn.commit()
            c.execute("SELECT id FROM client WHERE name = ?", (name,))
            user_id = c.fetchone()[0]

            ids = [1, 2, 3, 4, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25]
            fixed_ids = [5, 6, 7, 8, 9, 10]

            # Seleciona aleatoriamente IDs suficientes para completar 10 no total
            remaining_ids = random.sample(ids, 10 - len(fixed_ids))

            # Combina os IDs fixos com os aleatórios
            card_ids = fixed_ids + remaining_ids

            # Agora você pode associar esses IDs ao usuário
            self.link_cards_to_user(user_id, card_ids)

            return user_id
        except sqlite3.Error as e:
            print(f"Erro ao criar usuário: {e}")
            return None
        finally:
            conn.close()

    def create_card(self, name, intelligence, charisma, sport, humor, creativity, appearance, image_path, user_id):
        global conn
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Criar a carta
            c.execute('''INSERT INTO cards (name, intelligence, charisma, sport, humor, creativity, appearance, image_path)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                      (name, intelligence, charisma, sport, humor, creativity, appearance, image_path))
            card_id = c.lastrowid  # Obter o ID da última carta criada

            # Adicionar a carta à tabela de conexões do usuário
            c.execute("INSERT INTO client_id_card_id (user_id, card_id) VALUES (?, ?)",
                      (user_id, card_id))

            conn.commit()  # Salvar (commit) as alterações no banco de dados
            return card_id  # Retornar o ID da carta criada

        except sqlite3.Error as e:
            print(f"Erro ao criar carta: {e}")
            return None

        finally:
            conn.close()

    def remove_card_from_deck(self, user_id, card_id):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Obter o ID da carta com base no nome
            c.execute("SELECT id FROM cards WHERE id = ?", (card_id,))
            result = c.fetchone()

            if result is None:
                print(f"Carta com nome '{card_id}' não encontrada.")
                return

            card_id = result[0]

            # Remover a carta do deck do usuário
            c.execute("DELETE FROM deck WHERE user_id = ? AND card_id = ?", (user_id, card_id))
            conn.commit()

        except sqlite3.Error as e:
            print(f"Erro ao remover carta do deck: {e}")
        finally:
            conn.close()

    def get_all_users(self):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("SELECT * FROM client")
            users = c.fetchall()
            return users
        except sqlite3.Error as e:
            print(f"Erro ao obter usuários: {e}")
        finally:
            conn.close()

    def get_user_by_name(self, name):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("SELECT * FROM client WHERE name = ?", (name,))
            user_data = c.fetchone()
            user_id = user_data[0]
            user = User()
            user.rename(user_data[0], user_data[1])
            user_cards = self.get_user_cards(user_id)
            user_deck = self.get_user_deck(user_id)
            user.initialize(user_cards, user_deck)
            return user
        except sqlite3.Error as e:
            print(f"Erro ao obter usuário por nome: {e}")
        finally:
            conn.close()

    # FAZER
    def get_user_deck(self, user_id):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute('''SELECT cards.*
                         FROM cards
                         JOIN deck ON cards.id = deck.card_id
                         WHERE deck.user_id = ?''', (user_id,))
            deck_cards = [Card(card[0], card[1], card[2], card[3], card[4], card[5], card[6], card[7]) for card in
                          c.fetchall()]

            deck = Deck()
            deck.create(deck_cards)
            return deck
        except sqlite3.Error as e:
            print(f"Erro ao obter deck do usuário: {e}")
        finally:
            conn.close()

    def get_user_cards(self, user_id):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            # Atualizar a consulta SQL conforme a estrutura da tabela cards
            c.execute('''SELECT id, name, intelligence, charisma, sport, humor, creativity, appearance 
                         FROM cards
                         JOIN client_id_card_id ON cards.id = client_id_card_id.card_id
                         WHERE client_id_card_id.user_id = ?''', (user_id,))

            # Supondo que a tabela cards não tem user_id e as colunas estão na ordem correta
            cards = [Card(card[0], card[1], card[2], card[3], card[4], card[5], card[6], card[7]) for card in
                     c.fetchall()]
            return cards
        except sqlite3.Error as e:
            print(f"Erro ao obter cartas do usuário: {e}")
        finally:
            conn.close()

    def get_all_cards(self):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("SELECT * FROM cards")
            cards = c.fetchall()
            return cards
        except sqlite3.Error as e:
            print(f"Erro ao obter cartas: {e}")
        finally:
            conn.close()
