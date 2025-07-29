import datetime
from src.generator import generate_play_for_day
from src.evaluator import evaluate_jugada

def jugar_en_vivo(config, resultado_actual):
    dia_index = datetime.date.today().day - 1  # Ajuste mensual
    jugada = generate_play_for_day(dia_index, config)
    evaluacion = evaluate_jugada(jugada, resultado_actual, config)

    print("🟢 Evaluación Real:")
    for k, v in evaluacion.items():
        print(f"{k}: {v}")

    return evaluacion
