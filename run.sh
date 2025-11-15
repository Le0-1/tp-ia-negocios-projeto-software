#!/bin/bash
# Script para executar o Dashboard de Qualidade do Ar

# Verifica se o ambiente virtual existe
if [ ! -d "venv" ]; then
    echo "❌ Ambiente virtual não encontrado!"
    echo "💡 Execute primeiro: bash setup.sh"
    exit 1
fi

# Ativa o ambiente virtual
source venv/bin/activate

# Verifica se o streamlit está instalado
if ! command -v streamlit &> /dev/null; then
    echo "❌ Streamlit não encontrado no ambiente virtual."
    echo "💡 Execute: bash setup.sh"
    exit 1
fi

# Executa o aplicativo
echo "🚀 Iniciando Dashboard de Qualidade do Ar..."
streamlit run app.py

