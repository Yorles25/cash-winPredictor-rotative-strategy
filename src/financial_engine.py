# src/financial_engine.py

class FinancialEngine:
    def __init__(self, franjas, grupos_activos, config):
        self.franjas = franjas
        self.columnas = ['P', 'S', 'C'] # Principal, Secundaria, Cobertura
        self.config = config
        self.grupos_activos = grupos_activos
        self.reset_stakes()

    def reset_stakes(self):
        """Inicializa o resetea todos los contadores de apuesta a 1."""
        self.stakes = {}
        for franja in self.franjas:
            self.stakes[franja] = {col: 1 for col in self.columnas}

    def get_current_stakes(self, franja):
        """Devuelve el estado actual de las apuestas para una franja."""
        return self.stakes.get(franja, {col: 1 for col in self.columnas})

    def calculate_franja_finance(self, franja, ranking_predicho, numero_real):
        """Calcula el rendimiento financiero de una franja y actualiza las apuestas."""
        current_stakes = self.get_current_stakes(franja)
        costo_por_numero = self.config.get('costo_por_numero', 1)
        premio_multiplier = 7 # Premio 7x

        # 1. Determinar el grupo real y la ubicación del acierto
        grupo_real = None
        for g, numeros in self.grupos_activos.items():
            if numero_real in numeros:
                grupo_real = g
                break
        
        ubicacion_acierto = "Fallo"
        if grupo_real == ranking_predicho[0]: ubicacion_acierto = "Columna 1"
        elif len(ranking_predicho) > 1 and grupo_real == ranking_predicho[1]: ubicacion_acierto = "Columna 2"
        elif len(ranking_predicho) > 2 and grupo_real == ranking_predicho[2]: ubicacion_acierto = "Columna 3"

        # 2. Calcular rendimiento para cada sistema (P, S, C)
        financial_results = {}
        next_stakes = current_stakes.copy()
        total_ganancia_franja = 0

        for i, col in enumerate(self.columnas):
            grupo_apostado = ranking_predicho[i] if len(ranking_predicho) > i else None
            if grupo_apostado is None: continue

            apuesta = current_stakes[col]
            numeros_jugados = self.grupos_activos.get(grupo_apostado, [])
            costo = len(numeros_jugados) * apuesta
            
            acerto = (ubicacion_acierto == f"Columna {i+1}")
            premio = (costo / len(numeros_jugados) * premio_multiplier) if acerto else 0
            ganancia_neta = premio - costo
            total_ganancia_franja += ganancia_neta

            financial_results[col] = {
                'apuesta': apuesta, 'costo': costo, 
                'premio': premio, 'ganancia_neta': ganancia_neta
            }

            # 3. Actualizar la apuesta para la próxima vez
            if acerto:
                next_stakes[col] = 1 # Resetear a 1
            else:
                next_stakes[col] += 1 # Aumentar en 1
        
        self.stakes[franja] = next_stakes # Guardar el nuevo estado de las apuestas

        return {
            'ubicacion_acierto': ubicacion_acierto,
            'grupo_real': grupo_real,
            'financials': financial_results,
            'total_ganancia_franja': total_ganancia_franja
        }