# src/evaluator.py

def evaluar_dia_completo_con_motor_financiero(financial_engine, ranking_predicciones_dia, resultados_reales_dia):
    """
    Delega la evaluación financiera de cada franja al motor financiero.
    """
    resultados_franjas = []
    
    for franja, ranking_predicho in ranking_predicciones_dia.items():
        if franja not in resultados_reales_dia or resultados_reales_dia[franja] is None:
            continue

        numero_real = resultados_reales_dia[franja]
        
        # Llama al motor financiero para hacer todo el trabajo pesado
        resultado_franja = financial_engine.calculate_franja_finance(franja, ranking_predicho, numero_real)
        
        # Prepara los datos para la interfaz
        resultados_franjas.append({
            "franja": franja,
            "numero_real": numero_real,
            "grupo_real": resultado_franja['grupo_real'],
            "ranking_predicho": ranking_predicho,
            "ubicacion_acierto": resultado_franja['ubicacion_acierto'],
            "financials": resultado_franja['financials'],
            "ganancia_neta_franja": resultado_franja['total_ganancia_franja']
        })
        
    return resultados_franjas