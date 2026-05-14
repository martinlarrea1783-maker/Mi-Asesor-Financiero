import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from financial_engine import *

st.set_page_config(page_title="JP Morgan Style Advisor", layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
    .main { background-color: #0b0d10; color: #e0e0e0; }
    .stButton>button { background-color: #1a3a5a; color: white; border: 1px solid #d4af37; font-weight: bold; }
    .stTextInput>div>div>input { background-color: #1c1f26; color: white; }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Wealth Management Strategy Terminal")
st.caption("Quantitative Asset Allocation Engine | Powered by Yahoo Finance")

with st.sidebar:
    st.header("🏢 Investment Mandate")
    capital = st.number_input("Capital Liquidity (USD)", value=100000, step=10000)
    st.subheader("Asset Universe")
    assets = st.multiselect("Asset Classes", ["Acciones EEUU", "Acciones Intl", "Bonos", "Oro", "Real Estate", "Cripto"], 
                            default=["Acciones EEUU", "Bonos", "Oro"])
    custom = st.text_input("Direct Equity/ETFs (e.g. AAPL, MSFT, VOO)", "")
    st.info("The engine uses Mean-Variance Optimization (Markowitz) to find the efficient frontier.")

st.header("📋 Investor Suitability Profile")
c1, c2 = st.columns(2)
with c1:
    goal = st.selectbox("Primary Investment Goal", ["Capital Preservation", "Moderate Growth", "Aggressive Appreciation", "Speculative Alpha"])
    horizon = st.slider("Time Horizon (Years)", 1, 30, 10)
with c2:
    reaction = st.select_slider("Reaction to -20% Drawdown", options=["Panic/Sell", "Anxiety/Hold", "Rational/Rebalance", "Opportunistic/Buy"])
    knowledge = st.slider("Financial Literacy", 1, 10, 5)

if st.button("RUN QUANTITATIVE ANALYSIS"):
    # Score logic
    goal_map = {"Capital Preservation": 10, "Moderate Growth": 30, "Aggressive Appreciation": 60, "Speculative Alpha": 90}
    reac_map = {"Panic/Sell": 0, "Anxiety/Hold": 25, "Rational/Rebalance": 50, "Opportunistic/Buy": 100}
    score = (goal_map[goal] * 0.4) + (reac_map[reaction] * 0.3) + (horizon * 2) + (knowledge * 1)
    score = np.clip(score, 1, 100)
    
    profile = get_risk_profile(score)
    tickers = get_selected_tickers(assets, custom)
    
    with st.spinner("Executing Mathematical Optimization..."):
        t_list, weights, rets = optimize_portfolio(tickers, score)
        
    st.subheader(f"Strategy: {profile['name']}")
    st.write(profile['desc'])

    tab1, tab2, tab3 = st.tabs(["Asset Allocation", "Performance Projection", "Risk Analysis"])
    
    with tab1:
        col_pie, col_table = st.columns([1.5, 1])
        with col_pie:
            fig_pie = px.pie(names=t_list, values=weights, hole=0.5, color_discrete_sequence=px.colors.sequential.Blues_r)
            fig_pie.update_layout(template="plotly_dark", title="Optimal Target Weights")
            st.plotly_chart(fig_pie, use_container_width=True)
        with col_table:
            st.table(pd.DataFrame({"Ticker": t_list, "Weight": [f"{w*100:.2f}%" for w in weights]}))

    with tab2:
        st.write("### 10-Year Monte Carlo Wealth Path")
        paths = monte_carlo(weights, rets, capital)
        fig_mc = go.Figure()
        for i in range(15):
            fig_mc.add_trace(go.Scatter(y=paths[:, i], mode='lines', line=dict(width=1), opacity=0.3, showlegend=False))
        fig_mc.add_trace(go.Scatter(y=np.median(paths, axis=1), mode='lines', line=dict(color='#d4af37', width=4), name="Median Expectation"))
        fig_mc.update_layout(template="plotly_dark", xaxis_title="Trading Days", yaxis_title="Portfolio Value (USD)")
        st.plotly_chart(fig_mc, use_container_width=True)
        
    with tab3:
        st.write("### Portfolio Metrics")
        p_ret = np.sum(rets.mean() * weights) * 252
        p_vol = np.sqrt(np.dot(weights.T, np.dot(rets.cov() * 252, weights)))
        sharpe = p_ret / p_vol
        
        m1, m2, m3 = st.columns(3)
        m1.metric("Expected Annual Return", f"{p_ret*100:.2f}%")
        m2.metric("Annualized Volatility", f"{p_vol*100:.2f}%")
        m3.metric("Sharpe Ratio", f"{sharpe:.2f}")
