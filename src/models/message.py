import pickle


class Message:
    ATRIBUTO = 1
    ENCERRAR = 2
    WINNER_SELECT_CARD = 3
    ANOTHER_TYPE = 4
    START_GAME = 5
    LISTEN_PORT = 6
    NEW_PLAYER = 7
    HANDSHAKE = 8
    CONNECT = 9
    PLAYER_DATA = 10
    DISCONNECT = 11
    TYPO_ERROR = 12
    PLAYER_LIST = 13
    CLIENT_PORT = 14
    PLAY = 15
    WINNER = 16

    def __init__(self, message_type, data):
        self.message_type = message_type
        self.data = data

    def to_bytes(self):
        data_bytes = pickle.dumps(self.data)
        length = len(data_bytes)
        return self.message_type.to_bytes(1, byteorder='big') + length.to_bytes(4, byteorder='big') + data_bytes

    @classmethod
    def from_bytes(cls, byte_data):
        message_type = byte_data[0]
        length = int.from_bytes(byte_data[1:5], byteorder='big')
        data = pickle.loads(byte_data[5:])
        return cls(message_type, data)
