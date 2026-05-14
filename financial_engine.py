
import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

RISK_PROFILES = {
    (1, 20):   {"name": "Muy Conservador", "color": "#4FC3F7", "emoji": "🛡️", "desc": "Prioridad en preservación de capital."},
    (21, 40):  {"name": "Conservador",     "color": "#81C784", "emoji": "🌱", "desc": "Crecimiento modesto con baja volatilidad."},
    (41, 60):  {"name": "Moderado",        "color": "#FFD54F", "emoji": "⚖️", "desc": "Equilibrio 60/40 entre acciones y bonos."},
    (61, 80):  {"name": "Decidido",        "color": "#FF8A65", "emoji": "🚀", "desc": "Enfoque en crecimiento a largo plazo."},
    (81, 100): {"name": "Agresivo",        "color": "#EF5350", "emoji": "🔥", "desc": "Maximización de retorno, alta volatilidad."}
}

ETF_INFO = {
    "VTI": "Acciones EEUU", "VXUS": "Acciones Internacionales", "BND": "Bonos",
    "GLD": "Oro", "VNQ": "Real Estate", "BTC-USD": "Cripto",
    "AAPL": "Apple", "MSFT": "Microsoft", "KO": "Coca-Cola"
}

def calculate_risk_score(responses):
    return int(np.clip(np.mean(responses) * 20, 1, 100))

def get_risk_profile(score):
    for (low, high), profile in RISK_PROFILES.items():
        if low <= score <= high: return profile
    return RISK_PROFILES[(41, 60)]

def get_selected_tickers(markets, assets, custom_tickers=[]):
    selected = []
    if "Renta Variable" in assets:
        if "EEUU" in markets: selected.extend(["VTI", "AAPL"])
        if "Internacional" in markets: selected.append("VXUS")
    if "Renta Fija" in assets: selected.append("BND")
    if "Oro" in assets: selected.append("GLD")
    if "Real Estate" in assets: selected.append("VNQ")
    if "Cripto" in assets: selected.append("BTC-USD")
    if custom_tickers: selected.extend([t.strip().upper() for t in custom_tickers if t.strip()])
    return list(set(selected)) if selected else ["VTI", "BND"]

def download_price_data(tickers, years=5):
    end = datetime.now()
    start = end - timedelta(days=years*365)
    data = yf.download(tickers, start=start, end=end)['Close']
    return data.dropna()

def optimize_portfolio(returns_df, risk_score):
    num_assets = len(returns_df.columns)
    avg_returns = returns_df.mean() * 252
    cov_matrix = returns_df.cov() * 252
    risk_aversion = (100 - risk_score) / 10.0 + 0.1
    def objective(weights):
        p_ret = np.sum(avg_returns * weights)
        p_vol = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights)))
        return -(p_ret - risk_aversion * p_vol**2)
    constraints = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
    bounds = tuple((0.01, 0.5) for _ in range(num_assets))
    res = minimize(objective, [1./num_assets]*num_assets, method='SLSQP', bounds=bounds, constraints=constraints)
    return res.x if res.success else np.array([1./num_assets]*num_assets)
