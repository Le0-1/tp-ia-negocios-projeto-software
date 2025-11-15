# 🚀 Guia de Deploy - Dashboard de Qualidade do Ar

Este guia explica como fazer o deploy do Dashboard de Qualidade do Ar em diferentes plataformas.

## 📋 Pré-requisitos

- Conta na plataforma de hospedagem escolhida
- Chave de API da OpenAQ (obtenha em: https://explore.openaq.org/register)
- Repositório Git configurado

## 🌐 Streamlit Cloud (Recomendado)

O Streamlit Cloud é a forma mais fácil de fazer deploy de aplicativos Streamlit.

### Passos:

1. **Faça push do código para o GitHub:**
   ```bash
   git add .
   git commit -m "Preparar para deploy"
   git push origin main
   ```

2. **Acesse o Streamlit Cloud:**
   - Vá para https://share.streamlit.io/
   - Faça login com sua conta GitHub

3. **Crie um novo app:**
   - Clique em "New app"
   - Selecione seu repositório
   - Escolha o branch (geralmente `main`)
   - Defina o arquivo principal: `app.py`

4. **Configure a variável de ambiente:**
   - No painel do app, vá em "Settings" → "Secrets"
   - Adicione no formato TOML (use aspas duplas e a seção [secrets]):
     ```toml
     [secrets]
     OPENAQ_API_KEY = "3125f0d41afec0ee8b1871165638fa7352734cd8e2afe085f54a446d7092f864"
     ```
   - **Importante:** 
     - O Streamlit Cloud requer formato TOML válido
     - Use `[secrets]` na primeira linha
     - Use aspas duplas ao redor do valor
     - Não use espaços antes ou depois do `=`
     - Após salvar, aguarde 1-2 minutos para as mudanças propagarem
     - Recarregue a página do app após salvar

5. **Deploy:**
   - Clique em "Deploy"
   - Aguarde o build e deploy
   - Seu app estará disponível em: `https://seu-usuario-streamlit-app.streamlit.app`

### 🔍 Ver Logs da Aplicação

Para ver os logs e debug da aplicação no Streamlit Cloud:

1. **Acesse o painel do app:**
   - Vá para [share.streamlit.io](https://share.streamlit.io)
   - Faça login e selecione seu app

2. **Acesse os logs:**
   - Clique no menu "☰" (três linhas) no canto superior direito
   - Selecione **"Manage app"**
   - Clique na aba **"Logs"**
   - Você verá todos os logs da aplicação, incluindo mensagens de debug

3. **O que procurar nos logs:**
   - Mensagens como `✅ API Key encontrada!` ou `❌ API Key NÃO encontrada!`
   - Informações sobre como a chave foi acessada
   - Lista de secrets disponíveis (se a chave não for encontrada)

### ⚠️ Troubleshooting

**Se a chave de API não estiver funcionando:**

1. **Verifique o formato TOML:**
   - Deve começar com `[secrets]` na primeira linha
   - Use aspas duplas ao redor do valor
   - Não use espaços extras

2. **Aguarde a propagação:**
   - Após salvar os secrets, aguarde 1-2 minutos
   - Recarregue a página do app (F5)

3. **Faça um redeploy:**
   - No painel do app, clique em "☰" → "Manage app"
   - Clique em "Reboot app" para reiniciar
   - Ou faça um novo commit e push para forçar redeploy

4. **Verifique os logs:**
   - Use a seção "🔍 Informações de Debug" no app
   - Ou veja os logs no painel do Streamlit Cloud

## ☁️ Heroku

### Passos:

1. **Instale o Heroku CLI:**
   ```bash
   # Ubuntu/Debian
   curl https://cli-assets.heroku.com/install.sh | sh
   ```

2. **Faça login no Heroku:**
   ```bash
   heroku login
   ```

3. **Crie um app Heroku:**
   ```bash
   heroku create seu-app-nome
   ```

4. **Configure a variável de ambiente:**
   ```bash
   heroku config:set OPENAQ_API_KEY=3125f0d41afec0ee8b1871165638fa7352734cd8e2afe085f54a446d7092f864
   ```

5. **Faça deploy:**
   ```bash
   git push heroku main
   ```

6. **Abra o app:**
   ```bash
   heroku open
   ```

## 🐳 Docker (Para qualquer plataforma)

### Criar Dockerfile:

O Dockerfile já está incluído no projeto. Para fazer build:

```bash
docker build -t dashboard-qualidade-ar .
docker run -p 8501:8501 -e OPENAQ_API_KEY=3125f0d41afec0ee8b1871165638fa7352734cd8e2afe085f54a446d7092f864 dashboard-qualidade-ar
```

### Deploy no Railway:

1. Conecte seu repositório GitHub ao Railway
2. Configure a variável de ambiente `OPENAQ_API_KEY`
3. O Railway detectará automaticamente o Dockerfile

### Deploy no Render:

1. Conecte seu repositório GitHub ao Render
2. Crie um novo "Web Service"
3. Configure:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
4. Configure a variável de ambiente `OPENAQ_API_KEY`

## 🔒 Segurança

⚠️ **IMPORTANTE:** Nunca commite o arquivo `.env` com sua chave de API real!

- O arquivo `.env` está no `.gitignore`
- Use `.env.example` como template
- Configure a chave de API como variável de ambiente na plataforma de deploy

## 📝 Checklist de Deploy

- [ ] Código commitado e enviado para o repositório
- [ ] Variável de ambiente `OPENAQ_API_KEY` configurada na plataforma
- [ ] Arquivo `.env` não está no repositório (verificado no `.gitignore`)
- [ ] Testes locais passaram
- [ ] App está funcionando após o deploy

## 🆘 Troubleshooting

### Erro: "Chave de API não configurada"
- Verifique se a variável de ambiente está configurada corretamente
- Reinicie o app após configurar a variável

### Erro: "401 Unauthorized"
- Verifique se a chave de API está correta
- Confirme que a chave está ativa na OpenAQ

### App não inicia
- Verifique os logs da plataforma
- Confirme que todas as dependências estão no `requirements.txt`

