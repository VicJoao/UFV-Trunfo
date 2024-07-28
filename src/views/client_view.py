# client_view.py
from models.deck import Deck
class ClientView:
    def display_menu(self):
        print("0 - Return to user selection")
        print("1 - Create new card")
        print("2 - Print all cards")
        print("3 - Edit Deck")
        print("4 - Start server")
        print("5 - Find server")

    def get_server_option(self):
        return int(input("Option: "))

    def get_server_name(self):
        return input("Enter the server name: ")

    def get_server_port(self):
        return int(input("Enter the server port: "))


    def get_option(self):
        return int(input("Option: "))

    def display_edit_deck(self):
        print("0 - Return to menu")
        print("1 - Add card to deck")
        print("2 - Remove card from deck")
        print("3 - Print deck")

    def display_user_cards(self, cards):
        if not cards:
            print("No cards available.")
            return

        print("Cards:")
        for i, card in enumerate(cards, start=1):
            print("-" * 20)
            print(f"{i}--{card.name}\n")
            print(f"  Intelligence: {card.intelligence}")
            print(f"  Charisma: {card.charisma}")
            print(f"  Sport: {card.sport}")
            print(f"  Humor: {card.humor}")
            print(f"  Creativity: {card.creativity}")
            print(f"  Appearance: {card.appearance}")
            print("-" * 20)

    def display_user_deck(self, deck):
        if not isinstance(deck, Deck):
            print("Invalid deck object.")
            return

        cards = deck.get_cards()

        if not cards:
            print("Empty deck.")
            return

        for i, card in enumerate(cards, start=1):
            print("-" * 20)
            print(f"{i}--{card.name}\n")
            print(f"  Intelligence: {card.intelligence}")
            print(f"  Charisma: {card.charisma}")
            print(f"  Sport: {card.sport}")
            print(f"  Humor: {card.humor}")
            print(f"  Creativity: {card.creativity}")
            print(f"  Appearance: {card.appearance}")
            print("-" * 20)

    def get_card_option(self):
        return int(input("Option: "))

    def display_user_selection(self, users):
        print("Select the username you want to load")
        print("0 - Exit")
        print("1 - Create new user")
        for i, user in enumerate(users):
            print(f"{i + 2} - {user[1]}")

    def get_user_option(self):
        try:
            return int(input("Option: "))
        except ValueError:
            return -1

    def get_username(self):
        return input("Enter the username: ")

    def get_card_attributes(self):
        intelligence = int(input("Enter the intelligence value: "))
        charisma = int(input("Enter the charisma value: "))
        sport = int(input("Enter the sport value: "))
        humor = int(input("Enter the humor value: "))
        creativity = int(input("Enter the creativity value: "))
        appearance = int(input("Enter the appearance value: "))
        return intelligence, charisma, sport, humor, creativity, appearance

    def display_message(self, message):
        print(message)

    def get_card_name(self):
        return input("Enter the card name: ")
