import streamlit as st
import pandas as pd
from datetime import datetime

# Importamos las funciones del "cerebro" del sistema
from src.utils import cargar_json
from src.generator import generar_jugada_por_fecha
from src.evaluator import evaluar_jugada

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Cash WinPredictor",
    page_icon="🎯",
    layout="wide"
)

# --- CARGA DE DATOS (una sola vez para mejorar rendimiento) ---
@st.cache_data
def cargar_datos():
    config = cargar_json('data/strategy_configuration.json')
    historial_sorteos = cargar_json('data/historical_draws.json')
    historial_sorteos_dt = {datetime.strptime(k, "%Y-%m-%d").date(): v for k, v in historial_sorteos.items()}
    return config, historial_sorteos_dt

config, historial_sorteos = cargar_datos()

# --- FUNCIÓN DE BACKTESTING (una sola vez para mejorar rendimiento) ---
@st.cache_data
def ejecutar_backtesting_completo():
    resultados = []
    for fecha_sorteo, numeros_sorteados in historial_sorteos.items():
        jugada = generar_jugada_por_fecha(fecha_sorteo, config)
        resultado_eval = evaluar_jugada(jugada, numeros_sorteados, config)
        resultados.append(resultado_eval)
    df = pd.DataFrame(resultados)
    df['fecha'] = pd.to_datetime(df['fecha'])
    return df

resultados_df = ejecutar_backtesting_completo()

# --- BARRA LATERAL DE NAVEGACIÓN ---
st.sidebar.title("Panel de Navegación")
seccion = st.sidebar.radio(
    "Elige una sección:",
    ("🔮 Jugada Recomendada", "📈 Análisis de Backtesting", "🔴 Módulo en Vivo"),
    key="nav_radio"
)
st.sidebar.markdown("---")

# =============================================================================
# INICIO DE LA CORRECCIÓN: AÑADIR EL VISOR JSON A LA BARRA LATERAL
# =============================================================================
st.sidebar.subheader("⚙️ Configuración Activa")
# Usamos la variable 'config' que ya cargamos una vez al inicio
st.sidebar.json(config, expanded=False) 
# =============================================================================
# FIN DE LA CORRECCIÓN
# =============================================================================

st.sidebar.markdown("---")
# Mantenemos la información útil al final
st.sidebar.info("La configuración de la estrategia se gestiona en `data/strategy_configuration.json`.")


# --- TÍTULO PRINCIPAL ---
st.title("🎯 Cash WinPredictor")
st.caption("Herramienta para analizar y simular tu estrategia de apuestas basada en rotación de grupos.")


# =============================================================================
# CONTENIDO PRINCIPAL (SE MUESTRA SEGÚN LA SELECCIÓN DE LA BARRA LATERAL)
# =============================================================================

if seccion == "🔮 Jugada Recomendada":
    st.header("🔮 Jugada Recomendada por Fecha")
    fecha_seleccionada = st.date_input(
        "Selecciona una fecha para ver la jugada recomendada:",
        value=datetime.today(),
        help="Elige cualquier fecha para ver qué grupos y números correspondían según tu estrategia.",
        key="rec_date"
    )
    if fecha_seleccionada:
        jugada_hoy = generar_jugada_por_fecha(fecha_seleccionada, config)
        col1, col2 = st.columns(2)
        with col1:
            st.metric(label="Fecha Seleccionada", value=fecha_seleccionada.strftime("%Y-%m-%d"))
        with col2:
            st.metric(label="Grupos a Jugar", value=" + ".join(jugada_hoy['grupos_jugados']))
        st.subheader("Números a Jugar:")
        numeros_str = " - ".join(map(str, sorted(jugada_hoy['numeros_jugados'])))
        st.code(numeros_str, language=None)

elif seccion == "📈 Análisis de Backtesting":
    st.header("📈 Análisis de Backtesting")
    st.caption("Resultados de la estrategia aplicada a los sorteos históricos.")
    
    if not resultados_df.empty:
        min_fecha = resultados_df['fecha'].min().date()
        max_fecha = resultados_df['fecha'].max().date()

        date_range = st.date_input(
            "Selecciona un rango de fechas para el análisis:",
            value=(min_fecha, max_fecha),
            min_value=min_fecha,
            max_value=max_fecha,
            help="Las métricas y la tabla se actualizarán para mostrar solo los datos de este período.",
            key="backtest_date_range"
        )

        if isinstance(date_range, tuple) and len(date_range) == 2:
            fecha_inicio, fecha_fin = date_range

            if fecha_inicio <= fecha_fin:
                df_filtrado = resultados_df[
                    (resultados_df['fecha'].dt.date >= fecha_inicio) & 
                    (resultados_df['fecha'].dt.date <= fecha_fin)
                ]
                ganancia_neta_total = int(df_filtrado['ganancia'].sum())
                total_aciertos = int(df_filtrado['cantidad_aciertos'].sum())
                dias_totales = len(df_filtrado)
                dias_con_ganancia = int((df_filtrado['ganancia'] > 0).sum())
                
                col1, col2, col3 = st.columns(3)
                col1.metric("Ganancia Neta Total", f"${ganancia_neta_total}", f"{ganancia_neta_total}")
                col2.metric("Total de Aciertos", f"{total_aciertos}")
                col3.metric("Días con Ganancia", f"{dias_con_ganancia} de {dias_totales}")
                
                st.markdown("### Detalle de Sorteos")
                df_display = df_filtrado.sort_values(by="fecha", ascending=False).reset_index(drop=True)
                st.dataframe(df_display[[
                    "fecha", "grupos_jugados", "cantidad_aciertos", "ganancia", 
                    "premio", "costo", "numeros_jugados", "numeros_sorteados", "aciertos"
                ]])
    else:
        st.warning("No hay datos históricos para analizar. Revisa el archivo `data/historical_draws.json`.")

elif seccion == "🔴 Módulo en Vivo":
    st.header("🔴 Módulo en Vivo: Evaluar Sorteo")
    st.caption("Introduce los números de un sorteo para ver el resultado de tu jugada recomendada.")
    fecha_evaluar = st.date_input(
        "Selecciona la fecha del sorteo que quieres evaluar:",
        value=datetime.today(),
        help="Puedes evaluar sorteos pasados si no tuviste la oportunidad de hacerlo en su día.",
        key="live_date"
    )
    if fecha_evaluar:
        jugada_para_evaluar = generar_jugada_por_fecha(fecha_evaluar, config)
        st.write(f"Tu jugada recomendada para el **{fecha_evaluar.strftime('%Y-%m-%d')}** fue:")
        st.code(" + ".join(jugada_para_evaluar['grupos_jugados']) + " -> " + " - ".join(map(str, sorted(jugada_para_evaluar['numeros_jugados']))), language=None)
        
        numeros_sorteo_input = st.text_input(
            "Ingresa los 5 números sorteados, separados por comas (ej: 3,8,11,14,15)",
            key="live_text_input"
        )

        if st.button("Evaluar mi Jugada", key="live_button"):
            if numeros_sorteo_input:
                try:
                    numeros_sorteados_live = [int(n.strip()) for n in numeros_sorteo_input.split(',')]
                    if len(numeros_sorteados_live) != 5:
                        st.error("Por favor, ingresa exactamente 5 números.")
                    else:
                        resultado_live = evaluar_jugada(jugada_para_evaluar, numeros_sorteados_live, config)
                        st.success("¡Evaluación Completa!")
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Aciertos", resultado_live['cantidad_aciertos'])
                        col2.metric("Premio", f"${resultado_live['premio']}")
                        col3.metric("Ganancia Neta", f"${resultado_live['ganancia']}", delta=f"{resultado_live['ganancia']}")
                        st.write("Números acertados:")
                        st.code(str(resultado_live['aciertos']), language=None)
                except ValueError:
                    st.error("Formato inválido. Asegúrate de ingresar solo números separados por comas.")