# Contenido para src/generator.py (VERSIÓN ADAPTATIVA)

import json
from collections import Counter
import pandas as pd

from .utils import load_historical_data

STRATEGY_CONFIG_PATH = "strategy_config.json"

def load_strategy_config():
    """Carga la configuración de las estrategias."""
    try:
        with open(STRATEGY_CONFIG_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return None

# MODIFICACIÓN CLAVE: La función ahora acepta un argumento opcional
def generate_predictions(enabled_strategies=None):
    """
    Motor principal que genera predicciones.
    Si 'enabled_strategies' se proporciona, usa esa selección.
    Si no, usa la configuración del archivo JSON.
    """
    config = load_strategy_config()
    historical_data = load_historical_data()

    if not config or not historical_data:
        return []

    project_settings = config['project_settings']
    strategies_config = config['strategies']
    
    # Si no se pasa una selección desde la UI, usamos la del archivo
    if enabled_strategies is None:
        enabled_strategies = {name: params.get('enabled', False) for name, params in strategies_config.items()}

    df = pd.DataFrame.from_dict(historical_data, orient='index', columns=[f'n{i+1}' for i in range(5)])
    df.index = pd.to_datetime(df.index)
    
    all_numbers_drawn = df.values.flatten().tolist()
    
    number_scores = {i: 0.0 for i in range(project_settings['number_range']['min'], project_settings['number_range']['max'] + 1)}

    # AHORA EL IF COMPRUEBA LA SELECCIÓN DEL USUARIO
    if enabled_strategies.get('detective', False):
        params = strategies_config['detective']['params']
        weight = strategies_config['detective']['weight']
        recent_draws_df = df.sort_index(ascending=False).head(params['lookback_days'])
        numbers_in_recent_draws = set(recent_draws_df.values.flatten())
        for num in number_scores:
            if num not in numbers_in_recent_draws:
                number_scores[num] += 1.0 * weight

    if enabled_strategies.get('semaforo', False):
        weight = strategies_config['semaforo']['weight']
        frequency = Counter(all_numbers_drawn)
        if frequency:
            max_freq = max(frequency.values())
            for num in number_scores:
                score = frequency.get(num, 0) / max_freq
                number_scores[num] += score * weight

    if enabled_strategies.get('persistencia', False):
        params = strategies_config['persistencia']['params']
        weight = strategies_config['persistencia']['weight']
        last_draws_df = df.sort_index(ascending=False).head(params['repeat_lookback'])
        numbers_in_last_draws = set(last_draws_df.values.flatten())
        for num in numbers_in_last_draws:
            if num in number_scores:
                number_scores[num] += 1.0 * weight
    
    # ... Aquí irían futuras estrategias ...
    if enabled_strategies.get('afinidad', False):
        # La lógica de afinidad iría aquí
        pass

    sorted_candidates = sorted(number_scores.items(), key=lambda item: item[1], reverse=True)
    top_predictions = [num for num, score in sorted_candidates]
    
    return top_predictions[:project_settings['numbers_to_predict']]