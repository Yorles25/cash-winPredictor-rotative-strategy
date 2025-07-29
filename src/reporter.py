# src/reporter.py
import pandas as pd
import os

def guardar_reporte_csv(resultados, ruta_salida):
    """
    Convierte una lista de diccionarios de resultados a un DataFrame de Pandas
    y lo guarda como un archivo CSV.
    """
    if not resultados:
        print("No hay resultados para guardar.")
        return

    # Asegurarse de que el directorio de salida exista
    directorio_salida = os.path.dirname(ruta_salida)
    if not os.path.exists(directorio_salida):
        os.makedirs(directorio_salida)
        
    df = pd.DataFrame(resultados)
    
    # Organizar las columnas en un orden lógico
    columnas_ordenadas = [
        "fecha", "grupos_jugados", "cantidad_aciertos", "ganancia",
        "premio", "costo", "numeros_jugados", "numeros_sorteados", "aciertos"
    ]
    df = df[columnas_ordenadas]
    
    df.to_csv(ruta_salida, index=False, encoding='utf-8')
    print(f"Reporte de backtesting guardado exitosamente en: {ruta_salida}")