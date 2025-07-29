# main.py
from src.utils import cargar_json
from src.generator import generar_jugada_por_fecha
from src.evaluator import evaluar_jugada
from src.reporter import guardar_reporte_csv

def ejecutar_backtesting():
    """
    Flujo principal para ejecutar el análisis histórico (backtesting).
    """
    print("--- Iniciando Backtesting de Estrategia Rotativa ---")
    
    # 1. Cargar configuración e historial
    config = cargar_json("data/strategy_config.json")
    historial_sorteos = cargar_json("data/historical_draws.json")
    
    if not config or not historial_sorteos:
        print("Error al cargar archivos de configuración o datos. Abortando.")
        return

    resultados_finales = []
    
    # 2. Iterar sobre cada sorteo histórico
    for sorteo_real in historial_sorteos:
        fecha = sorteo_real["fecha"]
        print(f"Procesando fecha: {fecha}...")
        
        # 3. Generar la jugada que se *hubiera* hecho ese día
        jugada_generada = generar_jugada_por_fecha(fecha, config)
        
        # 4. Evaluar la jugada contra el resultado real
        if jugada_generada:
            resultado_dia = evaluar_jugada(jugada_generada, sorteo_real, config)
            resultados_finales.append(resultado_dia)

    # 5. Guardar el reporte final
    if resultados_finales:
        ruta_reporte = "outputs/backtesting_report.csv"
        guardar_reporte_csv(resultados_finales, ruta_reporte)
    else:
        print("No se generaron resultados para analizar.")
        
    print("--- Backtesting Finalizado ---")

if __name__ == "__main__":
    ejecutar_backtesting()