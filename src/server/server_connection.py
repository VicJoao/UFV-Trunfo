from random import randint
import socket
import threading
import time
import tqdm


def send_response(conn: socket.socket):
    with conn:
        msg = conn.recv(1024)
        name = msg.decode("utf8")
        print(f"Received name from client: {name}")  # Mensagem de depuração
        s = 0
        for _ in tqdm.tqdm(range(5)):
            s += randint(1, 100)
            time.sleep(0.25)
        response = f"Hello, {name}! Your number is: {s}"
        conn.sendall(response.encode("utf8"))
        print(f"Sent response to client: {response}")  # Mensagem de depuração


def main():
    print("Server is starting...")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("0.0.0.0", 4242))
        s.listen()
        print("Server is listening for connections...")
        while True:
            conn, addr = s.accept()
            print(f"Connected with {addr}")
            thread = threading.Thread(target=send_response, args=(conn,))
            thread.start()


if __name__ == "__main__":
    main()
