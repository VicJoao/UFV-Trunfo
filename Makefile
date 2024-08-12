# Nome do ambiente virtual
VENV_DIR = venv

# Comando para ativar o ambiente virtual
ACTIVATE = source $(VENV_DIR)/bin/activate

# Nome do pacote principal
PACKAGE = UFV-Trunfo

# Alvo padrão
all: install run

# Criar o ambiente virtual e instalar as dependências
$(VENV_DIR)/bin/activate: requirements.txt
	python3 -m venv $(VENV_DIR)
	$(ACTIVATE) && pip install --upgrade pip
	$(ACTIVATE) && pip install -r requirements.txt

# Instalar as dependências
install: $(VENV_DIR)/bin/activate

# Rodar o projeto
run: install
	$(ACTIVATE) && python3 main.py

# Limpar arquivos temporários
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

# Remover o ambiente virtual
dist-clean: clean
	rm -rf $(VENV_DIR)

.PHONY: all install run clean dist-clean
