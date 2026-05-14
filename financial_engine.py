import numpy as np

def get_detailed_profile(score):
    """Mapea el score a una categoría institucional con pesos macro."""
    if score <= 25:
        return {
            "name": "Conservador (Wealth Preservation)", 
            "weights": {"Renta Fija (Bonos)": 0.60, "Metales Preciosos (Oro/Plata)": 0.20, "Efectivo/Money Market": 0.15, "Acciones Defensivas": 0.05},
            "desc": "Prioridad absoluta en proteger el capital. Ideal para horizontes cortos o alta aversión al riesgo."
        }
    elif score <= 50:
        return {
            "name": "Moderado (Balanced Growth)", 
            "weights": {"Acciones (S&P 500/Global)": 0.40, "Renta Fija (Bonos)": 0.35, "Bienes Raíces (REITs)": 0.15, "Metales Preciosos": 0.10},
            "desc": "Equilibrio entre crecimiento y protección. Adecuado para metas a mediano plazo."
        }
    elif score <= 75:
        return {
            "name": "Crecimiento (Strategic Alpha)", 
            "weights": {"Acciones (Crecimiento/Tech)": 0.50, "Acciones Internacionales": 0.20, "Bienes Raíces (REITs)": 0.15, "Criptoactivos": 0.10, "Metales Preciosos": 0.05},
            "desc": "Busca superar la inflación con una volatilidad aceptable. Enfoque en acumulación."
        }
    else:
        return {
            "name": "Agresivo (High Appreciation)", 
            "weights": {"Acciones Crecimiento/Tech": 0.55, "Criptoactivos": 0.25, "Mercados Emergentes": 0.10, "Venture Capital/Startups": 0.10},
            "desc": "Máxima exposición al riesgo para maximizar el retorno compuesto. Solo para horizontes largos."
        }

def calculate_professional_score(data):
    """Algoritmo de scoring multivariable."""
    score = 0
    # 1. Factor Edad (Inversamente proporcional al riesgo)
    score += (80 - data['edad']) * 0.35
    
    # 2. Situación Financiera (Capacidad de Ahorro y Estabilidad)
    score += (data['ahorro_perc'] * 0.6)
    if data['estabilidad'] == "Alta": score += 15
    if data['deudas'] == "Ninguna": score += 10
    
    # 3. Horizonte Temporal
    score += (data['horizonte'] * 2.5)
    
    # 4. Tolerancia Psicológica
    tol_map = {"Baja": -10, "Media": 10, "Alta": 25}
    score += tol_map[data['tolerancia']]
    
    return np.clip(score, 5, 100)
