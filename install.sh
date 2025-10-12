
#!/bin/bash

echo "🚀 Instalando SmartAgent..."
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Verificar se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale Python 3.8+"
    exit 1
fi

echo -e "${BLUE}📦 Instalando dependências...${NC}"
pip install requests

echo ""
echo -e "${BLUE}🔧 Instalando SmartAgent...${NC}"
pip install -e .

echo ""
echo -e "${GREEN}✅ Instalação concluída!${NC}"
echo ""
echo "Para usar a biblioteca:"
echo "  from agent import Agent"
echo ""
echo "Exemplo:"
echo "  agent = Agent(model='groq')"
echo "  @agent.tool"
echo "  def minha_funcao():"
echo "      return 'Olá!'"
echo ""
