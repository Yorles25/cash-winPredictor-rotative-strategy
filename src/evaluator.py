# Contenido para src/evaluator.py

def evaluate_prediction(prediction: list, result: list) -> dict:
    """
    Compara una predicción con el resultado real de un sorteo.

    Args:
        prediction (list): La lista de números que se predijo.
        result (list): La lista de números que realmente salieron.

    Returns:
        dict: Un diccionario con el número de aciertos y la lista de números acertados.
    """
    if not isinstance(prediction, list) or not isinstance(result, list):
        return {"hits": 0, "matched_numbers": []}
        
    # Usamos la intersección de conjuntos para encontrar los aciertos de forma eficiente
    predicted_numbers = set(prediction)
    result_numbers = set(result)
    
    matched_numbers = list(predicted_numbers.intersection(result_numbers))
    hits = len(matched_numbers)
    
    return {
        "hits": hits,
        "matched_numbers": sorted(matched_numbers)
    }

# --- Bloque de Prueba ---
if __name__ == '__main__':
    print("⚙️  Ejecutando prueba del módulo evaluator...")
    
    # Caso de prueba 1: 2 aciertos
    test_prediction = [5, 9, 12, 18, 22]
    test_result = [3, 9, 15, 18, 25]
    evaluation = evaluate_prediction(test_prediction, test_result)
    print(f"\nCaso 1: Predicción {test_prediction}, Resultado {test_result}")
    print(f"   -> Resultado Evaluación: {evaluation}")
    assert evaluation['hits'] == 2
    assert evaluation['matched_numbers'] == [9, 18]
    print("✅ Prueba 1 superada.")

    # Caso de prueba 2: 0 aciertos
    test_prediction_2 = [1, 2, 3, 4, 5]
    test_result_2 = [10, 11, 12, 13, 14]
    evaluation_2 = evaluate_prediction(test_prediction_2, test_result_2)
    print(f"\nCaso 2: Predicción {test_prediction_2}, Resultado {test_result_2}")
    print(f"   -> Resultado Evaluación: {evaluation_2}")
    assert evaluation_2['hits'] == 0
    print("✅ Prueba 2 superada.")
    
    print("\nTodas las pruebas del evaluador superadas.")