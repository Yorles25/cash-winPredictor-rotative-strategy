# Contenido para app.py (VERSIÓN CON TABLA UNIFICADA)

import streamlit as st
import pandas as pd
from datetime import datetime

# Importamos las funciones de nuestros módulos
from src.utils import load_historical_data
from src.generator import generate_predictions, load_strategy_config
from src.evaluator import evaluate_prediction

def run_backtesting_unificado(config: dict, historical_data: dict):
    """
    Ejecuta el backtesting y genera UNA SOLA tabla con toda la información:
    Jugada, Resultado, Aciertos y Análisis Financiero.
    """
    if not historical_data:
        return pd.DataFrame()

    df = pd.DataFrame.from_dict(historical_data, orient='index', columns=[f'n{i+1}' for i in range(5)])
    df.index = pd.to_datetime(df.index)
    df.sort_index(inplace=True)

    results_log = []
    progress_bar = st.progress(0, text="Iniciando análisis...")
    status_text = st.empty()

    for i, (current_date, row) in enumerate(df.iterrows()):
        actual_result = row.tolist()
        
        # Generamos la predicción rotativa para ese día específico
        prediction = generate_predictions(fecha_str=current_date.strftime('%Y-%m-%d'))
        
        evaluation = evaluate_prediction(prediction, actual_result)
        
        # Calculamos el control financiero
        costo = len(prediction) * config['project_settings']['costo_por_numero']
        premio = evaluation['hits'] * config['project_settings']['premio_por_acierto']
        ganancia = premio - costo
        
        # Obtenemos los grupos jugados para mostrarlos en la tabla
        paso_del_ciclo = (current_date.timetuple().tm_yday - 1) % len(config['rotacion'])
        grupos_jugados_str = "+".join(config['rotacion'][paso_del_ciclo])

        # Creamos el registro con TODAS las columnas que quieres ver
        results_log.append({
            "Fecha": current_date.strftime('%Y-%m-%d'),
            "Números sorteados": ", ".join(map(str, actual_result)),
            "Grupos jugados": grupos_jugados_str,
            "Números jugados": ", ".join(map(str, prediction)),
            "Aciertos": evaluation['hits'],
            "Números acertados": ", ".join(map(str, evaluation['matched_numbers'])),
            "Costo ($)": costo,
            "Premio ($)": premio,
            "Ganancia ($)": ganancia
        })
        
        # Actualizamos la barra de progreso
        progress = (i + 1) / len(df)
        progress_bar.progress(progress, text=f"Analizando {current_date.strftime('%Y-%m-%d')}...")

    status_text.success("¡Análisis de rendimiento completado!")
    progress_bar.empty()
    
    # Devolvemos el DataFrame con el registro completo
    return pd.DataFrame(results_log)


# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="♟️ Predictor Rotativo", page_icon="⚙️", layout="wide")
config = load_strategy_config()
historical_data = load_historical_data()

# --- TÍTULO Y DESCRIPCIÓN ---
st.title("♟️ Sistema de Estrategia Rotativa")
st.markdown("Análisis de rendimiento y control financiero de la estrategia de rotación de grupos.")
st.divider()

# --- SECCIÓN DE ANÁLISIS ---
st.header("Análisis de Rendimiento (Backtesting)")
st.write("Presiona el botón para ejecutar un análisis completo del historial usando la estrategia rotativa.")

if st.button("Ejecutar Análisis Completo", type="primary", use_container_width=True):
    # Llamamos a nuestra función que genera la tabla unificada
    reporte_completo_df = run_backtesting_unificado(config, historical_data)
    
    if not reporte_completo_df.empty:
        st.subheader("Resumen Financiero Mensual")
        
        # Cálculos para las métricas
        total_invertido = reporte_completo_df['Costo ($)'].sum()
        total_premios = reporte_completo_df['Premio ($)'].sum()
        ganancia_neta = reporte_completo_df['Ganancia ($)'].sum()
        
        # Mostramos las métricas de resumen
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Invertido", f"${total_invertido}")
        col2.metric("Total en Premios", f"${total_premios}")
        col3.metric("Ganancia Neta", f"${ganancia_neta}", delta=f"{ganancia_neta} USD")
        
        st.subheader("Reporte Detallado por Día")
        # Mostramos la tabla unificada con todas las columnas
        # Ocultamos el índice del DataFrame para una vista más limpia
        st.dataframe(reporte_completo_df.set_index('Fecha'), use_container_width=True)

    else:
        st.warning("No se pudo generar el reporte. Verifica el archivo de datos históricos.")