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
    
    # Obtém a chave de API
    api_key = get_api_key()
    
    # Busca cidades disponíveis na API
    st.subheader("Selecione a Cidade")
    
    if api_key:
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
        st.info("Configure a variável de ambiente OPENAQ_API_KEY")
        selected_city = None
    
    st.markdown("---")
    st.info("💡 Este dashboard utiliza dados da API OpenAQ v3 para exibir informações sobre qualidade do ar em tempo real.")
    
    # Botão para atualizar dados
    refresh_button = st.button("🔄 Atualizar Dados", type="primary")

# Área principal do aplicativo
if selected_city:
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

