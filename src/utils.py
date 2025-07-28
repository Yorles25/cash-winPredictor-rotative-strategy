# Contenido para src/utils.py

import json

# --- Constantes del Proyecto ---
# Definimos la ruta al archivo de datos para no tener que escribirla en todos lados.
HISTORICAL_DATA_PATH = "data/historical_draws.json"

def load_historical_data():
    """
    Carga los datos históricos desde el archivo JSON.

    Returns:
        dict: Un diccionario con los sorteos históricos.
              Las llaves son las fechas y los valores son las listas de números.
        None: Si el archivo no se encuentra o está vacío.
    """
    try:
        with open(HISTORICAL_DATA_PATH, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if not data:
                print("⚠️ Advertencia: El archivo historical_draws.json está vacío.")
                return None
            return data
    except FileNotFoundError:
        print(f"❌ Error: No se encontró el archivo en la ruta: {HISTORICAL_DATA_PATH}")
        return None
    except json.JSONDecodeError:
        print("❌ Error: El archivo JSON tiene un formato inválido.")
        return None

# --- Bloque de Prueba ---
# Este código solo se ejecuta cuando corres 'python src/utils.py' directamente.
# Es perfecto para probar que nuestra función 'load_historical_data' funciona correctamente.
if __name__ == "__main__":
    print("⚙️  Ejecutando prueba del módulo utils...")
    
    historical_data = load_historical_data()
    
    if historical_data:
        print("✅ ¡Éxito! Datos históricos cargados correctamente.")
        
        # Mostramos la cantidad de sorteos cargados
        print(f"   Total de sorteos en el historial: {len(historical_data)}")
        
        # Mostramos los primeros 3 para verificar
        first_three_items = list(historical_data.items())[:3]
        print("   Mostrando los primeros 3 registros:")
        for date, draw in first_three_items:
            print(f"     - Fecha: {date}, Sorteo: {draw}")
    else:
        print(" Detección de problema al cargar datos. Revisa los mensajes de error de arriba.")