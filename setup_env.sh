#!/bin/bash
# Script para configurar o arquivo .env com a chave de API

echo "🔑 Configurando arquivo .env com a chave de API..."

# Cria o arquivo .env com a chave de API
cat > .env << EOF
# Chave de API da OpenAQ v3
OPENAQ_API_KEY=3125f0d41afec0ee8b1871165638fa7352734cd8e2afe085f54a446d7092f864
EOF

echo "✅ Arquivo .env criado com sucesso!"
echo ""
echo "⚠️  IMPORTANTE: O arquivo .env está no .gitignore e não será commitado."
echo "   Para deploy, configure a variável de ambiente OPENAQ_API_KEY na plataforma."

