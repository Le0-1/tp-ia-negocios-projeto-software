"""
Módulos do Dashboard de Qualidade do Ar.

Este pacote contém os módulos responsáveis por:
- Buscar dados da API OpenAQ
- Processar e estruturar os dados
- Gerar visualizações
"""

from modules.data_fetcher import fetch_air_quality_data, get_available_cities, get_api_key
from modules.data_processor import process_data, get_latest_measurements, pivot_data_by_parameter
from modules.visualizer import plot_time_series, plot_bar_chart, format_parameter_name

__all__ = [
    # data_fetcher
    'fetch_air_quality_data',
    'get_available_cities',
    'get_api_key',
    # data_processor
    'process_data',
    'get_latest_measurements',
    'pivot_data_by_parameter',
    # visualizer
    'plot_time_series',
    'plot_bar_chart',
    'format_parameter_name',
]
