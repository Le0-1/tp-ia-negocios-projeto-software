"""
Testes unitários para o módulo data_fetcher.
"""

import unittest
from unittest.mock import patch, Mock
from modules.data_fetcher import fetch_air_quality_data, get_available_cities


class TestDataFetcher(unittest.TestCase):
    """Testes para as funções de busca de dados."""
    
    @patch('modules.data_fetcher.get_api_key')
    @patch('modules.data_fetcher.requests.get')
    def test_fetch_air_quality_data_success(self, mock_get, mock_api_key):
        """Testa busca bem-sucedida de dados de qualidade do ar."""
        # Mock da chave de API
        mock_api_key.return_value = 'test_api_key'
        
        # Mock das respostas da API v3
        # Primeiro: busca de países
        mock_countries_response = Mock()
        mock_countries_response.status_code = 200
        mock_countries_response.json.return_value = {
            'results': [{'code': 'BR', 'id': 45}]
        }
        
        # Segundo: busca de locations
        mock_locations_response = Mock()
        mock_locations_response.status_code = 200
        mock_locations_response.json.return_value = {
            'results': [
                {
                    'id': 123,
                    'name': 'São Paulo',
                    'locality': 'São Paulo',
                    'sensors': [
                        {
                            'id': 1,
                            'parameter': {'name': 'pm25', 'units': 'μg/m³'}
                        }
                    ]
                }
            ],
            'meta': {'found': 1}
        }
        
        # Terceiro: busca de dados latest
        mock_latest_response = Mock()
        mock_latest_response.status_code = 200
        mock_latest_response.json.return_value = {
            'results': [
                {
                    'value': 15.5,
                    'datetime': {'utc': '2024-01-01T12:00:00Z'},
                    'sensorsId': 1
                }
            ]
        }
        
        # Configura os mocks para retornar em sequência
        mock_get.side_effect = [
            mock_countries_response,  # Busca países
            mock_locations_response,  # Busca locations
            mock_latest_response      # Busca latest
        ]
        
        # Executa a função
        result = fetch_air_quality_data('São Paulo', 'BR', 100, api_key='test_api_key')
        
        # Verifica os resultados
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
    
    @patch('modules.data_fetcher.get_api_key')
    @patch('modules.data_fetcher.requests.get')
    def test_fetch_air_quality_data_api_error(self, mock_get, mock_api_key):
        """Testa tratamento de erro da API."""
        # Mock da chave de API
        mock_api_key.return_value = 'test_api_key'
        
        # Mock de erro da API
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        # Executa a função
        result = fetch_air_quality_data('Cidade Inexistente', 'BR', api_key='test_api_key')
        
        # Verifica que retorna None
        self.assertIsNone(result)
    
    @patch('modules.data_fetcher.get_api_key')
    @patch('modules.data_fetcher.requests.get')
    def test_fetch_air_quality_data_timeout(self, mock_get, mock_api_key):
        """Testa tratamento de timeout."""
        # Mock da chave de API
        mock_api_key.return_value = 'test_api_key'
        
        import requests
        mock_get.side_effect = requests.exceptions.Timeout()
        
        # Executa a função
        result = fetch_air_quality_data('São Paulo', 'BR', api_key='test_api_key')
        
        # Verifica que retorna None
        self.assertIsNone(result)
    
    @patch('modules.data_fetcher.get_api_key')
    @patch('modules.data_fetcher.requests.get')
    def test_fetch_air_quality_data_connection_error(self, mock_get, mock_api_key):
        """Testa tratamento de erro de conexão."""
        # Mock da chave de API
        mock_api_key.return_value = 'test_api_key'
        
        import requests
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        # Executa a função
        result = fetch_air_quality_data('São Paulo', 'BR', api_key='test_api_key')
        
        # Verifica que retorna None
        self.assertIsNone(result)
    
    @patch('modules.data_fetcher.get_api_key')
    @patch('modules.data_fetcher.requests.get')
    def test_get_available_cities_success(self, mock_get, mock_api_key):
        """Testa busca bem-sucedida de cidades disponíveis."""
        # Mock da chave de API
        mock_api_key.return_value = 'test_api_key'
        
        # Mock das respostas da API v3
        # Primeiro: busca de países
        mock_countries_response = Mock()
        mock_countries_response.status_code = 200
        mock_countries_response.json.return_value = {
            'results': [{'code': 'BR', 'id': 45}]
        }
        
        # Segundo: busca de locations
        mock_locations_response = Mock()
        mock_locations_response.status_code = 200
        mock_locations_response.json.return_value = {
            'results': [
                {
                    'id': 123,
                    'name': 'São Paulo',
                    'locality': 'São Paulo'
                },
                {
                    'id': 124,
                    'name': 'Rio de Janeiro',
                    'locality': 'Rio de Janeiro'
                }
            ],
            'meta': {'found': 2}
        }
        
        # Terceiro: busca de dados latest (para verificar se tem dados)
        mock_latest_response = Mock()
        mock_latest_response.status_code = 200
        mock_latest_response.json.return_value = {
            'results': [{'value': 15.5}]
        }
        
        # Configura os mocks para retornar em sequência
        mock_get.side_effect = [
            mock_countries_response,  # Busca países
            mock_locations_response,  # Busca locations (página 1)
            mock_latest_response,     # Verifica dados para São Paulo
            mock_latest_response      # Verifica dados para Rio de Janeiro
        ]
        
        # Executa a função
        result = get_available_cities('BR', api_key='test_api_key')
        
        # Verifica os resultados
        self.assertIsNotNone(result)
        self.assertGreater(len(result), 0)
        # Verifica se retorna lista de dicionários
        if isinstance(result[0], dict):
            city_names = [city['name'] for city in result]
            self.assertIn('São Paulo', city_names)
    
    @patch('modules.data_fetcher.get_api_key')
    @patch('modules.data_fetcher.requests.get')
    def test_get_available_cities_error(self, mock_get, mock_api_key):
        """Testa tratamento de erro ao buscar cidades."""
        # Mock da chave de API
        mock_api_key.return_value = 'test_api_key'
        
        # Mock de erro da API
        mock_response = Mock()
        mock_response.status_code = 500
        mock_get.return_value = mock_response
        
        # Executa a função
        result = get_available_cities('BR', api_key='test_api_key')
        
        # Verifica que retorna None
        self.assertIsNone(result)


if __name__ == '__main__':
    unittest.main()

