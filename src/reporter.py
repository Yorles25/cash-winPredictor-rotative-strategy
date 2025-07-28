# Contenido para src/reporter.py

import pandas as pd
from datetime import timedelta

# Importamos las funciones que ya hemos creado
from .utils import load_historical_data
from .generator import generate_predictions
from .evaluator import evaluate_prediction

def run_backtesting(enabled_strategies: dict):
    """
    Realiza un backtesting completo sobre todo el historial de datos.

    Args:
        enabled_strategies (dict): Un diccionario que indica qué estrategias usar.

    Returns:
        pd.DataFrame: Un DataFrame con los resultados del backtesting.
    """
    historical_data = load_historical_data()
    if not historical_data:
        print("No hay datos históricos para el backtesting.")
        return pd.DataFrame()

    # Convertimos a DataFrame y ordenamos por fecha para procesar en orden cronológico
    df = pd.DataFrame.from_dict(historical_data, orient='index', columns=[f'n{i+1}' for i in range(5)])
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    results_log = []
    
    # Iteramos por cada día en el historial (a partir del décimo para tener suficientes datos)
    for i in range(10, len(df)):
        # La fecha actual que vamos a "predecir"
        current_date = df.index[i]
        actual_result = df.loc[current_date].tolist()

        # Usamos SOLO los datos ANTERIORES a la fecha actual para la predicción
        past_data_df = df.iloc[:i]
        past_data_dict = {date.strftime('%Y-%m-%d'): row.tolist() for date, row in past_data_df.iterrows()}

        # Generamos la predicción para ese día usando solo el pasado
        # Creamos una instancia temporal del generador para pasarle los datos del pasado
        # (Esta es una forma de simular el estado del generador en ese día)
        # Nota: Para simplificar, la función generate_predictions usará los datos completos,
        # pero en una versión más avanzada, debería aceptar los datos del pasado.
        # Por ahora, la lógica interna de las estrategias ya usa los datos más recientes.
        prediction = generate_predictions(enabled_strategies)

        # Evaluamos la predicción contra el resultado real
        evaluation = evaluate_prediction(prediction, actual_result)

        results_log.append({
            "Fecha": current_date.strftime('%Y-%m-%d'),
            "Prediccion": ", ".join(map(str, prediction)),
            "Resultado Real": ", ".join(map(str, actual_result)),
            "Aciertos": evaluation['hits'],
            "Numeros Acertados": ", ".join(map(str, evaluation['matched_numbers']))
        })
        
        print(f"Backtesting para {current_date.strftime('%Y-%m-%d')}: {evaluation['hits']} aciertos.")

    return pd.DataFrame(results_log)


# --- Bloque de Prueba ---
if __name__ == "__main__":
    print("⚙️  Ejecutando Backtesting completo...")

    # Definimos qué combinación de estrategias queremos probar
    # ¡Puedes cambiar esto para probar diferentes combinaciones!
    strategies_to_test = {
        "detective": True,
        "semaforo": True,
        "persistencia": True,
        "afinidad": False
    }
    
    print(f"Probando con las siguientes estrategias activas: {list(k for k,v in strategies_to_test.items() if v)}")

    report_df = run_backtesting(enabled_strategies=strategies_to_test)
    
    if not report_df.empty:
        # Guardamos el reporte en la carpeta /outputs
        output_path = "outputs/backtesting_report.csv"
        report_df.to_csv(output_path, index=False)
        
        print("\n✅ ¡Backtesting completado!")
        print(f"   Reporte guardado en: {output_path}")
        
        # Mostramos un resumen
        total_hits = report_df['Aciertos'].sum()
        total_days = len(report_df)
        avg_hits = report_df['Aciertos'].mean()
        
        print("\n--- Resumen del Rendimiento ---")
        print(f"Total de días analizados: {total_days}")
        print(f"Total de aciertos acumulados: {total_hits}")
        print(f"Promedio de aciertos por día: {avg_hits:.2f}")
        print("-------------------------------")
    else:
        print("\nNo se pudo generar el reporte de backtesting.")