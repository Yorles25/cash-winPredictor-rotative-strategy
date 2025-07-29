# src/utils.py
import json

def cargar_json(ruta_archivo):
    """Carga un archivo JSON y devuelve su contenido."""
    try:
        with open(ruta_archivo, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta {ruta_archivo}")
        return None
    except json.JSONDecodeError:
        print(f"Error: El archivo en {ruta_archivo} no es un JSON válido.")
        return None