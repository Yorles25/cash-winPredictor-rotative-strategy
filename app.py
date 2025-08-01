import streamlit as st
import pandas as pd
from datetime import datetime, timedelta

from src.utils import cargar_json
from src.generator import generar_predicciones_del_dia
from src.evaluator import evaluar_dia_completo_con_motor_financiero
from src.financial_engine import FinancialEngine

st.set_page_config(page_title="Cash WinPredictor V4.1", page_icon="💰", layout="wide")

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
        except (ValueError, TypeError): continue
    df = pd.DataFrame(historial_list)
    df['fecha'] = pd.to_datetime(df['fecha']).dt.date
    df = df.sort_values(by='fecha', ascending=True).reset_index(drop=True)
    return config, df

config, historial_df = cargar_datos_y_preprocesar()

st.sidebar.title("Panel de Control")
st.sidebar.subheader("🔬 Selección de Estrategia")
estrategias_disponibles = list(config.get('group_definitions', {}).keys())
estrategia_seleccionada = st.sidebar.selectbox("Elige la definición de grupos:", options=estrategias_disponibles, key="strategy_selector")
grupos_activos = config['group_definitions'][estrategia_seleccionada]

st.sidebar.markdown("---")
seccion = st.sidebar.radio("Elige una sección:", ("📈 Análisis de Backtesting", "🔮 Jugada Recomendada", "🔴 Módulo en Vivo", "📜 Historial de Sorteos"), key="nav_radio")
st.sidebar.markdown("---")
st.sidebar.subheader("⚙️ Configuración Activa")
st.sidebar.json({"grupos_seleccionados": grupos_activos}, expanded=False)

st.title(f"🧠 Cash WinPredictor - {estrategia_seleccionada}")

if seccion == "📈 Análisis de Backtesting":
    st.header("📈 Resultados del Backtesting")
    st.sidebar.subheader("📊 Estrategia Financiera")
    estrategia_financiera = st.sidebar.radio("Elige la estrategia de inversión:", ("Apuesta Fija (Precisión)", "Progresiva por Carriles (Cobertura)"), key="financial_strategy")
    
    @st.cache_data(show_spinner="Ejecutando backtesting...")
    def ejecutar_backtesting_completo(_config, _historial_df, _grupos_activos):
        financial_engine = FinancialEngine(_config['franjas'], _grupos_activos, _config)
        resultados_totales = []
        fechas_para_predecir = _historial_df['fecha'].unique()
        if len(fechas_para_predecir) < 31: return pd.DataFrame()
        for i, fecha_actual in enumerate(fechas_para_predecir):
            if i < 30: continue
            historial_para_analisis = _historial_df[_historial_df['fecha'] < fecha_actual]
            predicciones_ranking = generar_predicciones_del_dia(historial_para_analisis, fecha_actual, _config, _grupos_activos)
            resultados_reales = _historial_df[_historial_df['fecha'] == fecha_actual].iloc[0].to_dict()
            resultado_dia = evaluar_dia_completo_con_motor_financiero(financial_engine, predicciones_ranking, resultados_reales)
            for detalle in resultado_dia:
                detalle['fecha'] = fecha_actual
                resultados_totales.append(detalle)
        df_final = pd.DataFrame(resultados_totales)
        if not df_final.empty: df_final['fecha'] = pd.to_datetime(df_final['fecha'])
        return df_final

    backtesting_results_df = ejecutar_backtesting_completo(config, historial_df, grupos_activos)
    
    if not backtesting_results_df.empty:
        st.subheader("Análisis por Período")
        min_fecha, max_fecha = backtesting_results_df['fecha'].min().date(), backtesting_results_df['fecha'].max().date()
        date_range = st.date_input("Selecciona un rango de fechas:", value=(min_fecha, max_fecha), min_value=min_fecha, max_value=max_fecha, key="results_date_range")
        if isinstance(date_range, tuple) and len(date_range) == 2:
            df_filtrado = backtesting_results_df[(backtesting_results_df['fecha'].dt.date >= date_range[0]) & (backtesting_results_df['fecha'].dt.date <= date_range[1])]
            
            if estrategia_financiera == "Progresiva por Carriles (Cobertura)":
                st.subheader("Métricas Financieras (Estrategia Progresiva)")
                # ... (código de métricas y panel sin cambios)
                inversion_total = sum(d['costo'] for r in df_filtrado['financials'] for d in r.values())
                premio_total = sum(d['premio'] for r in df_filtrado['financials'] for d in r.values())
                balance_total = df_filtrado['ganancia_neta_franja'].sum()
                roi = (balance_total / inversion_total) * 100 if inversion_total > 0 else 0
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Balance Neto", f"${balance_total:,.2f}")
                col2.metric("Inversión Total", f"${inversion_total:,.2f}")
                col3.metric("Premios Totales", f"${premio_total:,.2f}")
                col4.metric("ROI", f"{roi:.2f}%")
                st.subheader("Panel de Control Financiero")
                df_pivot = df_filtrado.copy()
                def format_cell_finance(row):
                    fin = row['financials']
                    p1, p2, p3 = (row['ranking_predicho'] + [None, None, None])[:3]
                    def format_line(col_name, pred_group, fin_data, is_winner):
                        style = "background-color: #28a745; color: white; padding: 2px; border-radius: 3px;" if is_winner else ""
                        line = f"<b>({col_name[0]}) {pred_group}</b> A:${fin_data['apuesta']} C:${fin_data['costo']} P:${fin_data['premio']} N:${fin_data['ganancia_neta']:+.2f}"
                        return f'<span style="{style}">{line}</span>' if is_winner else line
                    line1 = format_line("P", p1, fin.get('P', {}), row['ubicacion_acierto'] == 'Columna 1')
                    line2 = format_line("S", p2, fin.get('S', {}), row['ubicacion_acierto'] == 'Columna 2')
                    line3 = format_line("C", p3, fin.get('C', {}), row['ubicacion_acierto'] == 'Columna 3')
                    return f"<b>Resultado: {row['numero_real']}</b><br>{line1}<br>{line2}<br>{line3}<br><b>Neto Franja: ${row['ganancia_neta_franja']:,.2f}</b>"
                df_pivot['display_html'] = df_pivot.apply(format_cell_finance, axis=1)
                pivot_table = df_pivot.pivot_table(index='fecha', columns='franja', values='display_html', aggfunc='first').sort_index(ascending=False)
                st.markdown(pivot_table.to_html(escape=False), unsafe_allow_html=True)
            
            else: # Apuesta Fija (Precisión)
                # ... Lógica de visualización para Apuesta Fija aquí ...
                st.info("Visualización para Apuesta Fija (Precisión).")
                st.dataframe(df_filtrado)

elif seccion == "🔮 Jugada Recomendada":
    st.header("🔮 Jugada Recomendada por Fecha")
    fecha_a_predecir = st.date_input("Selecciona una fecha para la predicción:", value=datetime.today().date() + timedelta(days=1), key="rec_date")
    if st.button("Generar Predicción", key="rec_button"):
        with st.spinner("Analizando historial y generando ranking..."):
            predicciones_hoy = generar_predicciones_del_dia(historial_df[historial_df['fecha'] < fecha_a_predecir], fecha_a_predecir, config, grupos_activos)
            st.success(f"Ranking de predicciones para el **{fecha_a_predecir.strftime('%Y-%m-%d')}**")
            df_predicciones = pd.DataFrame(predicciones_hoy.items(), columns=['Franja', 'Ranking de Grupos (P, S, C)'])
            st.table(df_predicciones)

elif seccion == "🔴 Módulo en Vivo":
    st.header("🔴 Módulo en Vivo: Evaluar Sorteo")
    fecha_evaluar = st.date_input("1. Selecciona la fecha del sorteo:", value=datetime.today().date(), key="live_date")
    
    with st.spinner("Generando recomendaciones para la fecha seleccionada..."):
        predicciones_para_eval = generar_predicciones_del_dia(historial_df[historial_df['fecha'] < fecha_evaluar], fecha_evaluar, config, grupos_activos)
    
    st.write("2. Ranking de jugadas recomendadas para ese día:")
    st.table(pd.DataFrame(predicciones_para_eval.items(), columns=['Franja', 'Ranking de Grupos']))
    
    st.write("3. Ingresa los resultados reales:")
    resultados_reales_live = {}
    cols = st.columns(len(config.get("franjas", [])))
    for i, franja in enumerate(config.get("franjas", [])):
        resultados_reales_live[franja] = cols[i].number_input(franja, min_value=1, max_value=15, step=1, key=f"live_input_{franja}")
    
    if st.button("Evaluar mi Jugada", key="live_button"):
        if all(v > 0 for v in resultados_reales_live.values()):
            # Creamos un motor financiero temporal solo para este día
            live_engine = FinancialEngine(config['franjas'], grupos_activos, config)
            resultado_live = evaluar_dia_completo_con_motor_financiero(live_engine, predicciones_para_eval, resultados_reales_live)
            
            st.success("¡Evaluación Completa!")
            ganancia_total_dia = sum(r['ganancia_neta_franja'] for r in resultado_live)
            st.metric("Ganancia Neta del Día (Estrategia Progresiva)", f"${ganancia_total_dia:,.2f}", delta=f"{ganancia_total_dia:,.2f}")
            
            st.write("Detalle financiero por franja:")
            df_detalle = pd.DataFrame(resultado_live)
            st.dataframe(df_detalle[['franja', 'numero_real', 'ubicacion_acierto', 'financials', 'ganancia_neta_franja']], use_container_width=True)

elif seccion == "📜 Historial de Sorteos":
    st.header("📜 Historial de Sorteos Cargado")
    st.caption("Estos son los datos crudos leídos desde `historical_draws.json`.")
    df_display_historial = historial_df.rename(columns={'fecha': 'Draw Date'})
    st.dataframe(df_display_historial.sort_values(by='Draw Date', ascending=False), use_container_width=True)