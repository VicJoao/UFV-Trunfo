import sqlite3
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
                            user_id INTEGER,
                            name TEXT NOT NULL,
                            intelligence INTEGER,
                            charisma INTEGER,
                            sport INTEGER,
                            humor INTEGER,
                            creativity INTEGER,
                            appearance INTEGER,
                            FOREIGN KEY(user_id) REFERENCES client(id)
                        )''')

            # Criar tabela de deck (associando cartas aos usuários)
            c.execute('''CREATE TABLE IF NOT EXISTS deck (
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

    def create_user(self, name):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("INSERT INTO client (name) VALUES (?)", (name,))
            conn.commit()
            c.execute("SELECT id FROM client WHERE name = ?", (name,))
            user_id = c.fetchone()[0]
            return user_id
        except sqlite3.Error as e:
            print(f"Erro ao criar usuário: {e}")
            return None
        finally:
            conn.close()

    def create_card(self, user_id, name, intelligence, charisma, sport, humor, creativity, appearance):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute('''INSERT INTO cards (user_id, name, intelligence, charisma, sport, humor, creativity, appearance)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
                        (user_id, name, intelligence, charisma, sport, humor, creativity, appearance))
            conn.commit()
        except sqlite3.Error as e:
            print(f"Erro ao criar carta: {e}")
        finally:
            conn.close()

    def add_card_to_deck(self, user_id, card_name):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("SELECT id FROM cards WHERE user_id = ? AND name = ?", (user_id, card_name))
            card_id = c.fetchone()[0]
            c.execute("INSERT INTO deck (user_id, card_id) VALUES (?, ?)", (user_id, card_id))
            conn.commit()

        except sqlite3.Error as e:
            print(f"Erro ao adicionar carta ao deck: {e}")
        finally:
            conn.close()

    def remove_card_from_deck(self, user_id, card_name):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute("SELECT id FROM cards WHERE user_id = ? AND name = ?", (user_id, card_name))
            card_id = c.fetchone()[0]
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

    def get_user_deck(self, user_id):
        try:
            conn = sqlite3.connect(self.database)
            c = conn.cursor()

            c.execute('''SELECT cards.*
                         FROM cards
                         JOIN deck ON cards.id = deck.card_id
                         WHERE deck.user_id = ?''', (user_id,))
            deck_cards = [Card(card[2], card[3], card[4], card[5], card[6], card[7], card[8]) for card in c.fetchall()]
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

            c.execute('''SELECT * FROM cards WHERE user_id = ?''', (user_id,))
            cards = [Card(card[2], card[3], card[4], card[5], card[6], card[7], card[8]) for card in c.fetchall()]
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
