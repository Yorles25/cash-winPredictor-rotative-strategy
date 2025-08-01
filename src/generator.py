# src/generator.py

# Ahora importamos la nueva función con el nombre mejorado
from .intelligence_analyzer import analyze_franja_and_predict_ranking

def generar_predicciones_del_dia(historial_completo_df, fecha_prediccion, config, grupos_activos):
    """
    Orquesta la generación de predicciones para todas las franjas de un día.
    Ahora devuelve el ranking completo (lista de grupos) para cada franja.
    """
    franjas = config.get("franjas", ["Morning", "Matinee", "Afternoon", "Evening", "LateNight"])
    predicciones_con_ranking = {}

    for franja in franjas:
        # Llama a la nueva función del cerebro para obtener el ranking
        ranking_de_grupos = analyze_franja_and_predict_ranking(
            historial_completo_df,
            fecha_prediccion,
            franja,
            config,
            grupos_activos
        )
        # Guarda la lista completa del ranking para esta franja
        predicciones_con_ranking[franja] = ranking_de_grupos
        
    return predicciones_con_ranking