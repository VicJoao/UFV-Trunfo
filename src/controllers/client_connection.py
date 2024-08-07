import tkinter as tk
from tkinter import messagebox
import threading
import socket
import time


class ServerScanner:
    def __init__(self, root):
        self.root = root
        self.is_scanning = False
        self.servers = {}
        self.frame = tk.Frame(root)
        self.frame.pack(padx=10, pady=10)
        self.server_listbox = tk.Listbox(self.frame, width=50, height=10)
        self.server_listbox.pack()
        self.start_button = tk.Button(self.frame, text="Iniciar Escaneamento", command=self.start_scanning)
        self.start_button.pack(pady=5)
        self.stop_button = tk.Button(self.frame, text="Parar Escaneamento", command=self.stop_scanning)
        self.stop_button.pack(pady=5)
        self.stop_button.config(state=tk.DISABLED)
        self.connect_button = tk.Button(self.frame, text="Conectar ao Servidor", command=self.connect_to_server)
        self.connect_button.pack(pady=5)
        self.connect_button.config(state=tk.DISABLED)

    def start_scanning(self):
        self.is_scanning = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.server_listbox.delete(0, tk.END)
        self.servers.clear()
        self.scan_thread = threading.Thread(target=self.scan_for_servers)
        self.scan_thread.start()

    def stop_scanning(self):
        self.is_scanning = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def scan_for_servers(self):
        while self.is_scanning:
            for port in [4242]:
                self.check_port(port)
            time.sleep(5)

    def check_port(self, port):
        hosts = ['localhost']
        for host in hosts:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex((host, port))
                if result == 0:
                    s.sendall("NAME".encode('utf-8'))
                    name = s.recv(1024).decode('utf-8')
                    if not name:
                        name = f"{host}:{port}"
                    if host not in self.servers:
                        self.servers[host] = name
                        self.update_server_list(name)

    def update_server_list(self, server_name):
        self.server_listbox.insert(tk.END, server_name)
        self.connect_button.config(state=tk.NORMAL)

    def connect_to_server(self):
        selected_index = self.server_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Aviso", "Selecione um servidor para conectar.")
            return

        server_name = self.server_listbox.get(selected_index[0])
        host = next(key for key, value in self.servers.items() if value == server_name)
        port = 4242
        self.connect_to_host(host, port)

    def connect_to_host(self, host, port):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                s.sendall("CONNECT".encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                messagebox.showinfo("Conexão", response)
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível conectar ao servidor {host}:{port}. Erro: {e}")


def main():
    root = tk.Tk()
    root.title("Cliente de Conexão de Servidor")
    app = ServerScanner(root)
    root.mainloop()


if __name__ == "__main__":
    main()
