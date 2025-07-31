from datetime import datetime, timedelta
import pandas as pd

def get_group_for_number(number, groups_config):
    for group_name, numbers in groups_config.items():
        if number in numbers:
            return group_name
    return None

def analyze_franja_and_predict(historial_completo_df, fecha_prediccion, franja_a_predecir, config, grupos_activos):
    # NOTA: Ahora recibe 'grupos_activos'
    ventana_fin = fecha_prediccion - timedelta(days=1)
    ventana_inicio = ventana_fin - timedelta(days=29)

    historial_franja = historial_completo_df[
        (historial_completo_df['fecha'] >= ventana_inicio) &
        (historial_completo_df['fecha'] <= ventana_fin)
    ].copy()
    
    if historial_franja.empty:
        return list(grupos_activos.keys())[0] # Devuelve el primer nombre de grupo (ej. 'A')

    historial_franja['grupo_acertado'] = historial_franja[franja_a_predecir].apply(
        lambda x: get_group_for_number(x, grupos_activos)
    )

    nombres_de_grupos = list(grupos_activos.keys())
    frecuencia = historial_franja['grupo_acertado'].value_counts().reindex(nombres_de_grupos, fill_value=0)

    recencia = {}
    for grupo in nombres_de_grupos:
        ultimas_apariciones = historial_franja[historial_franja['grupo_acertado'] == grupo]
        if not ultimas_apariciones.empty:
            ultimo_dia = ultimas_apariciones['fecha'].max()
            dias_pasados = (ventana_fin - ultimo_dia).days
            recencia[grupo] = 30 - dias_pasados
        else:
            recencia[grupo] = 0

    puntuacion = {}
    peso_frecuencia = 0.70
    peso_recencia = 0.30

    for grupo in nombres_de_grupos:
        puntuacion[grupo] = (frecuencia.get(grupo, 0) * peso_frecuencia) + (recencia.get(grupo, 0) * peso_recencia)

    return max(puntuacion, key=puntuacion.get)