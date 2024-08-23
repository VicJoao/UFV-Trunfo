from models.user import User
import pygame
import tkinter as tk
from tkinter import messagebox, filedialog
import threading
import os
from PIL import Image

# def open_upload_dialog(callback, controller):
#     def run_upload():
#         selected_image_path = controller.upload_image_screen()
#         if selected_image_path:
#             callback(selected_image_path)
#     thread = threading.Thread(target=run_upload)
#     thread.start()

class ClientController:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.user = User()

        self.current_state = "0 - NONE"
        self.selected_image_path = None

    def load_state(self):
        if self.current_state == "0 - NONE":
            print("Loading state: 0 - NONE\nExiting...")
            sys.exit()
        elif self.current_state == "1 - MAIN MENU":
            self.view.main_menu(update=self.change_current_state,
                                background_path="assets/backgrounds/welcome.png")
        elif self.current_state == "2 - CREATE NEW USER":
            self.view.create_user(update=self.change_current_state,
                                  background_path="assets/backgrounds/new_user.png")
        elif self.current_state == "3 - SUBMIT NEW USER":
            self.submit_new_user()
        elif self.current_state == "4 - UPLOAD IMAGE":
            open_upload_dialog(self.on_image_uploaded, self)

        self.view.screen.draw_widgets()

    def on_image_uploaded(self, file_path):
        # Callback que é acionado quando a imagem é carregada
        self.selected_image_path = file_path
        print(f"Imagem carregada com sucesso: {file_path}")
        self.current_state = "2 - CREATE NEW USER"
        self.load_state()

    def upload_image_screen(self):
        print("[!] Upload image screen...")
        # root = tk.Tk()
        # root.withdraw()
        #
        # # Abre o filedialog e permite a seleção da imagem
        # file_path = filedialog.askopenfilename(
        #     title="Selecione uma imagem",
        #     filetypes=[("Image files", "*.jpg *.jpeg *.png")]
        # )
        #
        # if file_path:
        #     img = Image.open(file_path)
        #
        #     # Verifica se a pasta 'assets/selfies/' existe
        #     if not os.path.exists("assets/selfies/"):
        #         os.makedirs("assets/selfies/")
        #
        #     # Salva a imagem na pasta 'assets/selfies/'
        #     new_file_path = os.path.join("assets/selfies", os.path.basename(file_path))
        #     img.save(new_file_path)
        #
        #     root.quit()
        #     root.destroy()
        #     return new_file_path  # Retorna o caminho da imagem salva
        #
        # root.quit()
        # root.destroy()
        # return None  # Retorna None caso o upload seja cancelado

    def change_current_state(self, state):
        print(f"Changing state: {self.current_state} -> {state}")
        self.current_state = state
        self.load_state()

    def submit_new_user(self):
        print("[!] Submitting new user...")
        tk.Tk().wm_withdraw()
        # messagebox.showinfo("Florestrunfo", "User created successfully!")
        try:
            for i in range(1, len(self.view.screen.input_boxes)):
                print(self.view.screen.input_boxes[i].text)

        except ValueError:
            pass

    def run(self):
        pygame.init()
        pygame.display.set_caption("Florestrunfo")
        self.current_state = "1 - MAIN MENU"
        self.load_state()
