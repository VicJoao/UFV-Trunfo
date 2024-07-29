# model.py

class Model:
    def __init__(self):
        self.data = "Initial Data"

    def update_data(self, new_data):
        self.data = new_data

    def get_data(self):
        return self.data
