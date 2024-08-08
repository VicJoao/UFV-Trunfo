import tkinter as tk
from tkinter import messagebox

class ClientView:
    def __init__(self, controller):
        self.controller = controller
        self.root = tk.Tk()
        self.root.title("Florestrunfo - Cliente")
        self.create_menu()
        self.create_login_screen()


    def create_menu(self):
        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self.file_menu = tk.Menu(self.menu)
        self.menu.add_cascade(label="File", menu=self.file_menu)

        menu_items = [
            {"label": "Back", "command": self.user_selection_menu},
            {"label": "Exit", "command": self.root.quit}
        ]

        self.add_menu_items(self.file_menu, menu_items)

    def add_menu_items(self, menu, items):
        for item in items:
            menu.add_command(label=item["label"], command=item["command"])

    def user_selection_menu(self):
        messagebox.showinfo("Menu", "Back selected")

    def create_login_screen(self):
        self.label_user = tk.Label(self.root, text="User:")
        self.label_user.pack()
        self.entry_user = tk.Entry(self.root)
        self.entry_user.pack()

        self.label_password = tk.Label(self.root, text="Password:")
        self.label_password.pack()
        self.entry_password = tk.Entry(self.root, show="*")
        self.entry_password.pack()

        self.btn_login = tk.Button(self.root, text="Login", command=self.login)
        self.btn_login.pack()


    def create_home_screen(self):
        self.label_menu = tk.Label(self.root, text="Menu")
        self.label_menu.pack()

        self.btn_create_new_card = tk.Button(self.root, text="Create New Card", command=self.controller.create_card)
        self.btn_create_new_card.pack()

        self.btn_show_all_cards = tk.Button(self.root, text="Show All Cards", command=self.controller.show_cards)
        self.btn_show_all_cards.pack()

        self.btn_edit_deck = tk.Button(self.root, text="Edit Deck", command=self.controller.edit_deck)
        self.btn_edit_deck.pack()

        self.btn_find_match = tk.Button(self.root, text="Find Match", command=self.controller.find_match)
        self.btn_find_match.pack()

        self.btn_create_match = tk.Button(self.root, text="Create Match", command=self.controller.create_match)
        self.btn_create_match.pack()


    def login(self):
        usuario = self.entry_user.get()
        senha = self.entry_password.get()
        self.controller.login(usuario, senha)

    def mostrar_mensagem(self, mensagem):
        messagebox.showinfo("Informação", mensagem)

    def run(self):
        self.root.mainloop()

    def show_home_screen(self):
        try: self.root.destroy()
        except: pass
        self.root = tk.Tk()

        self.create_home_screen()

