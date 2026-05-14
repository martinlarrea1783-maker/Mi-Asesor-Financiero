"""
financial_engine.py
====================
Motor cuantitativo del Asesor Financiero Automatizado.
Separa toda la lógica financiera de la interfaz de usuario.
"""

import numpy as np
import pandas as pd
import yfinance as yf
from scipy.optimize import minimize
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')


# ─────────────────────────────────────────────
#  CONSTANTES Y CONFIGURACIÓN
# ─────────────────────────────────────────────

RISK_PROFILES = {
    (1, 20):   {"name": "Muy Conservador", "color": "#4FC3F7", "emoji": "🛡️",
                "desc": "Preservación del capital como prioridad absoluta. Mínima exposición a volatilidad."},
    (21, 40):  {"name": "Conservador",     "color": "#81C784", "emoji": "🌱",
                "desc": "Crecimiento moderado con protección ante caídas severas del mercado."},
    (41, 60):  {"name": "Moderado",        "color": "#FFD54F", "emoji": "⚖️",
                "desc": "Equilibrio entre crecimiento y estabilidad. Horizonte de medio plazo."},
    (61, 80):  {"name": "Decidido",        "color": "#FF8A65", "emoji": "🚀",
                "desc": "Mayor exposición a renta variable buscando rendimientos superiores."},
    (81, 100): {"name": "Agresivo",        "color": "#EF5350", "emoji": "🔥",
                "desc": "Maximización del retorno a largo plazo. Alta tolerancia a la volatilidad."},
}

ETF_INFO = {
    "VTI":     {"name": "Vanguard Total Stock Market", "category": "RV EEUU",       "expense": 0.03},
    "VXUS":    {"name": "Vanguard Total Intl Stock",   "category": "RV Internacional","expense": 0.07},
    "VGK":     {"name": "Vanguard FTSE Europe",        "category": "RV Europa",      "expense": 0.09},
    "VWO":     {"name": "Vanguard FTSE Emerging",      "category": "RV Emergentes",  "expense": 0.10},
    "BND":     {"name": "Vanguard Total Bond Market",  "category": "Renta Fija",     "expense": 0.03},
    "GLD":     {"name": "SPDR Gold Shares",            "category": "Oro",            "expense": 0.40},
    "BTC-USD": {"name": "Bitcoin USD",                 "category": "Cripto",         "expense": 0.00},
    "SPY":     {"name": "S&P 500 ETF (Benchmark)",     "category": "Benchmark",      "expense": 0.09},
}

# Pesos base por perfil de riesgo (orden: VTI, VXUS, VGK, VWO, BND, GLD, BTC-USD)
BASE_WEIGHTS = {
    "Muy Conservador": {"BND": 0.60, "GLD": 0.20, "VTI": 0.10, "VXUS": 0.05, "VGK": 0.03, "VWO": 0.02, "BTC-USD": 0.00},
    "Conservador":     {"BND": 0.40, "GLD": 0.15, "VTI": 0.25, "VXUS": 0.10, "VGK": 0.05, "VWO": 0.05, "BTC-USD": 0.00},
    "Moderado":        {"BND": 0.25, "GLD": 0.10, "VTI": 0.35, "VXUS": 0.15, "VGK": 0.08, "VWO": 0.05, "BTC-USD": 0.02},
    "Decidido":        {"BND": 0.10, "GLD": 0.08, "VTI": 0.40, "VXUS": 0.20, "VGK": 0.10, "VWO": 0.07, "BTC-USD": 0.05},
    "Agresivo":        {"BND": 0.05, "GLD": 0.05, "VTI": 0.35, "VXUS": 0.20, "VGK": 0.10, "VWO": 0.15, "BTC-USD": 0.10},
}


# ─────────────────────────────────────────────
#  SCORING PSICOMÉTRICO MiFID II
# ─────────────────────────────────────────────

def calculate_risk_score(answers: dict) -> tuple[int, dict]:
    """
    Calcula el Risk Score (1-100) a partir de las respuestas del cuestionario.
    Retorna (score, breakdown) con desglose por dimensión.
    """
    # Dimensión 1: Capacidad de Riesgo (35 puntos máx)
    cap_score = 0
    age_map = {"<30": 10, "30-45": 8, "45-55": 5, "55-65": 3, ">65": 1}
    cap_score += age_map.get(answers.get("age", "<30"), 5)

    income_map = {"<30k": 2, "30-60k": 4, "60-100k": 7, "100-200k": 9, ">200k": 10}
    cap_score += income_map.get(answers.get("income", "<30k"), 4)

    job_map = {"Desempleado": 1, "Autónomo": 4, "Empleado": 6, "Funcionario": 8, "Empresario": 7}
    cap_score += job_map.get(answers.get("job", "Empleado"), 5)

    savings_map = {"<3 meses": 1, "3-6 meses": 3, "6-12 meses": 5, ">12 meses": 7}
    cap_score += savings_map.get(answers.get("savings", "3-6 meses"), 3)

    debt_map = {"Alto (>50% ingresos)": 1, "Medio (25-50%)": 3, "Bajo (<25%)": 5, "Sin deudas": 8}
    cap_score += debt_map.get(answers.get("debt", "Bajo (<25%)"), 4)

    # Dimensión 2: Tolerancia al Riesgo (35 puntos máx)
    tol_score = 0
    reaction_map = {"Vendo todo": 2, "Vendo parte": 5, "No hago nada": 8, "Compro más": 10}
    tol_score += reaction_map.get(answers.get("reaction_drop", "No hago nada"), 7) * 1.2

    horizon_map = {"<2 años": 2, "2-5 años": 5, "5-10 años": 8, ">10 años": 10}
    tol_score += horizon_map.get(answers.get("horizon", "5-10 años"), 7)

    loss_map = {"0% (ninguna pérdida)": 1, "Hasta -10%": 4, "Hasta -25%": 7, "Hasta -50%": 9, "Más del -50%": 10}
    tol_score += loss_map.get(answers.get("max_loss", "Hasta -25%"), 6)

    # Dimensión 3: Conocimiento Financiero (30 puntos máx)
    know_score = 0
    exp_map = {"Ninguna": 2, "Básica (depósitos/fondos)": 5, "Media (acciones/ETFs)": 8, "Avanzada (derivados/opciones)": 10}
    know_score += exp_map.get(answers.get("experience", "Básica (depósitos/fondos)"), 4)

    products_map = {"1": 3, "2": 5, "3": 8, "4+": 10}
    know_score += products_map.get(str(answers.get("products_known", "2")), 5)

    freq_map = {"Nunca": 2, "Ocasionalmente": 4, "Regularmente": 7, "Diariamente": 10}
    know_score += freq_map.get(answers.get("follow_markets", "Regularmente"), 6)

    # Score final normalizado a 100
    raw_total = cap_score + tol_score + know_score
    max_possible = 35 + 35 + 30
    final_score = int(round((raw_total / max_possible) * 100))
    final_score = max(1, min(100, final_score))

    breakdown = {
        "Capacidad de Riesgo": round((cap_score / 35) * 100),
        "Tolerancia al Riesgo": round((tol_score / 35) * 100),
        "Conocimiento Financiero": round((know_score / 30) * 100),
    }

    return final_score, breakdown


def get_risk_profile(score: int) -> dict:
    """Retorna el perfil de riesgo según el score."""
    for (lo, hi), profile in RISK_PROFILES.items():
        if lo <= score <= hi:
            return profile
    return RISK_PROFILES[(81, 100)]


# ─────────────────────────────────────────────
#  DESCARGA Y PROCESAMIENTO DE DATOS
# ─────────────────────────────────────────────

def download_price_data(tickers: list, years: int = 5) -> pd.DataFrame:
    """
    Descarga datos históricos de precios ajustados.
    Maneja errores de conexión y días sin mercado.
    """
    end_date = datetime.today()
    start_date = end_date - timedelta(days=years * 365)

    prices = {}
    failed = []

    for ticker in tickers:
        try:
            data = yf.download(ticker, start=start_date, end=end_date,
                               progress=False, auto_adjust=True)
            if data.empty:
                failed.append(ticker)
                continue

            close = data['Close']
            if isinstance(close, pd.DataFrame):
                close = close.iloc[:, 0]

            prices[ticker] = close

        except Exception as e:
            failed.append(ticker)

    if not prices:
        raise ValueError(f"No se pudieron descargar datos. Tickers fallidos: {failed}")

    df = pd.DataFrame(prices).dropna(how='all').ffill().bfill()

    if failed:
        print(f"Advertencia: No se descargaron datos para: {failed}")

    return df


# ─────────────────────────────────────────────
#  OPTIMIZACIÓN MEDIA-VARIANZA (Markowitz)
# ─────────────────────────────────────────────

def optimize_portfolio(prices: pd.DataFrame, risk_score: int,
                       selected_tickers: list) -> dict:
    """
    Optimización de Media-Varianza con restricciones de perfil de riesgo.
    Maximiza Sharpe Ratio con target de volatilidad según score.
    """
    returns = np.log(prices[selected_tickers] / prices[selected_tickers].shift(1)).dropna()
    n = len(selected_tickers)

    if n == 0:
        return {}
    if n == 1:
        return {selected_tickers[0]: 1.0}

    mean_returns = returns.mean() * 252
    cov_matrix = returns.cov() * 252
    rf_rate = 0.05  # Risk-free rate aproximado

    # Target de volatilidad según perfil (normalizado de score 1-100)
    target_vol = 0.04 + (risk_score / 100) * 0.28  # 4% a 32% anual

    def neg_sharpe(weights):
        w = np.array(weights)
        port_return = np.dot(w, mean_returns)
        port_vol = np.sqrt(np.dot(w.T, np.dot(cov_matrix, w)))
        if port_vol < 1e-8:
            return 0
        return -(port_return - rf_rate) / port_vol

    def portfolio_vol(weights):
        return np.sqrt(np.dot(weights, np.dot(cov_matrix, weights)))

    constraints = [
        {'type': 'eq', 'fun': lambda w: np.sum(w) - 1},
    ]

    # Límites por activo según perfil
    if risk_score <= 40:
        bounds = [(0.0, 0.60) for _ in range(n)]
    elif risk_score <= 70:
        bounds = [(0.0, 0.50) for _ in range(n)]
    else:
        bounds = [(0.0, 0.60) for _ in range(n)]

    # Bitcoin limitado según perfil
    btc_idx = [i for i, t in enumerate(selected_tickers) if t == "BTC-USD"]
    if btc_idx:
        idx = btc_idx[0]
        max_btc = min(0.02 + (risk_score / 100) * 0.13, 0.15)
        bounds[idx] = (0.0, max_btc)

    x0 = np.array([1.0 / n] * n)

    try:
        result = minimize(neg_sharpe, x0, method='SLSQP',
                          bounds=bounds, constraints=constraints,
                          options={'maxiter': 1000, 'ftol': 1e-9})
        weights = result.x
    except Exception:
        weights = np.array([1.0 / n] * n)

    # Limpiar pesos pequeños
    weights[weights < 0.01] = 0
    if weights.sum() > 0:
        weights /= weights.sum()

    return {t: round(float(w), 4) for t, w in zip(selected_tickers, weights)}


# ─────────────────────────────────────────────
#  MÉTRICAS DEL PORTAFOLIO
# ─────────────────────────────────────────────

def calculate_portfolio_metrics(prices: pd.DataFrame, weights: dict) -> dict:
    """
    Calcula métricas cuantitativas exactas del portafolio.
    """
    tickers = list(weights.keys())
    w = np.array([weights[t] for t in tickers])

    log_returns = np.log(prices[tickers] / prices[tickers].shift(1)).dropna()
    port_returns = log_returns.dot(w)

    # Retorno anualizado (CAGR)
    total_return = np.exp(port_returns.sum()) - 1
    years = len(port_returns) / 252
    cagr = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0

    # Volatilidad anualizada
    vol_annual = port_returns.std() * np.sqrt(252)

    # Máximo Drawdown
    cum_returns = (1 + port_returns).cumprod()
    rolling_max = cum_returns.cummax()
    drawdown = (cum_returns - rolling_max) / rolling_max
    max_drawdown = drawdown.min()

    # Sharpe Ratio
    rf_daily = 0.05 / 252
    sharpe = ((port_returns.mean() - rf_daily) / port_returns.std()) * np.sqrt(252)

    # Sortino Ratio
    downside = port_returns[port_returns < 0].std() * np.sqrt(252)
    sortino = (cagr - 0.05) / downside if downside > 0 else 0

    # Calmar Ratio
    calmar = cagr / abs(max_drawdown) if max_drawdown != 0 else 0

    return {
        "cagr": round(cagr * 100, 2),
        "volatility": round(vol_annual * 100, 2),
        "max_drawdown": round(max_drawdown * 100, 2),
        "sharpe": round(sharpe, 3),
        "sortino": round(sortino, 3),
        "calmar": round(calmar, 3),
        "total_return": round(total_return * 100, 2),
        "years": round(years, 1),
    }


def calculate_portfolio_history(prices: pd.DataFrame, weights: dict,
                                initial_investment: float = 10000) -> pd.Series:
    """Retorna la serie temporal de valor del portafolio."""
    tickers = list(weights.keys())
    w = np.array([weights[t] for t in tickers])
    log_returns = np.log(prices[tickers] / prices[tickers].shift(1)).dropna()
    port_returns = log_returns.dot(w)
    cum_value = initial_investment * (1 + port_returns).cumprod()
    return cum_value


# ─────────────────────────────────────────────
#  SIMULACIÓN DE MONTE CARLO
# ─────────────────────────────────────────────

def monte_carlo_simulation(prices: pd.DataFrame, weights: dict,
                            initial_investment: float = 10000,
                            n_simulations: int = 1000,
                            n_years: int = 10) -> dict:
    """
    Simulación de Monte Carlo con log-retornos y correlaciones reales.
    Genera 1,000 trayectorias a N años.
    """
    tickers = list(weights.keys())
    w = np.array([weights[t] for t in tickers])

    log_returns = np.log(prices[tickers] / prices[tickers].shift(1)).dropna()
    port_returns = log_returns.dot(w)

    daily_mean = port_returns.mean()
    daily_std = port_returns.std()
    n_days = n_years * 252

    np.random.seed(42)
    daily_returns_sim = np.random.normal(
        loc=daily_mean,
        scale=daily_std,
        size=(n_days, n_simulations)
    )

    # Trayectorias acumuladas
    cum_returns = np.cumprod(1 + daily_returns_sim, axis=0)
    portfolio_values = initial_investment * cum_returns

    # Fechas simuladas
    start = prices.index[-1]
    dates = pd.bdate_range(start=start, periods=n_days + 1)[1:]

    # Percentiles
    p10 = np.percentile(portfolio_values, 10, axis=1)  # Pesimista
    p25 = np.percentile(portfolio_values, 25, axis=1)
    p50 = np.percentile(portfolio_values, 50, axis=1)  # Esperado
    p75 = np.percentile(portfolio_values, 75, axis=1)
    p90 = np.percentile(portfolio_values, 90, axis=1)  # Optimista

    # Probabilidades
    prob_loss = (portfolio_values[-1] < initial_investment).mean() * 100
    prob_double = (portfolio_values[-1] > initial_investment * 2).mean() * 100

    return {
        "dates": dates,
        "p10": p10, "p25": p25, "p50": p50, "p75": p75, "p90": p90,
        "all_paths": portfolio_values[:, :50],  # Solo 50 trayectorias para plot
        "final_values": portfolio_values[-1],
        "prob_loss": round(prob_loss, 1),
        "prob_double": round(prob_double, 1),
        "median_final": round(np.median(portfolio_values[-1]), 0),
        "p10_final": round(p10[-1], 0),
        "p90_final": round(p90[-1], 0),
    }


# ─────────────────────────────────────────────
#  SELECCIÓN DE TICKERS POR MERCADO/ACTIVO
# ─────────────────────────────────────────────

def get_selected_tickers(markets: list, assets: list) -> list:
    """
    Mapea selecciones de mercado/activo a tickers ETF reales.
    """
    ticker_map = {
        # Por mercado
        ("EEUU", "Renta Variable"):        "VTI",
        ("Internacional", "Renta Variable"): "VXUS",
        ("Europa", "Renta Variable"):      "VGK",
        ("Emergentes", "Renta Variable"):  "VWO",
        # Por activo (independiente de mercado)
        ("all", "Renta Fija"):             "BND",
        ("all", "Oro"):                    "GLD",
        ("all", "Cripto"):                 "BTC-USD",
    }

    selected = []

    # Renta Variable por mercado
    if "Renta Variable" in assets:
        if "EEUU" in markets and "VTI" not in selected:
            selected.append("VTI")
        if "Internacional" in markets and "VXUS" not in selected:
            selected.append("VXUS")
        if "Europa" in markets and "VGK" not in selected:
            selected.append("VGK")
        if "Emergentes" in markets and "VWO" not in selected:
            selected.append("VWO")

    # Activos independientes
    if "Renta Fija" in assets and "BND" not in selected:
        selected.append("BND")
    if "Oro" in assets and "GLD" not in selected:
        selected.append("GLD")
    if "Cripto" in assets and "BTC-USD" not in selected:
        selected.append("BTC-USD")

    # Fallback
    if not selected:
        selected = ["VTI", "BND"]

    return selected
