import random

def fetch_wine_data(name, vintage):
    """
    Simula a busca em uma API externa (Wine.com).
    No futuro, você colocará aqui sua API KEY real.
    """
    print(f"Buscando dados para: {name} safra {vintage}...")
    
    # Lógica Simulada (MOCK) para o sistema funcionar hoje
    # Tenta "adivinhar" o país pelo nome para popular as abas corretamente
    name_lower = name.lower()
    country = "Outros"
    wine_type = "Tinto"
    
    if any(x in name_lower for x in ['chablis', 'bordeaux', 'latour', 'margaux', 'champagne', 'rhône']):
        country = "França"
    elif any(x in name_lower for x in ['barolo', 'toscana', 'brunello', 'chianti']):
        country = "Itália"
    elif any(x in name_lower for x in ['rioja', 'priorat', 'vega sicilia']):
        country = "Espanha"
    elif any(x in name_lower for x in ['douro', 'porto', 'alentejo']):
        country = "Portugal"
        
    if 'blanc' in name_lower or 'chardonnay' in name_lower or 'riesling' in name_lower:
        wine_type = "Branco"

    # Retorna dados estruturados
    return {
        'country': country,
        'region': 'Região Desconhecida', # A API real preencheria isso
        'type': wine_type,
        'price': random.randint(200, 5000), # Preço simulado para fluxo de caixa
        'score_rp': str(random.randint(88, 100)),
        'score_ws': str(random.randint(85, 99)),
        'drink_window_start': int(vintage) + 5 if vintage.isdigit() else 2025,
        'drink_window_end': int(vintage) + 20 if vintage.isdigit() else 2035,
    }