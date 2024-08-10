# from dotenv import load_dotenv
# from controllers.client_controller import ClientController
# import os
# def main():
#     load_dotenv()
#     client_db = os.getenv("CLIENT_DB")
#     app = ClientController(client_db)
#     app.run()
#
# if __name__ == "__main__":
#     main()

import sqlite3
import models.client_model as cm

if __name__ == "__main__":
    client = cm.ClientModel("src/client.db")
    client.add_card_to_deck(1, "miguel")
