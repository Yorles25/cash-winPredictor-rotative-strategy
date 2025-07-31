import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

# Importamos las funciones del cerebro V2
from src.utils import cargar_json
from src.generator import generar_predicciones_del_dia
from src.evaluator import evaluar_dia_completo

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Cash WinPredictor V2.4", page_icon="🔬", layout="wide")

# --- CARGA DE DATOS ---
@st.cache_data
def cargar_datos_y_preprocesar():
    config = cargar_json('data/strategy_configuration.json')
    historial_sorteos = cargar_json('data/historical_draws.json')
    
    historial_list = []
    for fecha_str, franjas in historial_sorteos.items():
        try:
            fila = {'fecha': datetime.strptime(fecha_str, "%Y-%m-%d").date()}
            fila.update(franjas)
            historial_list.append(fila)
        except (ValueError, TypeError):
            continue
            
    df = pd.DataFrame(historial_list)
    df = df.sort_values(by='fecha', ascending=True).reset_index(drop=True)
    return config, df

config, historial_df = cargar_datos_y_preprocesar()

# --- BARRA LATERAL ---
st.sidebar.title("Panel de Control")

# --- INICIO DE LA MODIFICACIÓN: SELECTOR DE ESTRATEGIA ---
st.sidebar.subheader("🔬 Selección de Estrategia")

# Leemos las estrategias disponibles desde el JSON
estrategias_disponibles = list(config.get('group_definitions', {}).keys())

if not estrategias_disponibles:
    st.sidebar.error("No se encontraron definiciones de grupos en `strategy_configuration.json`.")
    st.stop()

estrategia_seleccionada = st.sidebar.selectbox(
    "Elige la definición de grupos a utilizar:",
    options=estrategias_disponibles,
    key="strategy_selector"
)

# Obtenemos la configuración de grupos activa
grupos_activos = config['group_definitions'][estrategia_seleccionada]

# --- FIN DE LA MODIFICACIÓN ---

st.sidebar.markdown("---")
seccion = st.sidebar.radio("Elige una sección:", ("📈 Análisis de Backtesting", "🔮 Jugada Recomendada", "🔴 Módulo en Vivo"), key="nav_radio")
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración Activa")
st.sidebar.json({"grupos_seleccionados": grupos_activos}, expanded=False)


# --- FUNCIÓN DE BACKTESTING V2.4 (ahora depende de la estrategia) ---
@st.cache_data(show_spinner="Ejecutando backtesting con la estrategia seleccionada...")
def ejecutar_backtesting_dinamico(_config_dict, _historial_completo_df, _grupos_activos):
    resultados_totales = []
    fechas_para_predecir = _historial_completo_df['fecha'].unique()

    if len(fechas_para_predecir) < 31:
        return pd.DataFrame()

    for i, fecha_actual in enumerate(fechas_para_predecir):
        if i < 30: continue
        
        historial_para_analisis = _historial_completo_df[_historial_completo_df['fecha'] < fecha_actual]
        predicciones = generar_predicciones_del_dia(historial_para_analisis, fecha_actual, _config_dict, _grupos_activos)
        resultados_reales = _historial_completo_df[_historial_completo_df['fecha'] == fecha_actual].iloc[0].to_dict()
        resultado_dia = evaluar_dia_completo(predicciones, resultados_reales, _config_dict, _grupos_activos)

        for detalle_franja in resultado_dia['detalle_franjas']:
            resultados_totales.append({
                'fecha': fecha_actual,
                'franja': detalle_franja['franja'],
                'grupo_predicho': detalle_franja['grupo_predicho'],
                'numeros_jugados': detalle_franja['numeros_jugados'],
                'numero_real': detalle_franja['numero_real'],
                'resultado': detalle_franja['resultado'],
                'ganancia_franja': detalle_franja['ganancia_franja']
            })
        
    df_final = pd.DataFrame(resultados_totales)
    if not df_final.empty:
        df_final['fecha'] = pd.to_datetime(df_final['fecha'])
    return df_final

# --- TÍTULO PRINCIPAL ---
st.title(f"🧠 Cash WinPredictor - {estrategia_seleccionada}")

# --- CONTENIDO PRINCIPAL ---
if seccion == "📈 Análisis de Backtesting":
    st.header("📈 Resultados del Backtesting")
    
    # El backtesting ahora se ejecuta con los grupos activos
    backtesting_results_df = ejecutar_backtesting_dinamico(config, historial_df, grupos_activos)
    
    if backtesting_results_df.empty:
        st.error("No se pudo ejecutar el backtesting.")
    else:
        # ... el resto de la sección de backtesting con su filtro ... (código sin cambios)
        st.subheader("Análisis por Período")

        min_fecha = backtesting_results_df['fecha'].min().date()
        max_fecha = backtesting_results_df['fecha'].max().date()
        
        date_range = st.date_input("Selecciona un rango de fechas para analizar:", value=(min_fecha, max_fecha), min_value=min_fecha, max_value=max_fecha, key="results_date_range")
        
        if isinstance(date_range, tuple) and len(date_range) == 2:
            fecha_inicio, fecha_fin = date_range
            
            df_filtrado = backtesting_results_df[(backtesting_results_df['fecha'].dt.date >= fecha_inicio) & (backtesting_results_df['fecha'].dt.date <= fecha_fin)]

            st.subheader("Métricas para el Período Seleccionado")
            
            total_franjas = len(df_filtrado)
            total_aciertos = len(df_filtrado[df_filtrado['resultado'] == "✅ ACIERTO"])
            tasa_acierto = (total_aciertos / total_franjas) * 100 if total_franjas > 0 else 0
            balance_total = df_filtrado['ganancia_franja'].sum()

            col1, col2, col3 = st.columns(3)
            col1.metric("Tasa de Acierto", f"{tasa_acierto:.2f}%")
            col2.metric("Balance Neto", f"${balance_total:,.2f}")
            col3.metric("Aciertos / Jugadas", f"{total_aciertos} / {total_franjas}")

            st.subheader("Detalle de Sorteos del Período")
            df_display = df_filtrado.sort_values(by=['fecha'], ascending=False).reset_index(drop=True)
            st.dataframe(df_display, use_container_width=True)

elif seccion == "🔮 Jugada Recomendada":
    st.header("🔮 Jugada Recomendada por Fecha")
    fecha_a_predecir = st.date_input("Selecciona una fecha para generar la predicción:", value=datetime.today().date() + timedelta(days=1), key="rec_date")
    
    if st.button("Generar Predicción", key="rec_button"):
        # Llama al generador con los grupos activos
        predicciones_hoy = generar_predicciones_del_dia(historial_df[historial_df['fecha'] < fecha_a_predecir], fecha_a_predecir, config, grupos_activos)
        st.success(f"Predicciones generadas para el **{fecha_a_predecir.strftime('%Y-%m-%d')}**")
        
        df_predicciones = pd.DataFrame(list(predicciones_hoy.items()), columns=['Franja', 'Grupo Predicho'])
        df_predicciones['Números a Jugar'] = df_predicciones['Grupo Predicho'].apply(lambda g: grupos_activos.get(g, []))
        st.table(df_predicciones)

elif seccion == "🔴 Módulo en Vivo":
    st.header("🔴 Módulo en Vivo: Evaluar Sorteo")
    fecha_evaluar = st.date_input("1. Selecciona la fecha del sorteo:", value=datetime.today().date(), key="live_date")
    
    # Llama al generador con los grupos activos
    predicciones_para_eval = generar_predicciones_del_dia(historial_df[historial_df['fecha'] < fecha_evaluar], fecha_evaluar, config, grupos_activos)
    
    st.write("2. Jugada recomendada para ese día:")
    df_pred_eval = pd.DataFrame(list(predicciones_para_eval.items()), columns=['Franja', 'Grupo Predicho'])
    df_pred_eval['Números Recomendados'] = df_pred_eval['Grupo Predicho'].apply(lambda g: grupos_activos.get(g, []))
    st.table(df_pred_eval)

    st.write("3. Ingresa los resultados reales:")
    
    resultados_reales_live = {}
    franjas_nombres = config.get("franjas", [])
    
    cols = st.columns(len(franjas_nombres))
    for i, franja in enumerate(franjas_nombres):
        resultados_reales_live[franja] = cols[i].number_input(franja, min_value=1, max_value=15, step=1, key=f"live_input_{franja}")

    if st.button("Evaluar mi Jugada", key="live_button"):
        # Llama al evaluador con los grupos activos
        resultado_live = evaluar_dia_completo(predicciones_para_eval, resultados_reales_live, config, grupos_activos)
        
        st.success("¡Evaluación Completa!")
        # ... (código para mostrar resultados sin cambios)
        col1, col2 = st.columns(2)
        col1.metric("Aciertos en el día", resultado_live['total_aciertos_dia'])
        col2.metric("Ganancia Neta del Día", f"${resultado_live['ganancia_neta_dia']}", delta=f"{resultado_live['ganancia_neta_dia']}")
        
        st.write("Detalle por franja:")
        st.table(pd.DataFrame(resultado_live['detalle_franjas']))