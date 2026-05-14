"""
app.py
======
Asesor Financiero Automatizado — Interfaz Streamlit
Motor cuantitativo en financial_engine.py
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from financial_engine import (
    calculate_risk_score, get_risk_profile, get_selected_tickers,
    download_price_data, optimize_portfolio, calculate_portfolio_metrics,
    calculate_portfolio_history, monte_carlo_simulation, ETF_INFO
)

# ─────────────────────────────────────────────
#  CONFIGURACIÓN DE LA PÁGINA
# ─────────────────────────────────────────────

st.set_page_config(
    page_title="QuantAdvisor — Asesor Financiero IA",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
#  ESTILOS PERSONALIZADOS
# ─────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500;600&display=swap');

:root {
    --bg: #0a0e1a;
    --surface: #111827;
    --surface2: #1a2235;
    --border: #1e2d45;
    --accent: #00d4ff;
    --accent2: #7c3aed;
    --accent3: #10b981;
    --text: #e2e8f0;
    --text-muted: #64748b;
    --gold: #f59e0b;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: var(--bg) !important;
    color: var(--text) !important;
}

.stApp {
    background: linear-gradient(135deg, #0a0e1a 0%, #0d1529 50%, #0a0e1a 100%);
}

/* Header Hero */
.hero-header {
    background: linear-gradient(135deg, #0d1529 0%, #1a1040 50%, #0d1529 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 32px 40px;
    margin-bottom: 32px;
    position: relative;
    overflow: hidden;
}
.hero-header::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(0,212,255,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-header::after {
    content: '';
    position: absolute;
    bottom: -50%;
    right: 5%;
    width: 250px;
    height: 250px;
    background: radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%);
    pointer-events: none;
}
.hero-title {
    font-family: 'DM Serif Display', serif;
    font-size: 2.6rem;
    color: var(--text);
    margin: 0 0 8px 0;
    letter-spacing: -0.02em;
}
.hero-title span {
    color: var(--accent);
}
.hero-sub {
    font-size: 1rem;
    color: var(--text-muted);
    font-weight: 300;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}

/* Cards */
.metric-card {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 16px;
}
.metric-card:hover {
    border-color: var(--accent);
    transition: border-color 0.3s ease;
}
.metric-value {
    font-family: 'DM Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    color: var(--accent);
}
.metric-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    margin-top: 4px;
}

/* Score Gauge Container */
.score-display {
    background: linear-gradient(135deg, var(--surface) 0%, var(--surface2) 100%);
    border: 1px solid var(--border);
    border-radius: 16px;
    padding: 28px;
    text-align: center;
}
.score-number {
    font-family: 'DM Serif Display', serif;
    font-size: 5rem;
    line-height: 1;
    background: linear-gradient(135deg, var(--accent) 0%, var(--accent2) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.profile-badge {
    display: inline-block;
    padding: 6px 20px;
    border-radius: 100px;
    font-size: 0.9rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    margin-top: 8px;
}

/* Question cards */
.q-section-title {
    font-family: 'DM Serif Display', serif;
    font-size: 1.1rem;
    color: var(--accent);
    border-bottom: 1px solid var(--border);
    padding-bottom: 8px;
    margin-bottom: 16px;
    margin-top: 8px;
}

/* Tabs override */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surface);
    border-radius: 12px;
    padding: 4px;
    border: 1px solid var(--border);
    gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    border-radius: 8px;
    color: var(--text-muted);
    font-weight: 500;
    padding: 10px 20px;
}
.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--accent2) 0%, #5b21b6 100%) !important;
    color: white !important;
}
.stTabs [data-baseweb="tab-panel"] {
    padding-top: 24px;
}

/* Streamlit elements */
div[data-testid="stRadio"] label {
    color: var(--text) !important;
    font-size: 0.95rem;
}
div[data-testid="stRadio"] [role="radiogroup"] {
    gap: 8px;
}
.stCheckbox label {
    color: var(--text) !important;
}
div[data-testid="stNumberInput"] label {
    color: var(--text) !important;
}
div[data-testid="stSlider"] label {
    color: var(--text) !important;
}

/* Button */
.stButton button {
    background: linear-gradient(135deg, var(--accent2) 0%, #4f46e5 100%);
    color: white;
    border: none;
    border-radius: 10px;
    padding: 14px 40px;
    font-size: 1rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    width: 100%;
    cursor: pointer;
    transition: all 0.3s ease;
}
.stButton button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(124,58,237,0.4);
}

/* Info boxes */
.info-box {
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 12px 0;
    font-size: 0.9rem;
}
.warning-box {
    background: rgba(245, 158, 11, 0.05);
    border: 1px solid rgba(245, 158, 11, 0.2);
    border-radius: 10px;
    padding: 16px 20px;
    margin: 12px 0;
}

/* Table override */
.dataframe {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
}

/* Divider */
hr {
    border-color: var(--border) !important;
    margin: 24px 0 !important;
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  PLOTLY TEMPLATE BASE
# ─────────────────────────────────────────────

PLOTLY_THEME = dict(
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(17,24,39,0.8)',
    font=dict(family='DM Sans, sans-serif', color='#e2e8f0', size=12),
    xaxis=dict(gridcolor='#1e2d45', linecolor='#1e2d45', zerolinecolor='#1e2d45'),
    yaxis=dict(gridcolor='#1e2d45', linecolor='#1e2d45', zerolinecolor='#1e2d45'),
    legend=dict(bgcolor='rgba(17,24,39,0.8)', bordercolor='#1e2d45', borderwidth=1),
    margin=dict(l=20, r=20, t=40, b=20),
)


# ─────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────

st.markdown("""
<div class="hero-header">
    <div class="hero-sub">🤖 MiFID II Compliant · Powered by Markowitz Optimization</div>
    <h1 class="hero-title">Quant<span>Advisor</span></h1>
    <p style="color:#94a3b8; margin:0; font-size:1.05rem;">
        Asesor Financiero Automatizado · Perfil de Riesgo Personalizado · Optimización de Portafolio
    </p>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  ESTADO DE SESIÓN
# ─────────────────────────────────────────────

if 'questionnaire_done' not in st.session_state:
    st.session_state.questionnaire_done = False
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'risk_score' not in st.session_state:
    st.session_state.risk_score = None
if 'portfolio_data' not in st.session_state:
    st.session_state.portfolio_data = None


# ─────────────────────────────────────────────
#  SIDEBAR — CONFIGURACIÓN
# ─────────────────────────────────────────────

with st.sidebar:
    st.markdown("### ⚙️ Parámetros de Simulación")
    initial_investment = st.number_input(
        "Capital Inicial (€/$)", min_value=1000, max_value=10_000_000,
        value=10000, step=1000, format="%d"
    )
    simulation_years = st.slider("Años de Proyección", 3, 30, 10)
    n_simulations = st.select_slider(
        "Simulaciones Monte Carlo", options=[500, 1000, 2000, 5000], value=1000
    )
    data_years = st.slider("Años de Datos Históricos", 3, 10, 5)

    st.markdown("---")
    st.markdown("### 🌍 Exposición por Mercado")
    markets = []
    if st.checkbox("🇺🇸 EEUU", value=True): markets.append("EEUU")
    if st.checkbox("🌐 Internacional", value=True): markets.append("Internacional")
    if st.checkbox("🇪🇺 Europa", value=False): markets.append("Europa")
    if st.checkbox("🌏 Mercados Emergentes", value=False): markets.append("Emergentes")

    st.markdown("### 📦 Clase de Activos")
    assets = []
    if st.checkbox("📈 Renta Variable", value=True): assets.append("Renta Variable")
    if st.checkbox("🏦 Renta Fija", value=True): assets.append("Renta Fija")
    if st.checkbox("🥇 Oro", value=False): assets.append("Oro")
    if st.checkbox("₿ Cripto (Bitcoin)", value=False): assets.append("Cripto")

    if not markets:
        markets = ["EEUU"]
    if not assets:
        assets = ["Renta Variable"]

    st.markdown("---")
    st.markdown('<div style="color:#64748b; font-size:0.75rem; text-align:center;">⚠️ Este software es solo informativo.<br>No constituye asesoramiento financiero regulado.</div>', unsafe_allow_html=True)


# ─────────────────────────────────────────────
#  CUESTIONARIO MiFID II
# ─────────────────────────────────────────────

if not st.session_state.questionnaire_done:
    st.markdown("## 📋 Cuestionario de Perfil de Riesgo")
    st.markdown('<div class="info-box">🔒 <strong>Basado en estándares MiFID II</strong> · Sus respuestas son confidenciales y solo se usan para calcular su perfil de inversión personalizado.</div>', unsafe_allow_html=True)

    with st.form("questionnaire_form"):

        # ── DIMENSIÓN 1: Capacidad de Riesgo ──
        st.markdown('<div class="q-section-title">DIMENSIÓN 1 · Capacidad Financiera</div>', unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            q1 = st.radio(
                "1. ¿Cuál es su rango de edad?",
                ["<30", "30-45", "45-55", "55-65", ">65"],
                index=1, key="age"
            )
        with col2:
            q2 = st.radio(
                "2. ¿Cuáles son sus ingresos anuales netos?",
                ["<30k", "30-60k", "60-100k", "100-200k", ">200k"],
                index=1, key="income"
            )

        col3, col4 = st.columns(2)
        with col3:
            q3 = st.radio(
                "3. ¿Cuál es su situación laboral?",
                ["Desempleado", "Autónomo", "Empleado", "Funcionario", "Empresario"],
                index=2, key="job"
            )
        with col4:
            q4 = st.radio(
                "4. ¿Cuántos meses de gastos tiene ahorrados como fondo de emergencia?",
                ["<3 meses", "3-6 meses", "6-12 meses", ">12 meses"],
                index=1, key="savings"
            )

        q5 = st.radio(
            "5. ¿Cuál es su nivel actual de endeudamiento respecto a sus ingresos?",
            ["Alto (>50% ingresos)", "Medio (25-50%)", "Bajo (<25%)", "Sin deudas"],
            index=2, key="debt", horizontal=True
        )

        st.markdown('<div class="q-section-title">DIMENSIÓN 2 · Tolerancia al Riesgo</div>', unsafe_allow_html=True)

        q6 = st.radio(
            "6. Si su portafolio cae un 20% en un mes, ¿qué haría?",
            ["Vendo todo", "Vendo parte", "No hago nada", "Compro más"],
            index=2, key="reaction_drop", horizontal=True
        )

        col5, col6 = st.columns(2)
        with col5:
            q7 = st.radio(
                "7. ¿Cuál es su horizonte de inversión?",
                ["<2 años", "2-5 años", "5-10 años", ">10 años"],
                index=2, key="horizon"
            )
        with col6:
            q8 = st.radio(
                "8. ¿Qué pérdida máxima toleraría en un año malo?",
                ["0% (ninguna pérdida)", "Hasta -10%", "Hasta -25%", "Hasta -50%", "Más del -50%"],
                index=2, key="max_loss"
            )

        st.markdown('<div class="q-section-title">DIMENSIÓN 3 · Conocimiento Financiero</div>', unsafe_allow_html=True)

        col7, col8 = st.columns(2)
        with col7:
            q9 = st.radio(
                "9. ¿Cuál es su experiencia inversora?",
                ["Ninguna", "Básica (depósitos/fondos)", "Media (acciones/ETFs)", "Avanzada (derivados/opciones)"],
                index=1, key="experience"
            )
        with col8:
            q10 = st.radio(
                "10. ¿Con cuántos tipos de productos financieros ha operado?",
                ["1", "2", "3", "4+"],
                index=1, key="products_known"
            )

        q11 = st.radio(
            "¿Con qué frecuencia sigue los mercados financieros?",
            ["Nunca", "Ocasionalmente", "Regularmente", "Diariamente"],
            index=2, key="follow_markets", horizontal=True
        )

        st.markdown("---")
        submitted = st.form_submit_button("🔍 Calcular Mi Perfil de Riesgo →", use_container_width=True)

    if submitted:
        answers = {
            "age": q1, "income": q2, "job": q3, "savings": q4,
            "debt": q5, "reaction_drop": q6, "horizon": q7,
            "max_loss": q8, "experience": q9, "products_known": q10,
            "follow_markets": q11,
        }
        st.session_state.answers = answers
        score, breakdown = calculate_risk_score(answers)
        st.session_state.risk_score = score
        st.session_state.score_breakdown = breakdown
        st.session_state.questionnaire_done = True
        st.rerun()


# ─────────────────────────────────────────────
#  DASHBOARD PRINCIPAL (tras cuestionario)
# ─────────────────────────────────────────────

if st.session_state.questionnaire_done:

    risk_score = st.session_state.risk_score
    profile = get_risk_profile(risk_score)
    breakdown = st.session_state.get('score_breakdown', {})

    selected_tickers = get_selected_tickers(markets, assets)

    # ── CARGA DE DATOS (con cache) ──
    @st.cache_data(ttl=3600, show_spinner=False)
    def load_data(tickers, years):
        all_tickers = list(set(tickers + ["SPY"]))
        return download_price_data(all_tickers, years)

    with st.spinner("⚡ Descargando datos de mercado y optimizando portafolio..."):
        try:
            prices = load_data(selected_tickers, data_years)

            # Verificar tickers disponibles
            available = [t for t in selected_tickers if t in prices.columns]
            if not available:
                st.error("No se pudieron cargar datos de mercado. Compruebe su conexión.")
                st.stop()

            weights = optimize_portfolio(prices, risk_score, available)
            metrics = calculate_portfolio_metrics(prices, weights)
            port_history = calculate_portfolio_history(prices, weights, initial_investment)

            mc_results = monte_carlo_simulation(
                prices, weights, initial_investment,
                n_simulations=n_simulations,
                n_years=simulation_years
            )

            # SPY benchmark
            spy_history = None
            if "SPY" in prices.columns:
                spy_history = prices["SPY"] / prices["SPY"].iloc[0] * initial_investment

        except Exception as e:
            st.error(f"❌ Error al procesar datos: {str(e)}")
            st.info("Verifica tu conexión a internet e intenta de nuevo.")
            if st.button("🔄 Reintentar"):
                st.cache_data.clear()
                st.rerun()
            st.stop()

    # ── RESET ──
    col_r1, col_r2 = st.columns([5, 1])
    with col_r2:
        if st.button("↩️ Rehacer", use_container_width=True):
            st.session_state.questionnaire_done = False
            st.session_state.portfolio_data = None
            st.cache_data.clear()
            st.rerun()

    # ─────────────────────────────────────────
    #  TABS PRINCIPALES
    # ─────────────────────────────────────────

    tab1, tab2, tab3 = st.tabs([
        "👤  Perfil & Asset Allocation",
        "📈  Backtesting Histórico",
        "🎲  Proyecciones Monte Carlo"
    ])

    # ══════════════════════════════════════════
    #  TAB 1: PERFIL Y ASSET ALLOCATION
    # ══════════════════════════════════════════
    with tab1:

        # Score principal
        col_score, col_breakdown = st.columns([1, 2])

        with col_score:
            st.markdown(f"""
            <div class="score-display">
                <div style="font-size:0.75rem; color:#64748b; text-transform:uppercase; letter-spacing:0.1em; margin-bottom:8px;">Risk Score MiFID II</div>
                <div class="score-number">{risk_score}</div>
                <div>/100</div>
                <div class="profile-badge" style="background:{profile['color']}22; color:{profile['color']}; border:1px solid {profile['color']}44; margin-top:12px;">
                    {profile['emoji']} {profile['name']}
                </div>
                <div style="color:#94a3b8; font-size:0.85rem; margin-top:16px; line-height:1.6;">
                    {profile['desc']}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_breakdown:
            # Radar breakdown de las 3 dimensiones
            cats = list(breakdown.keys())
            vals = list(breakdown.values())
            vals_closed = vals + [vals[0]]
            cats_closed = cats + [cats[0]]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(
                r=vals_closed, theta=cats_closed,
                fill='toself',
                fillcolor='rgba(124,58,237,0.2)',
                line=dict(color='#7c3aed', width=2),
                marker=dict(size=8, color='#7c3aed'),
                name="Tu Perfil"
            ))
            fig_radar.update_layout(
                **PLOTLY_THEME,
                polar=dict(
                    bgcolor='rgba(17,24,39,0.6)',
                    radialaxis=dict(range=[0, 100], gridcolor='#1e2d45',
                                   linecolor='#1e2d45', tickfont=dict(size=10, color='#64748b')),
                    angularaxis=dict(gridcolor='#1e2d45', linecolor='#1e2d45',
                                     tickfont=dict(size=11, color='#e2e8f0'))
                ),
                showlegend=False,
                title=dict(text="Desglose por Dimensión", font=dict(size=14, color='#94a3b8')),
                height=300,
            )
            st.plotly_chart(fig_radar, use_container_width=True)

        st.markdown("---")

        # Métricas clave
        st.markdown("#### 📊 Métricas del Portafolio Optimizado")
        mcol1, mcol2, mcol3, mcol4, mcol5 = st.columns(5)

        def metric_card(label, value, color="#00d4ff", suffix=""):
            return f"""
            <div class="metric-card">
                <div class="metric-value" style="color:{color};">{value}{suffix}</div>
                <div class="metric-label">{label}</div>
            </div>"""

        with mcol1:
            color = "#10b981" if metrics['cagr'] > 0 else "#ef4444"
            st.markdown(metric_card("Retorno Anual (CAGR)", f"{metrics['cagr']:+.1f}", color, "%"), unsafe_allow_html=True)
        with mcol2:
            st.markdown(metric_card("Volatilidad Anual", f"{metrics['volatility']:.1f}", "#f59e0b", "%"), unsafe_allow_html=True)
        with mcol3:
            st.markdown(metric_card("Sharpe Ratio", f"{metrics['sharpe']:.2f}", "#00d4ff"), unsafe_allow_html=True)
        with mcol4:
            st.markdown(metric_card("Máx. Drawdown", f"{metrics['max_drawdown']:.1f}", "#ef5350", "%"), unsafe_allow_html=True)
        with mcol5:
            st.markdown(metric_card("Sortino Ratio", f"{metrics['sortino']:.2f}", "#a78bfa"), unsafe_allow_html=True)

        st.markdown("---")

        # Asset Allocation Pie + Tabla
        col_pie, col_table = st.columns([1.2, 1])

        with col_pie:
            filtered_weights = {k: v for k, v in weights.items() if v > 0.001}
            labels = [f"{t}\n{ETF_INFO.get(t, {}).get('category', t)}" for t in filtered_weights]
            values = list(filtered_weights.values())

            COLORS = ['#00d4ff', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#a78bfa', '#34d399']

            fig_pie = go.Figure(go.Pie(
                labels=labels,
                values=values,
                hole=0.55,
                marker=dict(colors=COLORS[:len(values)],
                            line=dict(color='#0a0e1a', width=3)),
                textfont=dict(size=12, color='white'),
                hovertemplate='<b>%{label}</b><br>Peso: %{percent}<br><extra></extra>'
            ))

            fig_pie.add_annotation(
                text=f"<b>{len(filtered_weights)}</b><br><span style='font-size:10px'>ACTIVOS</span>",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='#e2e8f0')
            )

            pie_theme = {k: v for k, v in PLOTLY_THEME.items() if k != 'legend'}
            fig_pie.update_layout(
                **pie_theme,
                title=dict(text="Asset Allocation Optimizado", font=dict(size=15, color='#94a3b8')),
                showlegend=True,
                legend=dict(orientation='v', x=1, y=0.5,
                            bgcolor='rgba(17,24,39,0.8)', bordercolor='#1e2d45', borderwidth=1),
                height=380,
            )
            st.plotly_chart(fig_pie, use_container_width=True)

        with col_table:
            st.markdown("##### 🗂️ Detalle del Portafolio")
            table_data = []
            for ticker, w in sorted(filtered_weights.items(), key=lambda x: -x[1]):
                info = ETF_INFO.get(ticker, {})
                table_data.append({
                    "Ticker": ticker,
                    "Nombre": info.get('name', ticker),
                    "Categoría": info.get('category', '—'),
                    "Peso (%)": f"{w*100:.1f}%",
                    "TER": f"{info.get('expense', 0):.2f}%",
                })
            df_table = pd.DataFrame(table_data)
            st.dataframe(df_table, hide_index=True, use_container_width=True,
                         column_config={
                             "Ticker": st.column_config.TextColumn(width="small"),
                             "Peso (%)": st.column_config.TextColumn(width="small"),
                             "TER": st.column_config.TextColumn(width="small"),
                         })

            # TER ponderado
            ter_weighted = sum(
                weights.get(t, 0) * ETF_INFO.get(t, {}).get('expense', 0)
                for t in weights
            )
            st.markdown(f"""
            <div class="info-box">
                💡 <strong>TER Ponderado del Portafolio:</strong> {ter_weighted:.3f}% anual<br>
                <span style="color:#64748b; font-size:0.85rem;">Coste total estimado de gestión de los ETFs seleccionados.</span>
            </div>
            """, unsafe_allow_html=True)

    # ══════════════════════════════════════════
    #  TAB 2: BACKTESTING
    # ══════════════════════════════════════════
    with tab2:

        st.markdown("#### 📈 Rendimiento Histórico vs S&P 500 (SPY)")
        st.markdown(f'<div class="info-box">📅 Período analizado: <strong>{data_years} años</strong> · Capital inicial: <strong>${initial_investment:,.0f}</strong> · Datos: <strong>yfinance / Yahoo Finance</strong></div>', unsafe_allow_html=True)

        fig_bt = go.Figure()

        # Portafolio
        fig_bt.add_trace(go.Scatter(
            x=port_history.index, y=port_history.values,
            name=f"Mi Portafolio ({profile['name']})",
            line=dict(color='#7c3aed', width=2.5),
            hovertemplate='<b>Portafolio</b><br>%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
        ))

        # SPY Benchmark
        if spy_history is not None:
            fig_bt.add_trace(go.Scatter(
                x=spy_history.index, y=spy_history.values,
                name="S&P 500 (SPY)",
                line=dict(color='#94a3b8', width=1.5, dash='dash'),
                hovertemplate='<b>S&P 500</b><br>%{x|%b %Y}<br>$%{y:,.0f}<extra></extra>'
            ))

        # Initial investment line
        fig_bt.add_hline(
            y=initial_investment,
            line_dash="dot", line_color="#1e2d45",
            annotation_text="Capital Inicial",
            annotation_font_color="#64748b"
        )

        fig_bt.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Evolución del Capital (Base 100)", font=dict(size=15, color='#94a3b8')),
            xaxis_title="Fecha",
            yaxis_title="Valor ($)",
            hovermode='x unified',
            height=450,
        )
        fig_bt.update_yaxes(tickformat="$,.0f")

        st.plotly_chart(fig_bt, use_container_width=True)

        # Drawdown chart
        port_returns_dd = port_history.pct_change().dropna()
        cum_port = (1 + port_returns_dd).cumprod()
        rolling_max_dd = cum_port.cummax()
        drawdown_series = ((cum_port - rolling_max_dd) / rolling_max_dd) * 100

        fig_dd = go.Figure()
        fig_dd.add_trace(go.Scatter(
            x=drawdown_series.index, y=drawdown_series.values,
            fill='tozeroy',
            fillcolor='rgba(239,68,68,0.15)',
            line=dict(color='#ef4444', width=1.5),
            name="Drawdown",
            hovertemplate='%{x|%b %Y}<br>Drawdown: %{y:.1f}%<extra></extra>'
        ))
        fig_dd.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Drawdown del Portafolio (%)", font=dict(size=14, color='#94a3b8')),
            height=200,
            xaxis_title="",
            yaxis_title="Drawdown (%)",
            showlegend=False,
        )
        st.plotly_chart(fig_dd, use_container_width=True)

        # Comparativa anual de retornos
        st.markdown("##### 📅 Retornos Anuales")
        port_annual = port_history.resample('YE').last().pct_change().dropna() * 100

        colors_bar = ['#10b981' if v >= 0 else '#ef4444' for v in port_annual.values]

        fig_annual = go.Figure()
        fig_annual.add_trace(go.Bar(
            x=[str(d.year) for d in port_annual.index],
            y=port_annual.values,
            marker_color=colors_bar,
            name="Portafolio",
            hovertemplate='%{x}: %{y:.1f}%<extra></extra>'
        ))

        if spy_history is not None:
            spy_annual = spy_history.resample('YE').last().pct_change().dropna() * 100
            fig_annual.add_trace(go.Scatter(
                x=[str(d.year) for d in spy_annual.index],
                y=spy_annual.values,
                mode='markers+lines',
                line=dict(color='#94a3b8', dash='dash'),
                marker=dict(size=8),
                name="S&P 500",
            ))

        fig_annual.update_layout(
            **PLOTLY_THEME,
            title=dict(text="Retorno Anual (%)", font=dict(size=14, color='#94a3b8')),
            height=300, barmode='group',
            yaxis_tickformat=".1f", yaxis_ticksuffix="%"
        )
        fig_annual.add_hline(y=0, line_color='#1e2d45', line_width=1)
        st.plotly_chart(fig_annual, use_container_width=True)

    # ══════════════════════════════════════════
    #  TAB 3: MONTE CARLO
    # ══════════════════════════════════════════
    with tab3:

        st.markdown(f"#### 🎲 Simulación de Monte Carlo — {simulation_years} años · {n_simulations:,} trayectorias")

        col_mc1, col_mc2, col_mc3, col_mc4 = st.columns(4)
        mc_metrics = [
            ("Escenario Pesimista (P10)", f"${mc_results['p10_final']:,.0f}", "#ef5350"),
            ("Escenario Esperado (P50)", f"${mc_results['median_final']:,.0f}", "#00d4ff"),
            ("Escenario Optimista (P90)", f"${mc_results['p90_final']:,.0f}", "#10b981"),
            ("Prob. de Pérdida", f"{mc_results['prob_loss']:.1f}%", "#f59e0b"),
        ]
        for col, (label, val, color) in zip([col_mc1, col_mc2, col_mc3, col_mc4], mc_metrics):
            with col:
                st.markdown(f"""
                <div class="metric-card" style="border-color:{color}44;">
                    <div class="metric-value" style="color:{color}; font-size:1.5rem;">{val}</div>
                    <div class="metric-label">{label}</div>
                </div>""", unsafe_allow_html=True)

        # Gráfico principal Monte Carlo
        dates = mc_results['dates']
        all_dates = pd.concat([pd.Series([prices.index[-1]]), pd.Series(dates)])

        # Gráfico de áreas por percentiles
        fig_mc = go.Figure()

        # Área P10-P90
        fig_mc.add_trace(go.Scatter(
            x=list(dates) + list(reversed(list(dates))),
            y=list(mc_results['p90']) + list(reversed(list(mc_results['p10']))),
            fill='toself',
            fillcolor='rgba(0,212,255,0.06)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Rango P10-P90',
            hoverinfo='skip',
        ))

        # Área P25-P75
        fig_mc.add_trace(go.Scatter(
            x=list(dates) + list(reversed(list(dates))),
            y=list(mc_results['p75']) + list(reversed(list(mc_results['p25']))),
            fill='toself',
            fillcolor='rgba(0,212,255,0.12)',
            line=dict(color='rgba(0,0,0,0)'),
            name='Rango P25-P75',
            hoverinfo='skip',
        ))

        # Líneas de percentiles
        for label, data, color, dash in [
            ("Optimista (P90)", mc_results['p90'], '#10b981', 'dot'),
            ("Esperado (P50)",  mc_results['p50'], '#00d4ff', 'solid'),
            ("Pesimista (P10)", mc_results['p10'], '#ef5350', 'dot'),
        ]:
            fig_mc.add_trace(go.Scatter(
                x=dates, y=data,
                name=label,
                line=dict(color=color, width=2, dash=dash),
                hovertemplate=f'<b>{label}</b><br>%{{x|%b %Y}}<br>${{y:,.0f}}<extra></extra>'
            ))

        # Línea de capital inicial
        fig_mc.add_hline(
            y=initial_investment,
            line_dash="dot", line_color="#1e2d45", line_width=1.5,
            annotation_text=f"Capital Inicial ${initial_investment:,.0f}",
            annotation_font_color="#64748b"
        )

        fig_mc.update_layout(
            **PLOTLY_THEME,
            title=dict(
                text=f"Proyección de {simulation_years} años · {n_simulations:,} simulaciones de Monte Carlo",
                font=dict(size=15, color='#94a3b8')
            ),
            xaxis_title="Año",
            yaxis_title="Valor del Portafolio ($)",
            height=480,
            hovermode='x unified',
        )
        fig_mc.update_yaxes(tickformat="$,.0f")
        st.plotly_chart(fig_mc, use_container_width=True)

        # Distribución del valor final
        col_dist1, col_dist2 = st.columns([1.5, 1])

        with col_dist1:
            final_vals = mc_results['final_values']
            fig_hist = go.Figure()
            fig_hist.add_trace(go.Histogram(
                x=final_vals,
                nbinsx=60,
                marker_color='#7c3aed',
                marker_line_color='#0a0e1a',
                marker_line_width=0.5,
                opacity=0.85,
                name="Distribución Final",
                hovertemplate='$%{x:,.0f}<br>Count: %{y}<extra></extra>'
            ))

            # Marcadores de percentiles
            for pct, val, color, label in [
                (10, mc_results['p10_final'], '#ef5350', 'P10'),
                (50, mc_results['median_final'], '#00d4ff', 'Mediana'),
                (90, mc_results['p90_final'], '#10b981', 'P90'),
            ]:
                fig_hist.add_vline(x=val, line_color=color, line_dash='dash', line_width=1.5,
                                   annotation_text=f"{label}: ${val:,.0f}",
                                   annotation_font_color=color, annotation_font_size=10)

            fig_hist.update_layout(
                **PLOTLY_THEME,
                title=dict(text=f"Distribución del Valor Final (año {simulation_years})",
                           font=dict(size=14, color='#94a3b8')),
                xaxis_title="Valor ($)", yaxis_title="Frecuencia",
                xaxis_tickformat="$,.0f",
                showlegend=False, height=320,
            )
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_dist2:
            st.markdown("##### 📊 Estadísticas de Proyección")
            prob_double = mc_results['prob_double']
            prob_loss = mc_results['prob_loss']

            stats_data = {
                "Métrica": ["Capital Inicial", "Mediana (P50)", "Optimista (P90)", "Pesimista (P10)",
                            "Prob. Pérdida", "Prob. Doblar"],
                "Valor": [
                    f"${initial_investment:,.0f}",
                    f"${mc_results['median_final']:,.0f}",
                    f"${mc_results['p90_final']:,.0f}",
                    f"${mc_results['p10_final']:,.0f}",
                    f"{prob_loss:.1f}%",
                    f"{prob_double:.1f}%",
                ]
            }
            st.dataframe(pd.DataFrame(stats_data), hide_index=True, use_container_width=True)

            # CAGR implícito en escenarios
            def implied_cagr(final, initial, years):
                if initial <= 0 or years <= 0:
                    return 0
                return ((final / initial) ** (1 / years) - 1) * 100

            st.markdown(f"""
            <div class="info-box">
                <strong>CAGR Implícito por Escenario</strong><br>
                🔴 Pesimista: {implied_cagr(mc_results['p10_final'], initial_investment, simulation_years):.1f}% anual<br>
                🔵 Esperado:  {implied_cagr(mc_results['median_final'], initial_investment, simulation_years):.1f}% anual<br>
                🟢 Optimista: {implied_cagr(mc_results['p90_final'], initial_investment, simulation_years):.1f}% anual
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="warning-box">
                ⚠️ <strong>Nota metodológica</strong><br>
                <span style="font-size:0.83rem; color:#94a3b8;">
                Simulación basada en log-retornos históricos de {data_years} años.
                Rendimientos pasados no garantizan resultados futuros.
                Modelo asume distribución normal y no captura eventos extremos (fat tails).
                </span>
            </div>
            """, unsafe_allow_html=True)
