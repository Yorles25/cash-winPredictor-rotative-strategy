# Contenido para app.py (VERSIÓN FINAL CON EVALUADOR)

import streamlit as st
import pandas as pd
import json

# Importamos TODAS nuestras funciones, incluyendo el nuevo evaluador
from src.utils import load_historical_data
from src.generator import generate_predictions, load_strategy_config
from src.evaluator import evaluate_prediction # <-- NUEVO IMPORT

# --- Configuración de la Página ---
st.set_page_config(page_title="🔮 Predictor de Sorteos", page_icon="⚙️", layout="wide")

# --- Cargar Configuración ---
if 'config' not in st.session_state:
    st.session_state.config = load_strategy_config()
config = st.session_state.config

# --- Título ---
st.title("🔮 Laboratorio Predictivo de Sorteos")
st.divider()

# ==============================================================================
# --- PANEL LATERAL (SIDEBAR) ---
# ==============================================================================
st.sidebar.header("Panel de Control ⚙️")

# --- Control de Estrategias ---
st.sidebar.subheader("1. Seleccionar Estrategias")
strategies_config = config.get('strategies', {})
active_strategies_flags = {}
for name, params in strategies_config.items():
    is_active = st.sidebar.checkbox(
        f"{name.capitalize()} (Peso: {params.get('weight', 1.0)})", 
        value=params.get('enabled', False),
        key=f"strategy_{name}"
    )
    active_strategies_flags[name] = is_active

# --- Botón de Predicción ---
st.sidebar.subheader("2. Generar Predicción")
if st.sidebar.button("Generar", type="primary", use_container_width=True):
    with st.spinner('Aplicando estrategias...'):
        st.session_state.predictions = generate_predictions(enabled_strategies=active_strategies_flags)

st.sidebar.divider()

# ==============================================================================
# --- ÁREA PRINCIPAL ---
# ==============================================================================

# --- Columna de Predicción y Evaluación ---
col1, col2 = st.columns(2)

with col1:
    st.header("🎯 Predicción")
    if 'predictions' in st.session_state and st.session_state.predictions:
        predictions = st.session_state.predictions
        st.code(", ".join(map(str, predictions)), language="text")
        
        st.subheader("🔍 Evaluar Predicción")
        # Campo para que el usuario ingrese los números del sorteo real
        result_input = st.text_input(
            "Ingresa los números ganadores separados por comas (ej: 5,9,15,18,25)",
            key="result_input"
        )
        
        if result_input:
            try:
                # Procesamos la entrada del usuario
                result_numbers = [int(num.strip()) for num in result_input.split(',')]
                
                # Llamamos a nuestro nuevo módulo evaluador
                evaluation = evaluate_prediction(predictions, result_numbers)
                
                # Mostramos el resultado de la evaluación
                hits = evaluation['hits']
                matched = evaluation['matched_numbers']
                
                if hits > 0:
                    st.success(f"¡Felicitaciones! Acertaste {hits} número(s): **{', '.join(map(str, matched))}**")
                else:
                    st.error("No hubo aciertos esta vez. ¡Mejor suerte para la próxima!")
            
            except ValueError:
                st.warning("Por favor, ingresa solo números separados por comas.")

    else:
        st.info("Presiona 'Generar' en el panel de la izquierda para obtener una predicción.")

# --- Columna de Historial ---
with col2:
    st.header("📚 Histórico de Sorteos")
    if st.checkbox("Mostrar historial", value=False):
        historical_data = load_historical_data()
        if historical_data:
            df_history = pd.DataFrame.from_dict(historical_data, orient='index')
            df_history.index.name = "Fecha"
            st.dataframe(df_history.sort_index(ascending=False), use_container_width=True)