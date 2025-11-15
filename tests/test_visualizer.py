"""
Testes unitários para o módulo visualizer.
"""

import unittest
import pandas as pd
from datetime import datetime, timedelta
from modules.visualizer import plot_time_series, plot_bar_chart, format_parameter_name
from modules.data_processor import process_data, pivot_data_by_parameter


class TestVisualizer(unittest.TestCase):
    """Testes para as funções de visualização."""
    
    def setUp(self):
        """Prepara dados de teste."""
        # Cria dados de teste
        dates = pd.date_range(start='2024-01-01', periods=5, freq='h')
        self.pivot_df = pd.DataFrame({
            'pm25': [15.5, 18.2, 16.8, 20.1, 17.5],
            'o3': [120.0, 125.5, 122.3, 128.0, 124.5]
        }, index=dates)
        
        # Cria dados no formato não-pivoteado
        self.sample_data = []
        for date in dates:
            self.sample_data.append({
                'parameter': 'pm25',
                'value': 15.5,
                'unit': 'μg/m³',
                'date': {'utc': date.isoformat() + 'Z'},
                'location': 'Location1'
            })
            self.sample_data.append({
                'parameter': 'o3',
                'value': 120.0,
                'unit': 'μg/m³',
                'date': {'utc': date.isoformat() + 'Z'},
                'location': 'Location1'
            })
        
        self.measurements = {
            'pm25': {
                'value': 17.5,
                'unit': 'μg/m³',
                'datetime': dates[-1]
            },
            'o3': {
                'value': 124.5,
                'unit': 'μg/m³',
                'datetime': dates[-1]
            }
        }
    
    def test_plot_time_series_with_pivot_data(self):
        """Testa criação de gráfico de série temporal com dados pivoteados."""
        fig = plot_time_series(self.pivot_df, "Teste de Série Temporal")
        
        # Verifica que retorna uma figura
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_plot_time_series_with_non_pivot_data(self):
        """Testa criação de gráfico de série temporal com dados não-pivoteados."""
        df = process_data(self.sample_data)
        fig = plot_time_series(df, "Teste de Série Temporal")
        
        # Verifica que retorna uma figura
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_plot_time_series_empty_dataframe(self):
        """Testa criação de gráfico com DataFrame vazio."""
        empty_df = pd.DataFrame()
        fig = plot_time_series(empty_df)
        self.assertIsNone(fig)
    
    def test_plot_time_series_none(self):
        """Testa criação de gráfico com None."""
        fig = plot_time_series(None)
        self.assertIsNone(fig)
    
    def test_plot_bar_chart_success(self):
        """Testa criação de gráfico de barras."""
        fig = plot_bar_chart(self.measurements, "Teste de Barras")
        
        # Verifica que retorna uma figura
        self.assertIsNotNone(fig)
        self.assertTrue(hasattr(fig, 'axes'))
    
    def test_plot_bar_chart_empty_dict(self):
        """Testa criação de gráfico com dicionário vazio."""
        fig = plot_bar_chart({})
        self.assertIsNone(fig)
    
    def test_plot_bar_chart_none(self):
        """Testa criação de gráfico com None."""
        fig = plot_bar_chart(None)
        self.assertIsNone(fig)
    
    def test_format_parameter_name_pm25(self):
        """Testa formatação do nome do parâmetro PM2.5."""
        result = format_parameter_name('pm25')
        self.assertEqual(result, 'PM₂.₅')
    
    def test_format_parameter_name_pm10(self):
        """Testa formatação do nome do parâmetro PM10."""
        result = format_parameter_name('pm10')
        self.assertEqual(result, 'PM₁₀')
    
    def test_format_parameter_name_o3(self):
        """Testa formatação do nome do parâmetro O3."""
        result = format_parameter_name('o3')
        self.assertEqual(result, 'O₃')
    
    def test_format_parameter_name_no2(self):
        """Testa formatação do nome do parâmetro NO2."""
        result = format_parameter_name('no2')
        self.assertEqual(result, 'NO₂')
    
    def test_format_parameter_name_so2(self):
        """Testa formatação do nome do parâmetro SO2."""
        result = format_parameter_name('so2')
        self.assertEqual(result, 'SO₂')
    
    def test_format_parameter_name_co(self):
        """Testa formatação do nome do parâmetro CO."""
        result = format_parameter_name('co')
        self.assertEqual(result, 'CO')
    
    def test_format_parameter_name_unknown(self):
        """Testa formatação de parâmetro desconhecido."""
        result = format_parameter_name('unknown_param')
        self.assertEqual(result, 'UNKNOWN_PARAM')
    
    def test_format_parameter_name_case_insensitive(self):
        """Testa que a formatação é case-insensitive."""
        result1 = format_parameter_name('PM25')
        result2 = format_parameter_name('pm25')
        result3 = format_parameter_name('Pm25')
        self.assertEqual(result1, 'PM₂.₅')
        self.assertEqual(result2, 'PM₂.₅')
        self.assertEqual(result3, 'PM₂.₅')


if __name__ == '__main__':
    unittest.main()

