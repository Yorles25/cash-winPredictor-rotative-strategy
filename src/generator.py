# src/generator.py

from datetime import datetime

def generar_jugada_por_fecha(fecha, config):
    """
    Genera la combinación de grupos y números a jugar para una fecha específica.
    Ahora acepta tanto un string 'YYYY-MM-DD' como un objeto date/datetime.
    """
    
    # --- INICIO DE LA CORRECCIÓN ---
    # Verificamos si la fecha ya es un objeto de fecha/datetime
    if isinstance(fecha, datetime):
        dia_del_mes = fecha.day
    elif hasattr(fecha, 'day'): # Cubre objetos date
        dia_del_mes = fecha.day
    else: # Si es un string, lo convertimos
        dia_del_mes = datetime.strptime(fecha, "%Y-%m-%d").day
    # --- FIN DE LA CORRECCIÓN ---

    rotacion = config['rotacion']
    grupos_config = config['grupos']
    
    # Usamos el operador módulo para crear un ciclo infinito de rotación
    # Restamos 1 porque los índices de las listas empiezan en 0
    indice_rotacion = (dia_del_mes - 1) % len(rotacion)
    
    grupos_a_jugar = rotacion[indice_rotacion]
    
    numeros_a_jugar = []
    for grupo_id in grupos_a_jugar:
        numeros_a_jugar.extend(grupos_config[grupo_id])
    
    # Usamos set para eliminar duplicados (si los hubiera) y luego lo convertimos a lista
    numeros_a_jugar = sorted(list(set(numeros_a_jugar)))
    
    return {
        "fecha": fecha.strftime("%Y-%m-%d") if hasattr(fecha, 'strftime') else str(fecha),
        "grupos_jugados": grupos_a_jugar,
        "numeros_jugados": numeros_a_jugar
    }