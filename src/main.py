from dotenv import load_dotenv
from controllers.client_controller import ClientController
import os
def main():
    load_dotenv()
    client_db = os.getenv("CLIENT_DB")
    app = ClientController(client_db)
    app.run()

if __name__ == "__main__":
    main()
