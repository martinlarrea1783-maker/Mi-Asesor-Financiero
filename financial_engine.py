import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from datetime import datetime, timedelta

def get_risk_profile(score):
    if score <= 25: return {"name": "Conservador (Preservación)", "target_vol": 0.05, "desc": "Enfoque en bonos y activos defensivos."}
    if score <= 50: return {"name": "Moderado (Equilibrado)", "target_vol": 0.10, "desc": "Balance 60/40 entre crecimiento y seguridad."}
    if score <= 75: return {"name": "Crecimiento (Decidido)", "target_vol": 0.15, "desc": "Preferencia por renta variable global."}
    return {"name": "Agresivo (Especulativo)", "target_vol": 0.22, "desc": "Maximización de capital a largo plazo."}

def get_selected_tickers(assets, custom):
    mapping = {
        "Acciones EEUU": ["VTI", "VOO", "QQQ"],
        "Acciones Intl": ["VXUS", "VEA", "VWO"],
        "Bonos": ["BND", "AGG", "TLT"],
        "Oro": ["GLD", "IAU"], 
        "Real Estate": ["VNQ", "SCHH"],
        "Cripto": ["BTC-USD", "ETH-USD"]
    }
    tickers = []
    for a in assets:
        if a in mapping: tickers.extend(mapping[a])
    if custom:
        tickers.extend([t.strip().upper() for t in custom.split(",") if t.strip()])
    return list(dict.fromkeys(tickers))

def optimize_portfolio(tickers, risk_score):
    data = yf.download(tickers, period="5y")['Close']
    if isinstance(data, pd.Series): data = data.to_frame()
    data = data.dropna(axis=1, how='all').dropna()
    valid_tickers = data.columns.tolist()
    returns = data.pct_change().dropna()
    
    mu = returns.mean() * 252
    cov = returns.cov() * 252
    n = len(valid_tickers)
    
    risk_aversion = (100 - risk_score) / 10.0 + 0.1

    def objective(w):
        p_ret = np.sum(mu * w)
        p_vol = np.sqrt(np.dot(w.T, np.dot(cov, w)))
        return -(p_ret - risk_aversion * (p_vol**2))

    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.01, 0.45) for _ in range(n))
    
    res = minimize(objective, [1./n]*n, method='SLSQP', bounds=bounds, constraints=constraints)
    return valid_tickers, res.x, returns

def monte_carlo(weights, returns, capital, years=10):
    p_ret = np.sum(returns.mean() * weights) * 252
    p_vol = np.sqrt(np.dot(weights.T, np.dot(returns.cov() * 252, weights)))
    
    sims = 500
    days = years * 252
    dt = 1/252
    
    paths = np.zeros((days, sims))
    paths[0] = capital
    for t in range(1, days):
        shock = np.random.normal(0, 1, sims)
        paths[t] = paths[t-1] * np.exp((p_ret - 0.5 * p_vol**2) * dt + p_vol * np.sqrt(dt) * shock)
    return paths
