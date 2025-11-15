"""
Módulo responsável por buscar dados da API OpenAQ v3.

Este módulo contém funções para fazer requisições à API OpenAQ v3
e obter dados de qualidade do ar para cidades brasileiras.
A API v3 requer autenticação com chave de API.
"""

import requests
from typing import Optional, Dict, List
import logging
from datetime import datetime, timedelta
import os

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# URLs da API OpenAQ v3
BASE_URL_MEASUREMENTS = "https://api.openaq.org/v3/measurements"
BASE_URL_LOCATIONS = "https://api.openaq.org/v3/locations"


def get_api_key() -> Optional[str]:
    """
    Obtém a chave de API das variáveis de ambiente.
    
    Returns:
        Chave de API ou None se não estiver configurada.
    """
    return os.getenv('OPENAQ_API_KEY')


def fetch_air_quality_data(city: str, country: str = "BR", limit: int = 100, api_key: Optional[str] = None) -> Optional[List[Dict]]:
    """
    Busca dados de qualidade do ar para uma cidade específica usando a API OpenAQ v3.
    
    Args:
        city: Nome da cidade (ex: "São Paulo", "Rio de Janeiro")
        country: Código do país (padrão: "BR" para Brasil)
        limit: Número máximo de resultados a retornar (padrão: 100)
        api_key: Chave de API da OpenAQ (opcional, tenta obter de variável de ambiente se não fornecida)
    
    Returns:
        Lista de dicionários com os dados de qualidade do ar, ou None em caso de erro.
    """
    # Obtém a chave de API
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        logger.error("Chave de API não fornecida. Configure a variável de ambiente OPENAQ_API_KEY.")
        return None
    
    try:
        headers = {
            'X-API-Key': api_key
        }
        
        # Primeiro, busca o ID do país pelo código ISO
        logger.info(f"Buscando ID do país {country}")
        countries_url = "https://api.openaq.org/v3/countries"
        countries_params = {'limit': 200}
        
        countries_response = requests.get(
            countries_url,
            headers=headers,
            params=countries_params,
            timeout=15
        )
        
        if countries_response.status_code != 200:
            logger.error(f"Erro ao buscar países: Status {countries_response.status_code}")
            if countries_response.status_code == 401:
                logger.error("Chave de API inválida ou não autorizada")
            return None
        
        countries_data = countries_response.json()
        countries = countries_data.get('results', [])
        
        # Encontra o país pelo código ISO
        country_id = None
        for c in countries:
            if c.get('code', '').upper() == country.upper():
                country_id = c.get('id')
                break
        
        if not country_id:
            logger.error(f"País {country} não encontrado")
            return None
        
        logger.info(f"ID do país {country}: {country_id}")
        
        # Agora busca locations para o país usando o ID
        logger.info(f"Buscando locations para {country} (ID: {country_id})")
        
        # Normaliza o nome da cidade para busca (remove acentos e converte para minúsculas)
        city_normalized = city.lower()
        # Remove acentos comuns
        city_normalized = city_normalized.replace('ã', 'a').replace('á', 'a').replace('â', 'a')
        city_normalized = city_normalized.replace('é', 'e').replace('ê', 'e')
        city_normalized = city_normalized.replace('í', 'i')
        city_normalized = city_normalized.replace('ó', 'o').replace('ô', 'o')
        city_normalized = city_normalized.replace('ú', 'u')
        city_normalized = city_normalized.replace('ç', 'c')
        
        # Função auxiliar para normalizar texto (remove acentos)
        def normalize_text(text):
            """Remove acentos e converte para minúsculas."""
            if not text:
                return ''
            text = text.lower()
            # Remove acentos
            replacements = {
                'ã': 'a', 'á': 'a', 'â': 'a', 'à': 'a',
                'é': 'e', 'ê': 'e', 'è': 'e',
                'í': 'i', 'î': 'i', 'ì': 'i',
                'ó': 'o', 'ô': 'o', 'ò': 'o',
                'ú': 'u', 'û': 'u', 'ù': 'u',
                'ç': 'c', 'ñ': 'n'
            }
            for old, new in replacements.items():
                text = text.replace(old, new)
            return text
        
        # Busca locations em lotes (a API pode ter muitas locations)
        city_locations = []
        page = 1
        limit_per_page = 100
        max_pages = 30  # Aumenta para 30 páginas (3000 locations) para garantir que encontra todas as cidades
        total_searched = 0
        
        # Variantes comuns de nomes de cidades brasileiras
        city_variants = [city_normalized]
        city_variants_map = {
            'belo horizonte': ['belo horizonte', 'bh', 'belo-horizonte'],
            'brasilia': ['brasilia', 'brasília', 'brasil', 'df'],
            'curitiba': ['curitiba', 'curitiba-pr'],
            'porto alegre': ['porto alegre', 'porto-alegre', 'poa'],
            'fortaleza': ['fortaleza', 'fortaleza-ce'],
            'salvador': ['salvador', 'salvador-ba'],
            'recife': ['recife', 'recife-pe'],
            'manaus': ['manaus', 'manaus-am'],
            'sao paulo': ['sao paulo', 'são paulo', 'sp', 'sao-paulo'],
            'rio de janeiro': ['rio de janeiro', 'rio', 'rj', 'rio-de-janeiro']
        }
        
        # Adiciona variantes se existirem
        for key, variants in city_variants_map.items():
            if city_normalized in variants or any(v in city_normalized for v in variants):
                city_variants.extend(variants)
        
        city_variants = list(set(city_variants))  # Remove duplicatas
        
        logger.info(f"Buscando locations com variantes: {city_variants[:3]}...")
        
        while page <= max_pages:
            locations_params = {
                'countries_id': country_id,
                'limit': limit_per_page,
                'page': page
            }
            
            locations_response = requests.get(
                BASE_URL_LOCATIONS, 
                headers=headers, 
                params=locations_params, 
                timeout=15
            )
            
            if locations_response.status_code != 200:
                logger.error(f"Erro ao buscar locations: Status {locations_response.status_code}")
                if locations_response.status_code == 401:
                    logger.error("Chave de API inválida ou não autorizada")
                break
            
            locations_data = locations_response.json()
            locations = locations_data.get('results', [])
            meta = locations_data.get('meta', {})
            total_found = meta.get('found', 0)
            
            if not locations:
                break
            
            total_searched += len(locations)
            
            # Log de progresso a cada 5 páginas
            if page % 5 == 0:
                logger.info(f"Buscando página {page}... ({total_searched}/{total_found} locations verificadas)")
            
            # Filtra locations pela cidade (busca no name, locality, e provider)
            for loc in locations:
                loc_name = normalize_text(loc.get('name') or '')
                loc_locality = normalize_text(loc.get('locality') or '')
                provider = loc.get('provider', {})
                provider_name = normalize_text(provider.get('name', '') if provider else '')
                
                # Verifica se alguma variante da cidade está no nome, locality ou provider
                found = False
                for variant in city_variants:
                    if (variant in loc_name or 
                        variant in loc_locality or
                        variant in provider_name):
                        found = True
                        break
                
                if found:
                    city_locations.append(loc)
            
            # Calcula quantas páginas existem baseado no total encontrado
            total_pages = (total_found + limit_per_page - 1) // limit_per_page if total_found > 0 else 1
            
            # Se encontrou locations suficientes, continua buscando mais algumas páginas
            # para garantir que pegou todas, mas limita a busca
            if len(city_locations) >= 5:
                # Se já encontrou algumas, busca mais 2 páginas para garantir
                if page >= min(3, total_pages):
                    break
            elif len(locations) < limit_per_page or page >= total_pages:
                # Não há mais páginas disponíveis
                break
            
            # Se não encontrou nada ainda, continua buscando até encontrar ou esgotar as páginas
            # Não para na primeira página se não encontrou nada - busca pelo menos 5 páginas
            if len(city_locations) == 0 and page < min(5, total_pages):
                # Continua buscando se ainda não encontrou nada
                page += 1
            elif len(city_locations) == 0:
                # Se já buscou 5 páginas e não encontrou nada, pode ser que não exista
                # Mas continua até o máximo de páginas configurado
                page += 1
            else:
                page += 1
        
        logger.info(f"Buscou {total_searched} locations em {page} páginas")
        
        if not city_locations:
            logger.warning(f"Nenhuma location encontrada para {city}, {country}")
            logger.info(f"Buscou {total_searched} locations em {page} páginas")
            # Tenta obter lista de cidades disponíveis para informar ao usuário
            try:
                available_cities = get_available_cities(country, api_key)
                if available_cities and len(available_cities) > 0:
                    logger.info(f"Cidades disponíveis na API: {', '.join(available_cities[:10])}{'...' if len(available_cities) > 10 else ''}")
            except:
                pass
            return None
        
        logger.info(f"Encontradas {len(city_locations)} locations para {city}")
        
        # Busca dados mais recentes (latest) para cada location encontrada
        # A API v3 usa /v3/locations/{location_id}/latest para obter os dados mais recentes
        all_results = []
        location_ids = [loc['id'] for loc in city_locations[:5]]  # Limita a 5 locations
        
        logger.info(f"Buscando dados mais recentes para {len(location_ids)} locations em {city}, {country}")
        
        for location_id in location_ids:
            try:
                # Busca dados mais recentes para esta location
                latest_url = f"{BASE_URL_LOCATIONS}/{location_id}/latest"
                
                response = requests.get(
                    latest_url,
                    headers=headers,
                    timeout=15
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    
                    # Encontra a location correspondente para obter informações adicionais
                    location_info = next((loc for loc in city_locations if loc['id'] == location_id), None)
                    
                    # Converte o formato da API v3 para o formato esperado pelo processador
                    for result in results:
                        date_obj = result.get('datetime', {})
                        
                        # A API v3 latest retorna: datetime, value, coordinates, sensorsId, locationsId
                        # Precisamos buscar informações do sensor para obter o parâmetro
                        sensor_id = result.get('sensorsId')
                        
                        # Tenta obter informações do parâmetro da location_info
                        parameter_name = None
                        parameter_unit = 'μg/m³'
                        
                        if location_info and 'sensors' in location_info:
                            for sensor in location_info.get('sensors', []):
                                if sensor.get('id') == sensor_id:
                                    param = sensor.get('parameter', {})
                                    parameter_name = param.get('name', '')
                                    parameter_unit = param.get('units', 'μg/m³')
                                    break
                        
                        # Se não encontrou o parâmetro, tenta buscar do sensor
                        if not parameter_name:
                            # Usa um valor padrão ou tenta buscar do sensor
                            parameter_name = 'unknown'
                        
                        # Extrai o nome da cidade da location
                        location_city = location_info.get('locality') or location_info.get('name') or city if location_info else city
                        
                        formatted_result = {
                            'parameter': parameter_name,
                            'value': result.get('value', 0),
                            'unit': parameter_unit,
                            'date': {
                                'utc': date_obj.get('utc', '') if date_obj else ''
                            },
                            'location': location_info.get('name', '') if location_info else '',
                            'locationId': location_id,
                            'city': location_city,
                            'country': location_info.get('country', {}).get('code', country) if location_info and isinstance(location_info.get('country'), dict) else country
                        }
                        all_results.append(formatted_result)
                
                elif response.status_code == 404:
                    logger.warning(f"Location {location_id} não encontrada ou sem dados")
                elif response.status_code == 401:
                    logger.error("Chave de API inválida ou não autorizada")
                    return None
                elif response.status_code == 429:
                    logger.error("Limite de requisições excedido. Tente novamente mais tarde.")
                    return None
                else:
                    logger.warning(f"Erro ao buscar dados para location {location_id}: Status {response.status_code}")
            
            except Exception as e:
                logger.warning(f"Erro ao processar location {location_id}: {str(e)}")
                continue
        
        if not all_results:
            logger.warning(f"Nenhum dado encontrado para {city}, {country}")
            return None
        
        logger.info(f"Dados obtidos com sucesso: {len(all_results)} registros de {len(location_ids)} locations")
        return all_results
            
    except requests.exceptions.Timeout:
        logger.error("Timeout ao conectar com a API OpenAQ")
        return None
    except requests.exceptions.ConnectionError:
        logger.error("Erro de conexão com a API OpenAQ")
        return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Erro inesperado: {str(e)}")
        return None


def get_available_cities(country: str = "BR", api_key: Optional[str] = None) -> Optional[List[str]]:
    """
    Busca lista de cidades disponíveis na API OpenAQ v3 para um país.
    Retorna apenas cidades que realmente têm dados disponíveis.
    
    Args:
        country: Código do país (padrão: "BR" para Brasil)
        api_key: Chave de API da OpenAQ (opcional, tenta obter de variável de ambiente se não fornecida)
    
    Returns:
        Lista de nomes de cidades com dados disponíveis, ou None em caso de erro.
    """
    # Obtém a chave de API
    if not api_key:
        api_key = get_api_key()
    
    if not api_key:
        logger.error("Chave de API não fornecida. Configure a variável de ambiente OPENAQ_API_KEY.")
        return None
    
    try:
        headers = {
            'X-API-Key': api_key
        }
        
        # Primeiro, busca o ID do país pelo código ISO
        countries_url = "https://api.openaq.org/v3/countries"
        countries_params = {'limit': 200}
        
        countries_response = requests.get(
            countries_url,
            headers=headers,
            params=countries_params,
            timeout=15
        )
        
        if countries_response.status_code != 200:
            logger.error(f"Erro ao buscar países: Status {countries_response.status_code}")
            return None
        
        countries_data = countries_response.json()
        countries = countries_data.get('results', [])
        
        # Encontra o país pelo código ISO
        country_id = None
        for c in countries:
            if c.get('code', '').upper() == country.upper():
                country_id = c.get('id')
                break
        
        if not country_id:
            logger.error(f"País {country} não encontrado")
            return None
        
        # Busca todas as locations do país
        all_locations = []
        page = 1
        limit_per_page = 100
        
        while True:
            params = {
                'countries_id': country_id,
                'limit': limit_per_page,
                'page': page
            }
            
            response = requests.get(
                BASE_URL_LOCATIONS, 
                headers=headers, 
                params=params, 
                timeout=15
            )
            
            if response.status_code != 200:
                logger.error(f"Erro ao buscar locations: Status {response.status_code}")
                break
            
            data = response.json()
            locations = data.get('results', [])
            meta = data.get('meta', {})
            
            if not locations:
                break
            
            all_locations.extend(locations)
            
            # Verifica se há mais páginas
            total_found = meta.get('found', 0)
            if len(all_locations) >= total_found or len(locations) < limit_per_page:
                break
            
            page += 1
        
        # Função para verificar se um nome de cidade é válido
        def is_valid_city_name(city_name):
            """Verifica se o nome da cidade é válido (não é teste, N/A, etc.)"""
            if not city_name or not city_name.strip():
                return False
            
            city_lower = city_name.lower().strip()
            
            # Filtra nomes inválidos
            invalid_patterns = [
                'teste', 'test', 'n/a', 'na', 'none', 'null', 'unknown',
                '211004', 'modo_fixo', 'modo fixo', 'tiradentes 2.0',
                'sem nome', 'indefinido', 'undefined', 'cidade tiradentes',
                'grajaú-parelheiros', 'quality01', 'quality', 'quality0',
                'cid.', 'cid ', 'usp', 'ipen'  # Nomes de estações, não cidades
            ]
            
            # Filtra nomes que parecem ser códigos ou estações
            if any(char.isdigit() for char in city_lower[:3]) and len(city_lower) < 10:
                return False
            
            # Verifica se contém padrões inválidos
            for pattern in invalid_patterns:
                if pattern in city_lower:
                    return False
            
            # Verifica se é muito curto (menos de 3 caracteres)
            if len(city_lower) < 3:
                return False
            
            # Verifica se contém apenas números ou caracteres especiais
            if city_lower.replace(' ', '').replace('-', '').replace('_', '').isdigit():
                return False
            
            # Verifica se começa com número seguido de underscore (padrão de teste)
            if city_lower[0].isdigit() and '_' in city_lower:
                return False
            
            # Verifica se tem muitos underscores (provavelmente código de teste)
            if city_lower.count('_') > 1:
                return False
            
            return True
        
        # Lista de cidades principais brasileiras que queremos mostrar (prioridade)
        # Apenas as 10 maiores cidades com dados disponíveis
        priority_cities = [
            'são paulo', 'sao paulo',
            'rio de janeiro',
            'campinas',
            'guarulhos',
            'santos',
            'osasco',
            'santo andré', 'santo andre',
            'são bernardo do campo', 'sao bernardo do campo',
            'ribeirão preto', 'ribeirao preto'
        ]
        
        # Mapeamento de cidades brasileiras conhecidas para seus estados
        city_to_state = {
            'são paulo': 'SP', 'sao paulo': 'SP',
            'rio de janeiro': 'RJ',
            'campinas': 'SP',
            'guarulhos': 'SP',
            'santos': 'SP',
            'osasco': 'SP',
            'santo andré': 'SP', 'santo andre': 'SP',
            'são bernardo do campo': 'SP', 'sao bernardo do campo': 'SP',
            'ribeirão preto': 'SP', 'ribeirao preto': 'SP',
            'diadema': 'SP',
            'jacareí': 'SP', 'jacarei': 'SP',
            'santa gertrudes': 'SP',
            'taubaté': 'SP', 'taubate': 'SP',
            'tatuí': 'SP', 'tatui': 'SP',
            'piracicaba': 'SP',
            'araraquara': 'SP',
            'catanduva': 'SP',
            'americana': 'SP',
            'araçatuba': 'SP', 'aracatuba': 'SP',
            'bauru': 'SP',
            'carapicuíba': 'SP', 'carapicuiba': 'SP',
            'mogi das cruzes': 'SP', 'mogi-das-cruzes': 'SP',
            'imperatriz': 'MA'
        }
        
        # Extrai cidades únicas que realmente têm dados e são válidas
        cities_dict = {}  # {nome_cidade: {'state': estado, 'location_ids': [ids]}}
        
        for loc in all_locations:
            # Prioriza locality, mas usa name se locality não estiver disponível
            city = loc.get('locality') or loc.get('name')
            
            if city and city.strip() and is_valid_city_name(city):
                city_clean = city.strip()
                city_key = city_clean.lower()
                
                # Tenta obter informação do estado
                state = city_to_state.get(city_key)
                
                # Verifica se já temos essa cidade
                if city_clean not in cities_dict:
                    cities_dict[city_clean] = {
                        'state': state,
                        'location_ids': []
                    }
                
                # Adiciona o location_id
                cities_dict[city_clean]['location_ids'].append(loc.get('id'))
        
        # Verifica quais cidades realmente têm dados disponíveis
        # Prioriza cidades da lista priority_cities para verificar primeiro
        cities_to_check = []
        priority_cities_found = []
        other_cities = []
        
        for city_name, city_info in cities_dict.items():
            city_lower = city_name.lower()
            is_priority = any(priority in city_lower or city_lower in priority for priority in priority_cities)
            
            if is_priority:
                priority_cities_found.append((city_name, city_info))
            else:
                other_cities.append((city_name, city_info))
        
        # Verifica primeiro as cidades prioritárias
        cities_to_check = priority_cities_found + other_cities
        
        cities_with_data = []
        checked_count = 0
        max_to_check = 15  # Verifica até 15 cidades para garantir que temos 10 boas
        
        for city_name, city_info in cities_to_check:
            if len(cities_with_data) >= 10:
                break  # Já temos 10 cidades
            
            if checked_count >= max_to_check:
                break  # Limita verificações para não demorar muito
            
            location_ids = city_info['location_ids']
            has_data = False
            
            # Verifica apenas a primeira location (mais rápido)
            try:
                location_id = location_ids[0]
                latest_url = f"{BASE_URL_LOCATIONS}/{location_id}/latest"
                response = requests.get(
                    latest_url,
                    headers=headers,
                    timeout=3  # Timeout menor para ser mais rápido
                )
                
                if response.status_code == 200:
                    data = response.json()
                    results = data.get('results', [])
                    if results and len(results) > 0:
                        has_data = True
            except:
                pass
            
            checked_count += 1
            
            if has_data:
                # Formata o nome da cidade com estado se disponível
                if city_info['state']:
                    display_name = f"{city_name} - {city_info['state']}"
                else:
                    display_name = city_name
                
                cities_with_data.append({
                    'name': city_name,
                    'display': display_name,
                    'state': city_info['state']
                })
        
        # Ordena as cidades: primeiro as prioritárias, depois as outras
        def sort_key(city_info):
            city_lower = city_info['name'].lower()
            # Prioriza cidades da lista priority_cities
            for i, priority in enumerate(priority_cities):
                if priority in city_lower or city_lower in priority:
                    return (0, i)  # Prioridade alta, ordenada por índice
            return (1, city_info['name'])  # Outras cidades, ordenadas por nome
        
        cities_with_data.sort(key=sort_key)
        
        # Limita a 10 cidades principais
        cities_with_data = cities_with_data[:10]
        
        # Retorna lista de dicionários com nome e display
        logger.info(f"Cidades válidas com dados disponíveis: {len(cities_with_data)} (limitado a 10 principais)")
        return cities_with_data
            
    except Exception as e:
        logger.error(f"Erro ao buscar cidades: {str(e)}")
        return None
