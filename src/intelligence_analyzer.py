# src/intelligence_analyzer.py (Versión 2 - Multi-Ventana)

from datetime import datetime, timedelta
import pandas as pd

def get_group_for_number(number, groups_config):
    """Función de ayuda para encontrar a qué grupo pertenece un número."""
    for group_name, numbers in groups_config.items():
        if number in numbers:
            return group_name
    return None

def calculate_scores_for_window(historial_window_df, franja_a_predecir, grupos_activos, fecha_referencia):
    """Calcula las puntuaciones de frecuencia y recencia para una ventana de tiempo específica."""
    if historial_window_df.empty:
        return {grupo: 0 for grupo in grupos_activos.keys()}

    # Aseguramos que es una copia para evitar SettingWithCopyWarning
    df = historial_window_df.copy()
    
    df['grupo_acertado'] = df[franja_a_predecir].apply(
        lambda x: get_group_for_number(x, grupos_activos)
    )

    nombres_de_grupos = list(grupos_activos.keys())
    frecuencia = df['grupo_acertado'].value_counts().reindex(nombres_de_grupos, fill_value=0)

    recencia = {}
    for grupo in nombres_de_grupos:
        ultimas_apariciones = df[df['grupo_acertado'] == grupo]
        if not ultimas_apariciones.empty:
            ultimo_dia = ultimas_apariciones['fecha'].max()
            dias_pasados = (fecha_referencia - ultimo_dia).days
            # Puntuación de recencia: más puntos cuanto más reciente
            recencia[grupo] = (len(df) - dias_pasados) / len(df) if len(df) > 0 else 0
        else:
            recencia[grupo] = 0
            
    puntuacion = {}
    peso_frecuencia = 0.70
    peso_recencia = 0.30

    # Normalizar frecuencia para que sea comparable
    total_sorteos = len(df)
    frecuencia_normalizada = frecuencia / total_sorteos if total_sorteos > 0 else frecuencia

    for grupo in nombres_de_grupos:
        puntuacion[grupo] = (frecuencia_normalizada.get(grupo, 0) * peso_frecuencia) + (recencia.get(grupo, 0) * peso_recencia)

    return puntuacion

def analyze_franja_and_predict_ranking(historial_completo_df, fecha_prediccion, franja_a_predecir, config, grupos_activos):
    """
    Analiza el historial usando múltiples ventanas de tiempo (7, 30, 90 días)
    y devuelve un ranking ponderado de los grupos más probables.
    """
    ventana_fin = fecha_prediccion - timedelta(days=1)
    
    ventanas = {
        'corto_plazo': 7,
        'medio_plazo': 30,
        'largo_plazo': 90
    }
    
    pesos_ventana = {
        'corto_plazo': 0.2,
        'medio_plazo': 0.3,
        'largo_plazo': 0.5  # La tendencia a largo plazo tiene más peso
    }

    puntuaciones_finales = {grupo: 0 for grupo in grupos_activos.keys()}

    for nombre_ventana, dias in ventanas.items():
        ventana_inicio = ventana_fin - timedelta(days=dias - 1)
        
        # Aseguramos que la fecha es tz-naive para la comparación
        historial_ventana = historial_completo_df[
            (historial_completo_df['fecha'] >= ventana_inicio) &
            (historial_completo_df['fecha'] <= ventana_fin)
        ]

        if len(historial_ventana) < dias: # No calcular si no hay suficientes datos para la ventana
             continue

        puntuaciones_ventana = calculate_scores_for_window(
            historial_ventana, franja_a_predecir, grupos_activos, ventana_fin
        )

        for grupo, puntaje in puntuaciones_ventana.items():
            puntuaciones_finales[grupo] += puntaje * pesos_ventana[nombre_ventana]
            
    # Si ninguna ventana tuvo suficientes datos, devolver un ranking por defecto
    if all(p == 0 for p in puntuaciones_finales.values()):
        return list(grupos_activos.keys())

    # Ordenar los grupos por la puntuación final ponderada
    ranking_ordenado = sorted(puntuaciones_finales.keys(), key=puntuaciones_finales.get, reverse=True)
    
    return ranking_ordenado