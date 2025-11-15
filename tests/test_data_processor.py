"""
Testes unitários para o módulo data_processor.
"""

import unittest
import pandas as pd
from datetime import datetime
from modules.data_processor import process_data, get_latest_measurements, pivot_data_by_parameter


class TestDataProcessor(unittest.TestCase):
    """Testes para as funções de processamento de dados."""
    
    def setUp(self):
        """Prepara dados de teste."""
        self.sample_data = [
            {
                'parameter': 'pm25',
                'value': 15.5,
                'unit': 'μg/m³',
                'date': {'utc': '2024-01-01T12:00:00Z'},
                'location': 'Location1'
            },
            {
                'parameter': 'pm25',
                'value': 18.2,
                'unit': 'μg/m³',
                'date': {'utc': '2024-01-01T13:00:00Z'},
                'location': 'Location1'
            },
            {
                'parameter': 'o3',
                'value': 120.0,
                'unit': 'μg/m³',
                'date': {'utc': '2024-01-01T12:00:00Z'},
                'location': 'Location1'
            },
            {
                'parameter': 'o3',
                'value': 125.5,
                'unit': 'μg/m³',
                'date': {'utc': '2024-01-01T13:00:00Z'},
                'location': 'Location1'
            }
        ]
    
    def test_process_data_success(self):
        """Testa processamento bem-sucedido de dados."""
        result = process_data(self.sample_data)
        
        # Verifica que retorna um DataFrame
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
        # Verifica colunas essenciais
        self.assertIn('datetime', result.columns)
        self.assertIn('parameter', result.columns)
        self.assertIn('value', result.columns)
        
        # Verifica que as datas foram convertidas
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result['datetime']))
    
    def test_process_data_empty_list(self):
        """Testa processamento com lista vazia."""
        result = process_data([])
        self.assertIsNone(result)
    
    def test_process_data_none(self):
        """Testa processamento com None."""
        result = process_data(None)
        self.assertIsNone(result)
    
    def test_process_data_removes_duplicates(self):
        """Testa que duplicatas são removidas."""
        # Adiciona dados duplicados
        duplicate_data = self.sample_data + [self.sample_data[0]]
        result = process_data(duplicate_data)
        
        # Verifica que não há duplicatas
        duplicates = result.duplicated(subset=['datetime', 'parameter', 'location'])
        self.assertFalse(duplicates.any())
    
    def test_get_latest_measurements_success(self):
        """Testa extração de medições mais recentes."""
        df = process_data(self.sample_data)
        result = get_latest_measurements(df)
        
        # Verifica que retorna um dicionário
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        
        # Verifica que contém os parâmetros
        self.assertIn('pm25', result)
        self.assertIn('o3', result)
        
        # Verifica estrutura dos dados
        self.assertIn('value', result['pm25'])
        self.assertIn('unit', result['pm25'])
        self.assertIn('datetime', result['pm25'])
        
        # Verifica que os valores são os mais recentes
        # O valor mais recente de pm25 deve ser 18.2
        self.assertEqual(result['pm25']['value'], 18.2)
    
    def test_get_latest_measurements_empty_dataframe(self):
        """Testa extração com DataFrame vazio."""
        empty_df = pd.DataFrame()
        result = get_latest_measurements(empty_df)
        self.assertIsNone(result)
    
    def test_get_latest_measurements_none(self):
        """Testa extração com None."""
        result = get_latest_measurements(None)
        self.assertIsNone(result)
    
    def test_pivot_data_by_parameter_success(self):
        """Testa pivotagem de dados por parâmetro."""
        df = process_data(self.sample_data)
        result = pivot_data_by_parameter(df)
        
        # Verifica que retorna um DataFrame
        self.assertIsNotNone(result)
        self.assertIsInstance(result, pd.DataFrame)
        self.assertFalse(result.empty)
        
        # Verifica que os parâmetros são colunas
        self.assertIn('pm25', result.columns)
        self.assertIn('o3', result.columns)
        
        # Verifica que o índice é datetime
        self.assertTrue(pd.api.types.is_datetime64_any_dtype(result.index))
    
    def test_pivot_data_by_parameter_empty_dataframe(self):
        """Testa pivotagem com DataFrame vazio."""
        empty_df = pd.DataFrame()
        result = pivot_data_by_parameter(empty_df)
        self.assertIsNone(result)
    
    def test_pivot_data_by_parameter_none(self):
        """Testa pivotagem com None."""
        result = pivot_data_by_parameter(None)
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

