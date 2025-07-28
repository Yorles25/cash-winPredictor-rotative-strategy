# Contenido para src/generator.py (VERSIÓN CON ESTRATEGIA ROTATIVA)
import json
from datetime import datetime
from .utils import load_historical_data

STRATEGY_CONFIG_PATH = "strategy_config.json"

def load_strategy_config():
    with open(STRATEGY_CONFIG_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)

def generate_predictions_rotativa(fecha_a_predecir: datetime, config: dict) -> list:
    """
    Genera una predicción basada en la estrategia rotativa de grupos.
    """
    # El ciclo de rotación tiene 5 pasos. Calculamos en qué paso estamos.
    # Usamos el día del año para determinar la posición en el ciclo.
    dia_del_año = fecha_a_predecir.timetuple().tm_yday
    paso_del_ciclo = (dia_del_año - 1) % len(config['rotacion']) # -1 porque los días empiezan en 1
    
    # Obtenemos los grupos a jugar para ese paso del ciclo
    grupos_a_jugar = config['rotacion'][paso_del_ciclo]
    
    # Recopilamos todos los números de los grupos seleccionados
    numeros_predichos = []
    for grupo_id in grupos_a_jugar:
        numeros_predichos.extend(config['grupos'][grupo_id])
        
    return sorted(list(set(numeros_predichos))) # Devuelve lista ordenada y sin duplicados


# Esta función principal ahora decide qué estrategia usar
def generate_predictions(enabled_strategies=None, fecha_str=None):
    config = load_strategy_config()
    
    # Si no se especifica fecha, se usa la de hoy
    fecha_a_predecir = datetime.strptime(fecha_str, '%Y-%m-%d') if fecha_str else datetime.now()

    # LA LÓGICA PRINCIPAL AHORA ES LA ROTATIVA
    # Las otras estrategias se pueden añadir en el futuro para "refinar" la selección
    return generate_predictions_rotativa(fecha_a_predecir, config)