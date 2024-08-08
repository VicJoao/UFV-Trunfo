import pickle

class Message:
    HANDSHAKE = 1
    CONNECT = 2
    PLAYER_DATA = 3
    DISCONNECT = 4
    TYPO_ERROR = 5

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
