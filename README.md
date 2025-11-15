# 🌬️ Dashboard de Qualidade do Ar em Cidades Brasileiras

Dashboard interativo desenvolvido em Python usando Streamlit para visualizar dados de qualidade do ar em tempo real para cidades brasileiras, utilizando dados da API OpenAQ.

## 📋 Descrição

Este projeto é um aplicativo web que permite aos usuários:
- Selecionar uma cidade brasileira
- Visualizar indicadores atuais de qualidade do ar (PM2.5, O3, NO2, SO2, etc.)
- Analisar gráficos de série temporal e barras
- Exportar dados em formato CSV

## 🚀 Instalação

### Pré-requisitos

- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)
- Chave de API da OpenAQ v3 (obtenha em: https://explore.openaq.org/register)

### Instalação do pip (se necessário)

Se o comando `pip` não estiver disponível, instale-o primeiro:

**Linux (Debian/Ubuntu):**
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

**Linux (Fedora/RHEL):**
```bash
sudo dnf install python3-pip
```

**Linux (Arch):**
```bash
sudo pacman -S python-pip
```

**Alternativa (usando ensurepip):**
```bash
python3 -m ensurepip --upgrade
```

### Passos para Instalação

1. **Navegue até o diretório do projeto:**
   ```bash
   cd projeto-cursor-ia
   ```

2. **Execute o script de configuração:**
   ```bash
   bash setup.sh
   ```
   
   Este script irá:
   - Criar o ambiente virtual automaticamente
   - Instalar todas as dependências
   - Configurar tudo para você

3. **Configure a chave de API:**
   ```bash
   bash setup_env.sh
   ```
   
   Ou crie manualmente o arquivo `.env`:
   ```bash
   echo "OPENAQ_API_KEY=sua_chave_aqui" > .env
   ```

4. **Execute o aplicativo:**
   ```bash
   bash run.sh
   ```
   
   O aplicativo abrirá automaticamente em `http://localhost:8501`

## 🎯 Como Usar

### Executar o Aplicativo

Execute o script:
```bash
bash run.sh
```

O aplicativo abrirá automaticamente em `http://localhost:8501`

### Usar o Dashboard

1. **Selecione uma cidade** na barra lateral (apenas cidades com dados disponíveis são exibidas)
2. **Visualize os indicadores** de qualidade do ar em tempo real
3. **Explore os gráficos** de série temporal e barras
4. **Baixe os dados** em CSV se desejar

### Parar o Aplicativo

Pressione `Ctrl+C` no terminal para parar o servidor.

## 📁 Estrutura do Projeto

```
projeto-cursor-ia/
├── app.py                      # Aplicativo principal Streamlit
├── requirements.txt            # Dependências do projeto
├── README.md                   # Documentação do projeto
├── setup.sh                    # Script de configuração do ambiente virtual
├── run.sh                      # Script para executar o aplicativo
├── pytest.ini                  # Configuração de testes
├── modules/                    # Módulos do projeto
│   ├── __init__.py
│   ├── data_fetcher.py        # Busca dados da API OpenAQ
│   ├── data_processor.py      # Processa e estrutura os dados
│   └── visualizer.py          # Gera visualizações
└── tests/                      # Testes unitários
    ├── __init__.py
    ├── test_data_fetcher.py
    ├── test_data_processor.py
    └── test_visualizer.py
```

## 🔧 Módulos

### `data_fetcher.py`
Responsável por fazer requisições à API OpenAQ e obter dados de qualidade do ar.

**Funções principais:**
- `fetch_air_quality_data(city, country, limit)`: Busca dados para uma cidade específica
- `get_available_cities(country)`: Lista cidades disponíveis na API

### `data_processor.py`
Processa os dados brutos da API e os transforma em estruturas adequadas para análise.

**Funções principais:**
- `process_data(data)`: Converte dados brutos em DataFrame do pandas
- `get_latest_measurements(df)`: Extrai as medições mais recentes
- `pivot_data_by_parameter(df)`: Transforma dados em formato pivoteado

### `visualizer.py`
Gera gráficos e visualizações dos dados de qualidade do ar.

**Funções principais:**
- `plot_time_series(df, title)`: Cria gráfico de série temporal
- `plot_bar_chart(measurements, title)`: Cria gráfico de barras
- `format_parameter_name(parameter)`: Formata nomes de parâmetros

## 📊 Parâmetros de Qualidade do Ar

O dashboard exibe os seguintes parâmetros (quando disponíveis):

- **PM₂.₅**: Material particulado fino (≤ 2.5 μm)
- **PM₁₀**: Material particulado (≤ 10 μm)
- **O₃**: Ozônio
- **NO₂**: Dióxido de nitrogênio
- **SO₂**: Dióxido de enxofre
- **CO**: Monóxido de carbono

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criação de aplicativos web interativos
- **Pandas**: Manipulação e análise de dados
- **Matplotlib**: Criação de gráficos e visualizações
- **Requests**: Requisições HTTP para a API OpenAQ
- **Pytest**: Framework de testes unitários

## 📡 API Utilizada

Este projeto utiliza a [API OpenAQ v3](https://docs.openaq.org/), uma plataforma aberta que fornece dados de qualidade do ar de várias fontes ao redor do mundo.

### ⚠️ Importante: Mudança na API

A API OpenAQ v2 foi **descontinuada em janeiro de 2025**. O projeto foi atualizado para usar a **API v3**, que requer autenticação com chave de API.

### 🔑 Configuração da Chave de API

**Obrigatório:** Este projeto requer uma chave de API da OpenAQ v3 para funcionar.

1. **Registre-se** em [explore.openaq.org/register](https://explore.openaq.org/register)
2. **Obtenha sua chave de API** no painel de controle
3. **Configure a chave** usando uma das opções abaixo:

   **Opção 1: Arquivo .env (recomendado para desenvolvimento)**
   ```bash
   # Crie um arquivo .env na raiz do projeto
   echo "OPENAQ_API_KEY=sua_chave_aqui" > .env
   ```

   **Opção 2: Variável de ambiente**
   ```bash
   export OPENAQ_API_KEY=sua_chave_aqui
   ```

## 🌐 Deploy

Este aplicativo pode ser implantado em várias plataformas. Consulte o arquivo [DEPLOY.md](DEPLOY.md) para instruções detalhadas de deploy em:

- **Streamlit Cloud** (recomendado - mais fácil)
- **Heroku**
- **Railway**
- **Render**
- **Docker** (qualquer plataforma)

**Importante para deploy:** Configure a variável de ambiente `OPENAQ_API_KEY` na plataforma de hospedagem.

## ⚠️ Tratamento de Erros

O aplicativo inclui tratamento de erros para:
- Falhas de conexão com a API
- Timeouts de requisição
- Cidades sem dados disponíveis
- Dados inválidos ou malformados

## 🧪 Testes

O projeto inclui testes unitários para todos os módulos principais.

### Executando os Testes

Para executar os testes, use o pytest:

```bash
# Executar todos os testes
pytest

# Executar testes com mais detalhes
pytest -v

# Executar um arquivo de teste específico
pytest tests/test_data_fetcher.py
```

### Estrutura de Testes

- `tests/test_data_fetcher.py`: Testes para busca de dados da API
- `tests/test_data_processor.py`: Testes para processamento de dados
- `tests/test_visualizer.py`: Testes para geração de visualizações

## 🔮 Melhorias Futuras

- [x] Implementação de testes unitários
- [ ] Cache de dados para melhor performance
- [ ] Comparação entre múltiplas cidades
- [ ] Alertas quando os níveis de poluição excedem limites seguros
- [ ] Histórico de dados com seleção de período
- [ ] Mapa interativo com localização das estações de monitoramento

## 📝 Licença

Este projeto foi desenvolvido para fins acadêmicos.

## 👨‍💻 Autor

Desenvolvido como parte de um trabalho acadêmico utilizando plataforma de IA.

## 🙏 Agradecimentos

- [OpenAQ](https://openaq.org) por fornecer dados abertos de qualidade do ar
- Comunidade Streamlit pelo excelente framework

