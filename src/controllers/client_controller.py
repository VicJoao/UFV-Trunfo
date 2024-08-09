import sys
from models.client_model import ClientModel
from views.client_view import ClientView
from models.user import User
from controllers.conection import Connection
class ClientController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.user = User()
        self.connection = Connection()

    def login(self, user, password):
        if user == "" and password == "":  # Simulação de autenticação
            self.view.mostrar_mensagem("Login realizado com sucesso!")
            self.view.root.destroy()  # Fecha a janela Tkinter
            self.game_view.start_game() #@TODO: Implementar a view do jogo
            # self.view.show_home_screen()
        else:
            self.view.mostrar_mensagem("Usuário ou senha inválidos.")

    def run(self):
        self.view.run()