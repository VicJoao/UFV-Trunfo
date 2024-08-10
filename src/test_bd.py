import os
from models.client_model import ClientModel  # Certifique-se de que o caminho está correto para sua estrutura de diretórios

# Configuração do banco de dados existente
existing_db = 'src/client.db'  # Substitua pelo caminho correto do seu banco de dados existente

client_model = ClientModel(existing_db)

# Testar criação de usuário
user_id = client_model.create_user('Alice')
print(f"User ID for Alice: {user_id}")

user = client_model.get_user_by_name('Alice')
print(f"User Name: {user.name}")

# Testar criação de cartas
client_model.create_card('Card1', 8, 5, 6, 7, 4, 3, user_id)
user_deck = client_model.get_user_deck(user_id)
print("User's Deck Cards:")
for card in user_deck.cards:
    print(card.name)

# Testar remoção de cartas do deck
client_model.remove_card_from_deck(user_id, 'Card1')
user_deck = client_model.get_user_deck(user_id)
print("User's Deck Cards after removal:")
for card in user_deck.cards:
    print(card.name)

# Testar recuperação de todos os usuários e cartas
all_users = client_model.get_all_users()
print("All Users:")
for user in all_users:
    print(user)

all_cards = client_model.get_all_cards()
print("All Cards:")
for card in all_cards:
    print(card)