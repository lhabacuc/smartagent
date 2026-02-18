
.PHONY: install dev test test-env clean

install:
	@echo "Instalando SmartAgent..."
	pip install -e .

dev:
	@echo "Instalando modo desenvolvimento..."
	pip install -e ".[dev]"

test:
	@echo "Executando testes..."
	@if [ -d tests ]; then \
		if python -c "import importlib.util,sys;sys.exit(0 if importlib.util.find_spec('pytest') else 1)"; then \
			python -m pytest tests/; \
		else \
			echo "pytest não encontrado, usando unittest."; \
			python -m unittest discover -s tests -p 'test_*.py'; \
		fi; \
	else \
		echo "Diretório tests/ não encontrado."; \
	fi

test-env:
	@echo "Criando/atualizando ambiente virtual de teste (.venv)..."
	@python3 -m venv .venv
	@. .venv/bin/activate && python -m ensurepip --upgrade >/dev/null 2>&1 || true
	@echo "Executando testes no .venv..."
	@. .venv/bin/activate && python -m unittest discover -s tests -p 'test_*.py'

clean:
	@echo "Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "Limpeza concluída"

uninstall:
	@echo "🗑️ Desinstalando SmartAgent..."
	pip uninstall -y smartagent-sf

reinstall: uninstall clean install
	@echo "Reinstalação concluída"

rer: clean uninstall install
