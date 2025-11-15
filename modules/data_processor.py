"""
Módulo responsável por processar e estruturar os dados de qualidade do ar.

Este módulo contém funções para transformar os dados brutos da API
em estruturas adequadas para visualização e análise.
"""

import pandas as pd
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)


def process_data(data: Optional[List[Dict]]) -> Optional[pd.DataFrame]:
    """
    Processa os dados brutos da API e retorna um DataFrame estruturado.
    
    Args:
        data: Lista de dicionários com dados brutos da API OpenAQ
    
    Returns:
        DataFrame do pandas com os dados processados, ou None se não houver dados.
    """
    if not data or len(data) == 0:
        logger.warning("Nenhum dado para processar")
        return None
    
    try:
        # Converte para DataFrame
        df = pd.DataFrame(data)
        
        if df.empty:
            logger.warning("DataFrame vazio após conversão")
            return None
        
        # Extrai e converte a data (API OpenAQ v2 usa 'date' com estrutura aninhada)
        if 'date' in df.columns:
            if len(df) > 0 and isinstance(df['date'].iloc[0], dict):
                df['datetime'] = pd.to_datetime(df['date'].apply(lambda x: x.get('utc', '') if isinstance(x, dict) else x))
            else:
                df['datetime'] = pd.to_datetime(df['date'], errors='coerce')
        elif 'datetime' in df.columns:
            df['datetime'] = pd.to_datetime(df['datetime'], errors='coerce')
        else:
            logger.warning("Coluna de data não encontrada")
            return None
        
        # Remove linhas com data inválida
        df = df.dropna(subset=['datetime'])
        
        if df.empty:
            logger.warning("Nenhum dado válido após processamento de datas")
            return None
        
        # Garante que temos as colunas necessárias
        required_columns = ['parameter', 'value']
        missing_columns = [col for col in required_columns if col not in df.columns]
        
        if missing_columns:
            logger.warning(f"Colunas faltando: {missing_columns}")
            return None
        
        # Adiciona coluna 'location' se não existir (para evitar erro no drop_duplicates)
        if 'location' not in df.columns:
            if 'locationId' in df.columns:
                df['location'] = df['locationId']
            else:
                df['location'] = 'unknown'
        
        # Remove duplicatas e ordena por data
        subset_cols = ['datetime', 'parameter']
        if 'location' in df.columns:
            subset_cols.append('location')
        
        df = df.drop_duplicates(subset=subset_cols)
        df = df.sort_values('datetime')
        
        logger.info(f"Dados processados: {len(df)} registros")
        return df
        
    except Exception as e:
        logger.error(f"Erro ao processar dados: {str(e)}")
        return None


def get_latest_measurements(df: Optional[pd.DataFrame]) -> Optional[Dict]:
    """
    Extrai as medições mais recentes de cada parâmetro.
    
    Args:
        df: DataFrame com os dados processados
    
    Returns:
        Dicionário com os valores mais recentes de cada parâmetro, ou None.
    """
    if df is None or df.empty:
        return None
    
    try:
        # Pega a data mais recente
        latest_date = df['datetime'].max()
        latest_data = df[df['datetime'] == latest_date]
        
        # Cria dicionário com os valores mais recentes
        # Agrupa por parâmetro e pega a média se houver múltiplas medições
        measurements = {}
        for param in latest_data['parameter'].unique():
            param_data = latest_data[latest_data['parameter'] == param]
            avg_value = param_data['value'].mean()
            unit = param_data['unit'].iloc[0] if 'unit' in param_data.columns and len(param_data) > 0 else 'μg/m³'
            
            measurements[param] = {
                'value': float(avg_value),
                'unit': str(unit),
                'datetime': latest_date
            }
        
        return measurements
        
    except Exception as e:
        logger.error(f"Erro ao extrair medições mais recentes: {str(e)}")
        return None


def pivot_data_by_parameter(df: Optional[pd.DataFrame]) -> Optional[pd.DataFrame]:
    """
    Transforma os dados em formato pivoteado (parâmetros como colunas).
    
    Args:
        df: DataFrame com os dados processados
    
    Returns:
        DataFrame pivoteado com parâmetros como colunas, ou None.
    """
    if df is None or df.empty:
        return None
    
    try:
        # Agrupa por data e parâmetro, pegando a média dos valores
        pivot_df = df.pivot_table(
            index='datetime',
            columns='parameter',
            values='value',
            aggfunc='mean'
        )
        
        return pivot_df
        
    except Exception as e:
        logger.error(f"Erro ao pivotear dados: {str(e)}")
        return None

