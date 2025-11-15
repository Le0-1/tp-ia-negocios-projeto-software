"""
Módulo responsável por gerar visualizações dos dados de qualidade do ar.

Este módulo contém funções para criar gráficos e visualizações
usando matplotlib e outras bibliotecas de visualização.
"""

import matplotlib.pyplot as plt
import pandas as pd
from typing import Optional
import logging
from modules.data_processor import pivot_data_by_parameter

logger = logging.getLogger(__name__)


def plot_time_series(df: Optional[pd.DataFrame], title: str = "Níveis de Poluição ao Longo do Tempo") -> Optional[plt.Figure]:
    """
    Cria um gráfico de série temporal dos dados de qualidade do ar.
    
    Args:
        df: DataFrame com os dados processados (deve ter coluna 'datetime' e colunas de parâmetros)
        title: Título do gráfico
    
    Returns:
        Figura do matplotlib, ou None em caso de erro.
    """
    if df is None or df.empty:
        logger.warning("Nenhum dado para visualizar")
        return None
    
    try:
        # Pivoteia os dados se necessário
        if 'parameter' in df.columns:
            df = pivot_data_by_parameter(df)
            if df is None:
                return None
        
        if df.empty:
            logger.warning("DataFrame vazio após pivot")
            return None
        
        # Cria a figura
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plota cada parâmetro
        for column in df.columns:
            ax.plot(df.index, df[column], marker='o', label=column, linewidth=2, markersize=4)
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Data e Hora', fontsize=12)
        ax.set_ylabel('Concentração (μg/m³)', fontsize=12)
        ax.legend(loc='best', frameon=True, shadow=True)
        ax.grid(True, alpha=0.3)
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        logger.info("Gráfico de série temporal criado com sucesso")
        return fig
        
    except Exception as e:
        logger.error(f"Erro ao criar gráfico de série temporal: {str(e)}")
        return None


def plot_bar_chart(measurements: Optional[dict], title: str = "Medições Atuais de Qualidade do Ar") -> Optional[plt.Figure]:
    """
    Cria um gráfico de barras com as medições mais recentes.
    
    Args:
        measurements: Dicionário com as medições mais recentes
        title: Título do gráfico
    
    Returns:
        Figura do matplotlib, ou None em caso de erro.
    """
    if not measurements:
        logger.warning("Nenhuma medição para visualizar")
        return None
    
    try:
        # Extrai parâmetros e valores
        parameters = list(measurements.keys())
        values = [measurements[param]['value'] for param in parameters]
        units = [measurements[param].get('unit', '') for param in parameters]
        
        # Cria a figura
        fig, ax = plt.subplots(figsize=(10, 6))
        
        # Cria o gráfico de barras
        bars = ax.bar(parameters, values, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd'])
        
        # Adiciona valores nas barras
        for i, (bar, value, unit) in enumerate(zip(bars, values, units)):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{value:.2f} {unit}',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')
        
        ax.set_title(title, fontsize=16, fontweight='bold')
        ax.set_xlabel('Parâmetro', fontsize=12)
        ax.set_ylabel('Concentração', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        logger.info("Gráfico de barras criado com sucesso")
        return fig
        
    except Exception as e:
        logger.error(f"Erro ao criar gráfico de barras: {str(e)}")
        return None


def format_parameter_name(parameter: str) -> str:
    """
    Formata o nome do parâmetro para exibição mais amigável.
    
    Args:
        parameter: Nome do parâmetro (ex: "pm25", "o3")
    
    Returns:
        Nome formatado (ex: "PM2.5", "O₃")
    """
    formatting_map = {
        'pm25': 'PM₂.₅',
        'pm10': 'PM₁₀',
        'o3': 'O₃',
        'no2': 'NO₂',
        'so2': 'SO₂',
        'co': 'CO'
    }
    
    return formatting_map.get(parameter.lower(), parameter.upper())

