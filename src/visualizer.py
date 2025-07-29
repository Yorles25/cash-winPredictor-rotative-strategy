import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def exportar_csv(resultados, ruta="outputs/summary_report.csv"):
    df = pd.DataFrame(resultados)
    df.to_csv(ruta, index=False)
    print(f"📁 Resultados guardados en {ruta}")

def grafico_ganancia_diaria(resultados):
    df = pd.DataFrame(resultados)
    plt.figure(figsize=(12, 6))
    sns.lineplot(x="fecha", y="ganancia", data=df, marker="o")
    plt.xticks(rotation=45)
    plt.title("📈 Ganancia Diaria")
    plt.tight_layout()
    plt.show()

def heatmap_aciertos(resultados):
    df = pd.DataFrame(resultados)
    df["aciertos"] = df["aciertos"].apply(len)
    plt.figure(figsize=(10, 1))
    sns.heatmap([df["aciertos"].tolist()], cmap="Blues", annot=True, cbar=False)
    plt.title("🔍 Heatmap de Aciertos")
    plt.yticks([])
    plt.xticks(rotation=90)
    plt.tight_layout()
    plt.show()
