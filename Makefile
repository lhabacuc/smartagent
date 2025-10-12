
.PHONY: install dev test clean

install:
	@echo "📦 Instalando SmartAgent..."
	pip install -e .

dev:
	@echo "🔧 Instalando modo desenvolvimento..."
	pip install -e ".[dev]"

test:
	@echo "🧪 Executando testes..."
	python -m pytest tests/

clean:
	@echo "🧹 Limpando arquivos temporários..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "✅ Limpeza concluída"

uninstall:
	@echo "🗑️ Desinstalando SmartAgent..."
	pip uninstall -y smartagent

reinstall: uninstall clean install
	@echo "✅ Reinstalação concluída"
