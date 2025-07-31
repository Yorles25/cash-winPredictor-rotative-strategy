from .intelligence_analyzer import analyze_franja_and_predict

def generar_predicciones_del_dia(historial_completo_df, fecha_prediccion, config, grupos_activos):
    # NOTA: Ahora recibe 'grupos_activos'
    franjas = config.get("franjas", ["Morning", "Matinee", "Afternoon", "Evening", "LateNight"])
    predicciones = {}

    for franja in franjas:
        grupo_predicho = analyze_franja_and_predict(
            historial_completo_df,
            fecha_prediccion,
            franja,
            config,
            grupos_activos # Y se la pasa al cerebro
        )
        predicciones[franja] = grupo_predicho
        
    return predicciones