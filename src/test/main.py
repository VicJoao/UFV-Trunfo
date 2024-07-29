# main.py

from model import Model
from view import View
from controller import Controller
import threading


def main():
    model = Model()
    controller = Controller(model)
    view = View(controller)

    # Start controller thread
    controller_thread = threading.Thread(target=controller.run)
    controller_thread.start()

    # Run view in the main thread
    view.start()


if __name__ == "__main__":
    main()
