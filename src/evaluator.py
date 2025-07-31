def evaluar_dia_completo(predicciones_dia, resultados_reales_dia, config, grupos_activos):
    # NOTA: Ahora recibe 'grupos_activos'
    costo_por_numero = config.get('costo_por_numero', 1)
    premio_por_acierto = config.get('premio_por_acierto', 5)
    
    resultados_franjas = []
    total_aciertos_dia = 0
    total_premio_dia = 0
    total_costo_dia = 0

    for franja, grupo_predicho in predicciones_dia.items():
        if franja not in resultados_reales_dia:
            continue

        numero_real = resultados_reales_dia[franja]
        numeros_jugados = grupos_activos.get(grupo_predicho, [])
        
        acerto = numero_real in numeros_jugados
        cantidad_aciertos = 1 if acerto else 0
        
        costo_franja = len(numeros_jugados) * costo_por_numero
        premio_franja = cantidad_aciertos * premio_por_acierto
        ganancia_franja = premio_franja - costo_franja
        
        total_aciertos_dia += cantidad_aciertos
        total_premio_dia += premio_franja
        total_costo_dia += costo_franja

        resultados_franjas.append({
            "franja": franja,
            "grupo_predicho": grupo_predicho,
            "numeros_jugados": numeros_jugados,
            "numero_real": numero_real,
            "resultado": "✅ ACIERTO" if acerto else "❌ FALLO",
            "ganancia_franja": ganancia_franja
        })

    ganancia_neta_dia = total_premio_dia - total_costo_dia
    
    return {
        "detalle_franjas": resultados_franjas,
        "total_aciertos_dia": total_aciertos_dia,
        "ganancia_neta_dia": ganancia_neta_dia
    }