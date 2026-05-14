import numpy as np

def get_detailed_profile(score, knowledge):
    """
    MATRIZ DE IDONEIDAD DE 10 NIVELES (JP Morgan Style)
    Cruza el Score Multivariable con el Nivel de Competencia (Knowledge).
    """
    
    # Definición de la Torta según el Nivel de Riesgo (1-10)
    # Cada nivel añade o quita volatilidad de forma realista
    
    if score <= 10:
        name = "Nivel 1: Preservación Ultrasensiva"
        weights = {"Depósitos a Plazo/Cash": 0.80, "Bonos Gubernamentales": 0.20}
    elif score <= 20:
        name = "Nivel 2: Conservador Defensivo"
        weights = {"Bonos": 0.60, "Efectivo": 0.20, "Oro": 0.15, "ETFs Indexados": 0.05}
    elif score <= 30:
        name = "Nivel 3: Crecimiento con Protección"
        weights = {"Bonos": 0.50, "ETFs Diversificados": 0.25, "Oro": 0.15, "Real Estate": 0.10}
    elif score <= 40:
        name = "Nivel 4: Moderado Estable"
        weights = {"ETFs Indexados": 0.40, "Bonos": 0.30, "Real Estate": 0.20, "Oro": 0.10}
    elif score <= 50:
        name = "Nivel 5: Equilibrado Estratégico"
        weights = {"ETFs Sectoriales": 0.35, "ETFs Indexados": 0.25, "Real Estate": 0.20, "Bonos": 0.15, "Metales": 0.05}
    elif score <= 60:
        name = "Nivel 6: Crecimiento Dinámico"
        weights = {"Acciones Individuales": 0.25, "ETFs Growth": 0.35, "Real Estate": 0.15, "Cripto": 0.10, "Bonos": 0.10, "Metales": 0.05}
    elif score <= 70:
        name = "Nivel 7: Agresivo Selectivo"
        weights = {"Acciones Individuales": 0.40, "ETFs Growth": 0.25, "Cripto": 0.15, "Real Estate": 0.10, "Emergentes": 0.10}
    elif score <= 80:
        name = "Nivel 8: Máximo Crecimiento Alpha"
        weights = {"Acciones Individuales": 0.50, "Cripto": 0.20, "Sectores High-Beta": 0.15, "Emergentes": 0.10, "Real Estate": 0.05}
    elif score <= 90:
        name = "Nivel 9: Especulativo Avanzado"
        weights = {"Acciones Individuales": 0.55, "Cripto": 0.25, "Derivados/Opciones": 0.10, "Startups/VC": 0.10}
    else:
        name = "Nivel 10: Especulación de Cobertura Total"
        weights = {"Cripto": 0.40, "Acciones Individuales": 0.40, "Venture Capital": 0.20}

    # REGLA DE SEGURIDAD BANCARIA: Si el conocimiento es bajo (0-4),
    # el sistema "bloquea" instrumentos complejos y los pasa a ETFs seguros.
    final_weights = weights.copy()
    if knowledge <= 4:
        blocked_assets = ["Acciones Individuales", "Cripto", "Derivados/Opciones", "Startups/VC", "Venture Capital"]
        redistribute_val = 0
        for asset in blocked_assets:
            if asset in final_weights:
                redistribute_val += final_weights.pop(asset)
        
        if redistribute_val > 0:
            final_weights["ETFs (Protección IA)"] = final_weights.get("ETFs (Protección IA)", 0) + redistribute_val
            
    return {"name": name, "weights": final_weights}

def calculate_complex_score(d):
    """Algoritmo de 4 dimensiones para obtener un score de 1 a 100"""
    s = 0
    # 1. Capacidad de Riesgo (Situación Financiera - 40%)
    s += (d['ahorro'] * 0.5)
    if d['estabilidad'] == "Alta": s += 10
    if d['deuda'] == "Ninguna": s += 10
    if d['emergencia'] == "Sí": s += 10 # Tener fondo de emergencia sube capacidad
    
    # 2. Horizonte (Tiempo - 30%)
    s += (d['horizonte'] * 2.5)
    
    # 3. Psicología (Tolerancia - 30%)
    s += (d['conocimiento'] * 3) # A más conocimiento, más tolerancia estructural
    reac_map = {"Vender todo": 0, "Dudar/Mantener": 10, "Comprar más": 20}
    s += reac_map[d['reaccion']]
    
    # 4. Ajuste por Edad
    if d['edad'] > 60: s *= 0.7 # Defensivo por edad
    
    return np.clip(s, 1, 100)
