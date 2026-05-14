import pandas as pd
import numpy as np
import yfinance as yf
from datetime import datetime

def get_macro_data():
    # Representantes de cada clase de activo para el análisis de mercado
    proxies = {
        "Acciones (Crecimiento)": "QQQ",
        "Acciones (Valor/Dividendos)": "VYM",
        "Renta Fija (Bonos)": "BND",
        "Metales Preciosos (Oro/Plata)": "GLD",
        "Bienes Raíces (REITs)": "VNQ",
        "Criptoactivos": "BTC-USD"
    }
    data = yf.download(list(proxies.values()), period="5y")['Close']
    returns = data.pct_change().mean() * 252
    volatility = data.pct_change().std() * np.sqrt(252)
    
    # Invertimos el mapeo para devolver nombres legibles
    inv_proxies = {v: k for k, v in proxies.items()}
    return {inv_proxies[t]: {"ret": returns[t], "vol": volatility[t]} for t in proxies.values()}

def generate_strategic_allocation(score):
    market_stats = get_macro_data()
    
    # Lógica de IA para pesos basada en Risk Score (1-100)
    # A mayor score, más peso a Cripto y Crecimiento. A menor score, más Bonos y Oro.
    weights = {}
    
    if score <= 30: # Conservador
        weights = {"Renta Fija (Bonos)": 0.50, "Metales Preciosos (Oro/Plata)": 0.20, "Acciones (Valor/Dividendos)": 0.20, "Bienes Raíces (REITs)": 0.10}
    elif score <= 70: # Moderado
        weights = {"Acciones (Crecimiento)": 0.30, "Acciones (Valor/Dividendos)": 0.30, "Renta Fija (Bonos)": 0.20, "Bienes Raíces (REITs)": 0.10, "Metales Preciosos (Oro/Plata)": 0.05, "Criptoactivos": 0.05}
    else: # Agresivo
        weights = {"Acciones (Crecimiento)": 0.50, "Criptoactivos": 0.25, "Bienes Raíces (REITs)": 0.15, "Acciones (Valor/Dividendos)": 0.10}
        
    return weights
