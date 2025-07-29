# 📊 Cash WinPredictor - Estrategia Rotativa

Este proyecto es una herramienta de análisis y simulación para estrategias de lotería basadas en la rotación sistemática de grupos de números. Permite a los usuarios definir sus propios grupos, configurar ciclos de rotación y realizar backtesting contra datos históricos para evaluar la rentabilidad financiera de cada estrategia.

## ✨ Características Principales

*   **🧠 Estrategia Flexible:** Define tus propios grupos de números y secuencias de rotación en un simple archivo de configuración (`data/strategy_configuration.json`).
*   **⚙️ Motor de Simulación:** Genera automáticamente la jugada correspondiente para cualquier fecha basándose en la estrategia de rotación activa.
*   **📈 Backtesting Financiero:** Evalúa las jugadas generadas contra un historial de sorteos reales, calculando aciertos, costos, premios y la **ganancia neta** de cada día.
*   **🖥️ Interfaz Interactiva:** Utiliza Streamlit para presentar los resultados en una aplicación web fácil de usar, con métricas clave y tablas detalladas.
*   **🔴 Módulo en Vivo:** Permite evaluar la jugada recomendada para el día actual contra los resultados de un sorteo introducido manualmente.

## 🗂️ Estructura del Proyecto

```
.
├── data/
│   ├── historical_draws.json   # Historial de resultados (formato: {"fecha": [nums]})
│   └── strategy_configuration.json # Configuración de la estrategia
├── src/
│   ├── generator.py            # Genera la jugada del día
│   ├── evaluator.py            # Evalúa la jugada y calcula la ganancia
│   ├── reporter.py             # Guarda los reportes en CSV
│   └── utils.py                # Funciones de ayuda (ej: cargar JSON)
├── outputs/
│   └── backtesting_report.csv  # Reporte generado por main.py
├── .venv/                      # Entorno virtual de Python
├── app.py                      # Interfaz web con Streamlit (modo principal)
├── main.py                     # Ejecución en consola para generar reportes
├── requirements.txt            # Lista de dependencias del proyecto
└── README.md                   # Esta documentación
```

## 🚀 Cómo Empezar

### Prerrequisitos
- Python 3.8 o superior
- Git

### 1. Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/cash-winPredictor-rotative-strategy.git
cd cash-winPredictor-rotative-strategy
```

### 2. Crear y Activar el Entorno Virtual
```bash
# Crear el entorno (solo la primera vez)
python -m venv .venv

# Activar el entorno (CADA VEZ que trabajes en el proyecto)
# En Windows (PowerShell):
.\.venv\Scripts\activate
# En macOS/Linux:
source .venv/bin/activate
```
_Verás `(.venv)` al inicio de la línea de tu terminal si está activado._

### 3. Instalar las Dependencias
Con el entorno virtual activado, instala las librerías necesarias:
```bash
pip install -r requirements.txt
```

### 4. Configurar la Estrategia
Antes de ejecutar, personaliza tu estrategia:
1.  **`data/strategy_configuration.json`**: Define tus `grupos` de números y la secuencia de `rotacion`. Ajusta los valores de `costo_por_numero` y `premio_por_acierto`.
2.  **`data/historical_draws.json`**: Añade los resultados de sorteos pasados en el formato `{"YYYY-MM-DD": [num1, num2, ...]}`.

### 5. Ejecutar la Aplicación

Tienes dos modos de ejecución:

#### Modo Interactivo (Recomendado)
Para lanzar la interfaz web, ejecuta:
```bash
streamlit run app.py
```
Se abrirá una nueva pestaña en tu navegador con la aplicación.

#### Modo Consola (Para generar reportes CSV)
Para ejecutar el backtesting sin interfaz y generar un archivo `backtesting_report.csv`:
```bash
python main.py
```

## 🔧 Personalización

La principal fortaleza de este proyecto es su flexibilidad. Para probar una nueva estrategia:

1.  **Modifica la rotación:** Abre `data/strategy_configuration.json` y cambia el orden o la composición de los grupos en la lista `"rotacion"`.
2.  **Guarda el archivo.**
3.  **Refresca la página** de la aplicación en tu navegador (o ejecuta `streamlit run app.py` de nuevo). Los cálculos de backtesting se actualizarán al instante con la nueva estrategia, permitiéndote comparar su efectividad.

---
_Este proyecto fue desarrollado como una herramienta de análisis y simulación. El juego debe ser una actividad recreativa y responsable._