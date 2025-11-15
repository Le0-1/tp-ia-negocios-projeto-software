"""
Dashboard de Qualidade do Ar em Cidades Brasileiras

Aplicativo Streamlit para visualizar dados de qualidade do ar
obtidos da API OpenAQ v3 para cidades brasileiras.
"""

import streamlit as st
import pandas as pd
import os
from dotenv import load_dotenv
from modules.data_fetcher import fetch_air_quality_data, get_available_cities, get_api_key
from modules.data_processor import process_data, get_latest_measurements, pivot_data_by_parameter
from modules.visualizer import plot_time_series, plot_bar_chart, format_parameter_name

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

def get_api_key_from_streamlit():
    """
    Obtém a chave de API do Streamlit Cloud secrets ou variável de ambiente.
    Prioriza secrets do Streamlit Cloud.
    """
    api_key = None
    debug_info = []
    
    # Tenta obter dos secrets do Streamlit Cloud primeiro
    try:
        if hasattr(st, 'secrets'):
            debug_info.append("st.secrets existe")
            
            # O objeto Secrets tem métodos: get, has_key, keys, etc.
            # Primeiro verifica se a chave existe
            if hasattr(st.secrets, 'has_key') and st.secrets.has_key('OPENAQ_API_KEY'):
                debug_info.append("Chave encontrada via has_key")
                api_key = st.secrets.get('OPENAQ_API_KEY')
                debug_info.append("Acessado via st.secrets.get()")
            elif hasattr(st.secrets, 'get'):
                # Tenta usar get diretamente (pode retornar None se não existir)
                api_key = st.secrets.get('OPENAQ_API_KEY')
                if api_key:
                    debug_info.append("Acessado via st.secrets.get() (sucesso)")
                else:
                    debug_info.append("st.secrets.get() retornou None")
            else:
                # Tenta acessar como atributo
                try:
                    api_key = st.secrets.OPENAQ_API_KEY
                    debug_info.append("Acessado via st.secrets.OPENAQ_API_KEY")
                except AttributeError:
                    debug_info.append("Erro ao acessar como atributo")
                    # Tenta como dict
                    try:
                        api_key = st.secrets['OPENAQ_API_KEY']
                        debug_info.append("Acessado via st.secrets['OPENAQ_API_KEY']")
                    except (KeyError, TypeError):
                        debug_info.append("Erro ao acessar como dict")
        else:
            debug_info.append("st.secrets NÃO existe")
    except Exception as e:
        debug_info.append(f"Exceção geral: {str(e)}")
    
    # Se não encontrou nos secrets, tenta variável de ambiente
    if not api_key:
        env_key = get_api_key()
        if env_key:
            api_key = env_key
            debug_info.append("Usando variável de ambiente")
        else:
            debug_info.append("Nenhuma chave encontrada")
    
    # Log de debug (visível nos logs do Streamlit Cloud)
    if api_key:
        print(f"✅ API Key encontrada! (Debug: {' | '.join(debug_info)})")
    else:
        print(f"❌ API Key NÃO encontrada! (Debug: {' | '.join(debug_info)})")
        # Tenta listar todos os secrets disponíveis para debug
        try:
            if hasattr(st, 'secrets'):
                if hasattr(st.secrets, 'keys'):
                    try:
                        keys_list = list(st.secrets.keys())
                        print(f"Secrets disponíveis: {keys_list}")
                    except:
                        print("Não foi possível listar as chaves dos secrets")
                elif isinstance(st.secrets, dict):
                    print(f"Secrets disponíveis (dict): {list(st.secrets.keys())}")
        except Exception as e:
            print(f"Erro ao listar secrets: {str(e)}")
    
    return api_key

# Cache para a lista de cidades (evita recarregar toda vez)
@st.cache_data(ttl=3600)  # Cache por 1 hora
def get_cached_cities(api_key):
    """Busca cidades disponíveis com cache."""
    return get_available_cities("BR", api_key)

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Qualidade do Ar",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Título principal
st.title("🌬️ Dashboard de Qualidade do Ar em Cidades Brasileiras")
st.markdown("---")

# Sidebar com informações e seleção de cidade
with st.sidebar:
    st.header("⚙️ Configurações")
    
    # Obtém a chave de API (prioriza secrets do Streamlit Cloud, depois variável de ambiente)
    api_key = get_api_key_from_streamlit()
    
    # Busca cidades disponíveis na API
    st.subheader("Selecione a Cidade")
    
    if api_key:
        # Debug: mostra que a chave foi encontrada (apenas no primeiro carregamento)
        if 'api_key_loaded' not in st.session_state:
            st.session_state.api_key_loaded = True
            st.success("✅ Chave de API carregada com sucesso!")
        
        # Usa cache para evitar recarregar toda vez
        available_cities = get_cached_cities(api_key)
        
        if available_cities and len(available_cities) > 0:
            # Se a função retornar lista de dicionários, extrai os nomes de display
            if isinstance(available_cities[0], dict):
                city_options = [city['display'] for city in available_cities]
                city_names = {city['display']: city['name'] for city in available_cities}
            else:
                # Compatibilidade com formato antigo (lista de strings)
                city_options = available_cities
                city_names = {city: city for city in available_cities}
            
            # Encontra o índice de São Paulo se disponível
            default_index = 0
            for i, option in enumerate(city_options):
                if 'São Paulo' in option or 'sao paulo' in option.lower():
                    default_index = i
                    break
            
            selected_city_display = st.selectbox(
                "Escolha uma cidade:",
                options=city_options,
                index=default_index,
                help="Apenas cidades com dados disponíveis na API OpenAQ são exibidas"
            )
            
            # Converte o display name de volta para o nome real da cidade (remove estado se presente)
            selected_city = city_names.get(selected_city_display, selected_city_display)
            # Remove o estado do nome se estiver presente (ex: "São Paulo - SP" -> "São Paulo")
            if ' - ' in selected_city:
                selected_city = selected_city.split(' - ')[0]
        else:
            st.error("❌ Não foi possível carregar as cidades disponíveis.")
            st.info("Verifique sua conexão com a internet e a chave de API.")
            selected_city = None
    else:
        st.error("❌ Chave de API não configurada!")
        st.warning("""
        **Problema:** A chave de API não foi encontrada.
        
        **Verifique:**
        1. No Streamlit Cloud, vá em **Settings** → **Secrets**
        2. Certifique-se de que o formato está correto:
           ```toml
           [secrets]
           OPENAQ_API_KEY = "sua_chave_aqui"
           ```
        3. Aguarde 1-2 minutos após salvar
        4. Recarregue a página (F5)
        
        **Para ver os logs:**
        - No Streamlit Cloud, vá em **Manage app** → **Logs**
        - Os logs mostrarão informações de debug sobre a busca da chave
        """)
        
        # Mostra informações de debug
        with st.expander("🔍 Informações de Debug"):
            st.write("**Status dos Secrets:**")
            try:
                if hasattr(st, 'secrets'):
                    st.write("✅ `st.secrets` está disponível")
                    st.write(f"Tipo: {type(st.secrets)}")
                    
                    # Tenta listar as chaves disponíveis
                    try:
                        if hasattr(st.secrets, 'keys'):
                            keys_list = list(st.secrets.keys())
                            st.write(f"**Chaves disponíveis:** {keys_list}")
                            
                            # Verifica especificamente se OPENAQ_API_KEY existe
                            if hasattr(st.secrets, 'has_key'):
                                has_key = st.secrets.has_key('OPENAQ_API_KEY')
                                st.write(f"**OPENAQ_API_KEY existe?** {'✅ Sim' if has_key else '❌ Não'}")
                            
                            # Tenta obter o valor
                            if 'OPENAQ_API_KEY' in keys_list:
                                try:
                                    key_value = st.secrets.get('OPENAQ_API_KEY')
                                    if key_value:
                                        st.write(f"**Valor encontrado:** {key_value[:10]}... (primeiros 10 caracteres)")
                                    else:
                                        st.write("**Valor:** None ou vazio")
                                except Exception as e:
                                    st.write(f"**Erro ao obter valor:** {str(e)}")
                        elif isinstance(st.secrets, dict):
                            st.write(f"Tipo: dict")
                            st.write(f"Chaves disponíveis: {list(st.secrets.keys())}")
                        else:
                            st.write(f"Atributos públicos: {[attr for attr in dir(st.secrets) if not attr.startswith('_')]}")
                    except Exception as e:
                        st.write(f"Erro ao inspecionar: {str(e)}")
                else:
                    st.write("❌ `st.secrets` NÃO está disponível")
            except Exception as e:
                st.write(f"Erro: {str(e)}")
            
            st.write("\n**Variável de Ambiente:**")
            env_key = get_api_key()
            if env_key:
                st.write(f"✅ Encontrada (primeiros 10 caracteres: {env_key[:10]}...)")
            else:
                st.write("❌ Não encontrada")
        
        selected_city = None
    
    st.markdown("---")
    st.info("💡 Este dashboard utiliza dados da API OpenAQ v3 para exibir informações sobre qualidade do ar em tempo real.")
    
    # Botão para atualizar dados
    refresh_button = st.button("🔄 Atualizar Dados", type="primary")

# Área principal do aplicativo
if selected_city:
    # Verifica novamente a chave de API (pode ter mudado)
    if not api_key:
        api_key = get_api_key_from_streamlit()
    
    # Verifica se a chave de API está configurada
    if not api_key:
        st.error("❌ Chave de API não configurada!")
        st.warning("""
        **Configuração necessária:**
        
        Configure a variável de ambiente `OPENAQ_API_KEY` com sua chave de API.
        
        **Para desenvolvimento local:**
        1. Crie um arquivo `.env` na raiz do projeto
        2. Adicione: `OPENAQ_API_KEY=sua_chave_aqui`
        
        **Para deploy:**
        Configure a variável de ambiente na plataforma de hospedagem.
        """)
        st.stop()
    
    # Mostra indicador de carregamento
    with st.spinner(f"Buscando dados de qualidade do ar para {selected_city}..."):
        # Busca dados da API v3
        data = fetch_air_quality_data(selected_city, country="BR", limit=100, api_key=api_key)
    
    if data:
        # Processa os dados
        df = process_data(data)
        
        if df is not None and not df.empty:
            # Obtém medições mais recentes
            latest_measurements = get_latest_measurements(df)
            
            # Exibe informações da cidade
            st.header(f"📊 Dados de Qualidade do Ar - {selected_city}")
            
            # Seção de indicadores atuais
            if latest_measurements:
                st.subheader("📈 Indicadores Atuais")
                
                # Cria colunas para os indicadores
                num_params = len(latest_measurements)
                cols = st.columns(min(num_params, 4))
                
                for idx, (param, measurement) in enumerate(latest_measurements.items()):
                    with cols[idx % len(cols)]:
                        value = measurement['value']
                        unit = measurement.get('unit', 'μg/m³')
                        param_display = format_parameter_name(param)
                        
                        # Define cor baseada no valor (exemplo simplificado)
                        if param.lower() == 'pm25':
                            if value <= 12:
                                color = "🟢"
                            elif value <= 35:
                                color = "🟡"
                            else:
                                color = "🔴"
                        elif param.lower() == 'o3':
                            if value <= 100:
                                color = "🟢"
                            elif value <= 160:
                                color = "🟡"
                            else:
                                color = "🔴"
                        else:
                            color = "⚪"
                        
                        st.metric(
                            label=f"{color} {param_display}",
                            value=f"{value:.2f} {unit}"
                        )
                
                st.markdown("---")
            
            # Seção de visualizações
            st.subheader("📉 Visualizações")
            
            # Tabs para diferentes visualizações
            tab1, tab2, tab3 = st.tabs(["📈 Série Temporal", "📊 Gráfico de Barras", "📋 Dados Brutos"])
            
            with tab1:
                st.write("**Evolução dos níveis de poluição ao longo do tempo**")
                fig_time = plot_time_series(df, title=f"Níveis de Poluição - {selected_city}")
                if fig_time:
                    st.pyplot(fig_time)
                else:
                    st.warning("Não foi possível gerar o gráfico de série temporal.")
            
            with tab2:
                if latest_measurements:
                    st.write("**Medições mais recentes de cada parâmetro**")
                    fig_bar = plot_bar_chart(
                        latest_measurements,
                        title=f"Medições Atuais - {selected_city}"
                    )
                    if fig_bar:
                        st.pyplot(fig_bar)
                    else:
                        st.warning("Não foi possível gerar o gráfico de barras.")
                else:
                    st.warning("Não há medições recentes disponíveis.")
            
            with tab3:
                st.write("**Dados brutos da API**")
                
                # Mostra estatísticas básicas
                if 'parameter' in df.columns:
                    st.write("**Estatísticas por Parâmetro:**")
                    stats_df = df.groupby('parameter')['value'].agg(['mean', 'min', 'max', 'std']).round(2)
                    st.dataframe(stats_df, width='stretch')
                
                st.write("**Últimos registros:**")
                # Mostra as últimas 20 linhas
                display_df = df[['datetime', 'parameter', 'value', 'unit']].head(20) if 'unit' in df.columns else df[['datetime', 'parameter', 'value']].head(20)
                st.dataframe(display_df, width='stretch')
                
                # Botão para download dos dados
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 Download dos Dados (CSV)",
                    data=csv,
                    file_name=f"qualidade_ar_{selected_city.lower().replace(' ', '_')}.csv",
                    mime="text/csv"
                )
            
            # Informações adicionais
            st.markdown("---")
            with st.expander("ℹ️ Sobre os Parâmetros"):
                st.markdown("""
                **PM₂.₅ (Material Particulado 2.5):** Partículas finas com diâmetro menor que 2.5 micrômetros.
                - Boa: ≤ 12 μg/m³
                - Moderada: 12-35 μg/m³
                - Ruim: > 35 μg/m³
                
                **PM₁₀ (Material Particulado 10):** Partículas com diâmetro menor que 10 micrômetros.
                
                **O₃ (Ozônio):** Gás formado por reações químicas na atmosfera.
                - Boa: ≤ 100 μg/m³
                - Moderada: 100-160 μg/m³
                - Ruim: > 160 μg/m³
                
                **NO₂ (Dióxido de Nitrogênio):** Gás tóxico produzido principalmente por veículos.
                
                **SO₂ (Dióxido de Enxofre):** Gás produzido pela queima de combustíveis fósseis.
                """)
        
        else:
            st.error("❌ Não foi possível processar os dados recebidos da API.")
            st.info("💡 Tente selecionar outra cidade ou verifique se há dados disponíveis para esta cidade.")
    
    else:
        st.error("❌ Não foi possível obter dados para esta cidade.")
        st.warning("""
        **Possíveis causas:**
        
        1. **A cidade não possui dados disponíveis na API OpenAQ**
           - A API OpenAQ tem dados limitados para cidades brasileiras
           - Atualmente, apenas algumas cidades têm dados disponíveis:
             - ✅ **São Paulo** (14 locations)
             - ✅ **Rio de Janeiro** (17 locations)
             - ✅ Campinas, Guarulhos, Santos e outras cidades menores
        
        2. **Problema de conexão com a API**
           - Verifique sua conexão com a internet
           - A API OpenAQ pode estar temporariamente indisponível
        
        **Sugestões:**
        - Tente selecionar **São Paulo** ou **Rio de Janeiro** (cidades com dados disponíveis)
        - Verifique os logs no terminal para mais detalhes
        - Consulte a documentação da API: https://docs.openaq.org/
        
        **Nota:** Infelizmente, a API OpenAQ não possui dados para todas as cidades brasileiras.
        Cidades como Belo Horizonte, Brasília, Curitiba, Porto Alegre e Fortaleza não têm
        dados disponíveis na API no momento.
        """)

else:
    st.info("👈 Selecione uma cidade na barra lateral para visualizar os dados de qualidade do ar.")

# Rodapé
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Dados fornecidos por <a href='https://openaq.org' target='_blank'>OpenAQ</a> | 
        Desenvolvido com Streamlit</p>
    </div>
    """,
    unsafe_allow_html=True
)

