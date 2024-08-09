from dotenv import load_dotenv
from controllers.client_controller import ClientController
from models.client_model import ClientModel
from views.client_view import ClientView
import os
def main():
    load_dotenv()
    client_db = os.getenv("CLIENT_DB")
    model = ClientModel(client_db)
    view = ClientView()

    app = ClientController(model, view)
    app.run()

if __name__ == "__main__":
    main()
