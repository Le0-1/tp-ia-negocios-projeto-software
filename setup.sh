#!/bin/bash
# Script de configuração do ambiente virtual para o Dashboard de Qualidade do Ar

echo "🌬️  Configurando ambiente virtual para o Dashboard de Qualidade do Ar"
echo ""

# Verifica se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Por favor, instale o Python 3 primeiro."
    exit 1
fi

echo "✅ Python 3 encontrado: $(python3 --version)"
echo ""

# Verifica se python3-venv está instalado
if ! python3 -m venv --help &> /dev/null; then
    echo "⚠️  python3-venv não está disponível."
    echo "📦 Instalando python3-venv..."
    sudo apt-get update && sudo apt-get install -y python3-venv python3-full
fi

# Cria o ambiente virtual
echo "📦 Criando ambiente virtual..."
python3 -m venv venv

if [ $? -ne 0 ]; then
    echo "❌ Erro ao criar ambiente virtual."
    echo "💡 Tente instalar: sudo apt-get install python3-venv python3-full"
    exit 1
fi

echo "✅ Ambiente virtual criado com sucesso!"
echo ""

# Ativa o ambiente virtual
echo "🔄 Ativando ambiente virtual..."
source venv/bin/activate

# Atualiza pip
echo "⬆️  Atualizando pip..."
pip install --upgrade pip

# Instala as dependências
echo "📥 Instalando dependências..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Configuração concluída com sucesso!"
    echo ""
    echo "📋 Próximos passos:"
    echo "   1. Ative o ambiente virtual: source venv/bin/activate"
    echo "   2. Execute o aplicativo: streamlit run app.py"
    echo "   3. Para desativar o ambiente: deactivate"
    echo ""
else
    echo "❌ Erro ao instalar dependências."
    exit 1
fi

