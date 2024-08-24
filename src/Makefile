SHELL := /bin/bash

# Nome do arquivo de requisitos
REQUIREMENTS_FILE = requirements.txt
VENV_DIR = venv
PYRO_PORT = 9090  # Porta padrão para o Pyro5 Name Server

# Alvo padrão: Instalar as dependências, rodar o Pyro5 Nameserver e o projeto
all: install run

# Alvo para verificar se o python3-venv está instalado
check_venv:
	@if ! dpkg -s python3-venv >/dev/null 2>&1; then \
		echo "python3-venv não está instalado."; \
		echo "Por favor, instale usando: sudo apt install python3-venv"; \
		exit 1; \
	fi

# Alvo para criar o ambiente virtual e instalar as dependências
$(VENV_DIR)/bin/activate: $(REQUIREMENTS_FILE) check_venv
	python3 -m venv $(VENV_DIR)
	@$(VENV_DIR)/bin/pip install --upgrade pip
	@$(VENV_DIR)/bin/pip install -r $(REQUIREMENTS_FILE)

# Alvo para instalar as dependências
install: $(VENV_DIR)/bin/activate

# Alvo para rodar o Pyro5 Nameserver
run_pyro5_ns:
	@clear
	@if lsof -Pi :$(PYRO_PORT) -sTCP:LISTEN -t >/dev/null ; then \
		echo "Pyro5 Name Server já está em execução na porta $(PYRO_PORT)."; \
	else \
		echo "Iniciando Pyro5 Name Server na porta $(PYRO_PORT)..."; \
		$(VENV_DIR)/bin/pyro5-ns -p $(PYRO_PORT) & \
	fi

# Alvo para rodar o projeto
run: install run_pyro5_ns
	@$(VENV_DIR)/bin/python3 main.py & \
	$(VENV_DIR)/bin/python3 main2.py & \
	$(VENV_DIR)/bin/python3 main3.py & \
	$(VENV_DIR)/bin/python3 run_server.py

# Alvo para limpar arquivos temporários
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

# Alvo para remover o ambiente virtual
dist-clean: clean
	rm -rf $(VENV_DIR)

.PHONY: all check_venv install run run_pyro5_ns clean dist-clean
