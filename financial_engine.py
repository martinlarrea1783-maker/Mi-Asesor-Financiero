import numpy as np

def get_detailed_profile(score, knowledge):
    # Definición de 10 niveles de agresividad reales
    # Si score es bajo, la cartera es defensiva. Si es alto, es ofensiva.
    
    levels = {
        1: {"name": "Preservación Estricta", "weights": {"Bonos": 0.80, "Metales": 0.20}},
        2: {"name": "Conservador Defensivo", "weights": {"Bonos": 0.60, "Metales": 0.20, "ETFs Indexados": 0.20}},
        3: {"name": "Conservador Moderado", "weights": {"Bonos": 0.50, "ETFs Indexados": 0.30, "Metales": 0.15, "Real Estate": 0.05}},
        4: {"name": "Moderado Estable", "weights": {"ETFs Indexados": 0.40, "Bonos": 0.30, "Real Estate": 0.20, "Metales": 0.10}},
        5: {"name": "Moderado Crecimiento", "weights": {"ETFs Indexados": 0.35, "Real Estate": 0.25, "Bonos": 0.20, "Acciones Indiv.": 0.15, "Metales": 0.05}},
        6: {"name": "Crecimiento Estratégico", "weights": {"Acciones Indiv.": 0.30, "ETFs Indexados": 0.30, "Real Estate": 0.20, "Cripto": 0.10, "Metales": 0.10}},
        7: {"name": "Crecimiento Dinámico", "weights": {"Acciones Indiv.": 0.40, "ETFs Indexados": 0.20, "Cripto": 0.15, "Real Estate": 0.15, "Metales": 0.10}},
        8: {"name": "Agresivo Alpha", "weights": {"Acciones Indiv.": 0.50, "Cripto": 0.20, "ETFs Indexados": 0.15, "Real Estate": 0.10, "Metales": 0.05}},
        9: {"name": "Especulativo", "weights": {"Acciones Indiv.": 0.55, "Cripto": 0.30, "Real Estate": 0.10, "Especulativos": 0.05}},
        10: {"name": "Especulación Máxima", "weights": {"Cripto": 0.50, "Acciones Indiv.": 0.40, "Especulativos": 0.10}}
    }
    
    # Seleccionar nivel (1-10) basado en score 1-100
    idx = int(np.clip(round(score / 10), 1, 10))
    profile = levels[idx]
    
    # FILTRO DE PROTECCIÓN: Si no sabe nada (conocimiento 0-3), bloqueamos Cripto y Acciones Individuales
    if knowledge <= 3:
        w = profile['weights']
        to_move = 0
        for asset in ["Cripto", "Acciones Indiv.", "Especulativos"]:
            if asset in w:
                to_move += w.pop(asset)
        w["ETFs (Protección IA)"] = w.get("ETFs (Protección IA)", 0) + to_move
        profile['weights'] = w
        
    return profile

def calculate_score(d):
    s = 0
    # Lógica de puntos:
    # Horizonte (25%)
    s += (d['horizonte'] * 2.5)
    # Capacidad Financiera (40%)
    s += (d['ahorro'] * 0.5)
    if d['estabilidad'] == "Alta": s += 15
    # Psicología (35%)
    reac_map = {"Vender todo": 0, "Dudar": 15, "Comprar más": 35}
    s += reac_map[d['reaccion']]
    
    # Penalización por Edad
    if d['edad'] > 55: s *= 0.8
    
    return np.clip(s, 1, 100)
