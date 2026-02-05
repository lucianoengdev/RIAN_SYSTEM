import random
from difflib import SequenceMatcher

def similar(a, b):
    """Retorna uma taxa de similaridade entre 0 e 1 entre duas strings"""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def search_wine_api(query_name, query_vintage):
    """
    Simula a busca nas APIs do Wine.com/Robert Parker.
    Retorna uma LISTA de candidatos para o usuário escolher.
    """
    
    # Simulação de um banco de dados global (No futuro, isso vem da API Real)
    # Isso resolve o problema de 'múltiplos resultados'
    mock_database = [
        {"name": "Chateau Margaux", "country": "França", "region": "Bordeaux", "sub": "Margaux"},
        {"name": "Pavillon Rouge du Chateau Margaux", "country": "França", "region": "Bordeaux", "sub": "Margaux"},
        {"name": "Catena Zapata Malbec Argentino", "country": "Argentina", "region": "Mendoza", "sub": "Uco Valley"},
        {"name": "Solaia Antinori", "country": "Itália", "region": "Toscana", "sub": "Chianti"},
        {"name": "Pera Manca", "country": "Portugal", "region": "Alentejo", "sub": "Évora"},
    ]

    results = []
    
    # 1. Busca Exata ou Similaridade Alta (> 0.4)
    for wine in mock_database:
        similarity = similar(query_name, wine['name'])
        
        if query_name.lower() in wine['name'].lower() or similarity > 0.4:
            # Simula dados que viriam da API paga
            results.append({
                'name': wine['name'],
                'vintage': query_vintage,
                'country': wine['country'],
                'region': wine['region'],
                'sub_region': wine['sub'],
                'price': random.randint(200, 5000), # Mock de preço
                'score_rp': str(random.randint(90, 100)),
                'score_ws': str(random.randint(88, 98)),
                'drink_from': int(query_vintage) + 5 if query_vintage.isdigit() else 2026,
                'drink_to': int(query_vintage) + 25 if query_vintage.isdigit() else 2040,
                'confidence': similarity # Para ordenar o melhor resultado primeiro
            })
    
    # Ordena os resultados pelo mais parecido com o que o usuário digitou
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    return results