import numpy as np

def calculate_score(data):
    """
    Calcula el puntaje de perfil de riesgo (1-100).
    data: dict con 'edad', 'horizonte', 'ahorro_mensual', 'estabilidad', 'reaccion_crisis'
    """
    # Ponderaciones de los factores (ajustables)
    w_horizonte = 0.35
    w_estabilidad = 0.20
    w_crisis = 0.30
    w_ahorro = 0.15
    
    # Normalización de variables a escala 1-100
    score = (data['horizonte'] * w_horizonte + 
             data['estabilidad'] * w_estabilidad + 
             data['reaccion_crisis'] * w_crisis + 
             (min(data['ahorro_mensual'] / 1000, 1) * 100) * w_ahorro)
    
    # Penalización por edad (Riesgo decreciente post-55)
    if data['edad'] > 55:
        penalizacion = (data['edad'] - 55) * 2
        score = max(1, score - penalizacion)
        
    return min(100, score)

def get_detailed_profile(score, knowledge):
    """
    Mapea el score a 10 niveles y aplica filtros de idoneidad.
    """
    niveles = [
        "Preservación Ultrasensiva", "Conservador Ingreso", "Conservador Moderado",
        "Balanceado Defensivo", "Balanceado Crecimiento", "Crecimiento Estratégico",
        "Crecimiento Agresivo", "Especulación Moderada", "Especulación Activa", "Especulación Máxima"
    ]
    
    # Determinar índice del nivel (0-9)
    idx = int(min(score // 10, 9))
    perfil_nombre = niveles[idx]
    
    # Matriz base de distribución (ETFs, Acciones, Bonos, Metales, Cripto, Inmobiliario)
    # Estos pesos escalan según el riesgo (idx)
    base_weights = np.array([
        [0.20, 0.00, 0.60, 0.15, 0.00, 0.05], # Nivel 0
        [0.30, 0.05, 0.45, 0.10, 0.00, 0.10], # Nivel 1
        [0.40, 0.10, 0.30, 0.05, 0.00, 0.15], # Nivel 2
        [0.45, 0.15, 0.20, 0.05, 0.02, 0.13], # Nivel 3
        [0.50, 0.20, 0.15, 0.03, 0.05, 0.07], # Nivel 4
        [0.45, 0.25, 0.10, 0.02, 0.08, 0.10], # Nivel 5
        [0.40, 0.30, 0.05, 0.00, 0.15, 0.10], # Nivel 6
        [0.35, 0.35, 0.00, 0.00, 0.20, 0.10], # Nivel 7
        [0.25, 0.45, 0.00, 0.00, 0.25, 0.05], # Nivel 8
        [0.10, 0.50, 0.00, 0.00, 0.40, 0.00], # Nivel 9
    ])
    
    weights = base_weights[idx].copy()
    labels = ["ETFs Indexados", "Acciones Individuales", "Bonos", "Metales", "Cripto", "Sector Inmobiliario"]
    
    # Filtro de Idoneidad
    if knowledge <= 3:
        # Identificar índices de activos complejos
        idx_acciones = 1
        idx_cripto = 4
        
        reubicacion = weights[idx_acciones] + weights[idx_cripto]
        weights[idx_acciones] = 0.0
        weights[idx_cripto] = 0.0
        
        # Mover a "ETFs de Protección" (en este caso, reemplazamos la etiqueta de ETFs Indexados)
        labels[0] = "ETFs de Protección"
        weights[0] += reubicacion
        
    return perfil_nombre, dict(zip(labels, weights))
