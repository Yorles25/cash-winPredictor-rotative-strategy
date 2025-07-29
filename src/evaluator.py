# src/evaluator.py

def evaluar_jugada(jugada_realizada, numeros_sorteados_reales, config):
    """
    Evalúa una jugada contra los números de un sorteo real.

    Args:
        jugada_realizada (dict): El diccionario de la jugada generada.
            Ej: {"fecha": "2025-07-28", "grupos_jugados": [...], "numeros_jugados": [...]}
        numeros_sorteados_reales (list): La lista de números que salieron en el sorteo.
            Ej: [3, 8, 11, 14, 15]
        config (dict): El diccionario de configuración con costos y premios.

    Returns:
        dict: Un diccionario con el resultado completo de la evaluación.
    """
    numeros_jugados = jugada_realizada["numeros_jugados"]
    
    # --- CORRECCIÓN CLAVE ---
    # Ya no se asume que el segundo argumento es un diccionario.
    # Se usa directamente como la lista de números sorteados.
    
    # Usamos la intersección de conjuntos para encontrar los aciertos de forma eficiente
    aciertos = list(set(numeros_jugados) & set(numeros_sorteados_reales))
    cantidad_aciertos = len(aciertos)
    
    costo_por_numero = config["costo_por_numero"]
    premio_por_acierto = config["premio_por_acierto"]
    
    costo_total = len(numeros_jugados) * costo_por_numero
    premio_total = cantidad_aciertos * premio_por_acierto
    ganancia = premio_total - costo_total
    
    # Devolvemos un diccionario completo con todos los datos relevantes
    return {
        "fecha": jugada_realizada["fecha"],
        "grupos_jugados": jugada_realizada["grupos_jugados"],
        "numeros_jugados": numeros_jugados,
        "numeros_sorteados": numeros_sorteados_reales,
        "cantidad_aciertos": cantidad_aciertos,
        "aciertos": sorted(aciertos),
        "costo": costo_total,
        "premio": premio_total,
        "ganancia": ganancia
    }