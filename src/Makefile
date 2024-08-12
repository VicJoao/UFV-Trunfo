# Nome do pacote principal
PACKAGE = UFV-Trunfo

# Alvo padrão: instala dependências e roda o projeto
.PHONY: all
all: install run

# Instalar as dependências
.PHONY: install
install:
	# Se você usar pip para instalação global
	pip install --upgrade pip
	pip install -r requirements.txt

	# Se você usar conda
	# conda install --file requirements.txt

# Rodar o projeto
.PHONY: run
run:
	python3 main.py &
	python3 main2.py &
	python3 main3.py &
	python3 run_server.py

# Limpar arquivos temporários
.PHONY: clean
clean:
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -r {} +

# Limpar todas as dependências instaladas (usado com pip)
.PHONY: dist-clean
dist-clean: clean
	pip uninstall -r requirements.txt -y

# Limpar ambiente conda
.PHONY: conda-clean
conda-clean: clean
	conda env remove --name $(PACKAGE)

