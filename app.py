
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from financial_engine import *

st.set_page_config(page_title="QuantAdvisor Pro", layout="wide")

st.title("🤖 QuantAdvisor: Asesoría Financiera Inteligente")
st.markdown("---")

with st.sidebar:
    st.header("⚙️ Configuración")
    markets = st.multiselect("Mercados", ["EEUU", "Internacional"], default=["EEUU"])
    assets = st.multiselect("Activos", ["Renta Variable", "Renta Fija", "Oro", "Real Estate", "Cripto"], default=["Renta Variable", "Renta Fija"])
    custom = st.text_input("Acciones adicionales (tickers ej: MSFT, KO)", "")
    custom_list = custom.split(",") if custom else []
    
    st.markdown("---")
    investment = st.number_input("Inversión Inicial ($)", value=10000)

st.header("1. Test de Perfil de Riesgo")
col1, col2 = st.columns(2)
with col1:
    q1 = st.slider("¿Qué harías si tu inversión cae 20% en un mes?", 1, 5, 3, help="1: Vender todo, 5: Comprar más")
    q2 = st.slider("Horizonte de inversión (años)", 1, 5, 3, help="1: <2 años, 5: >10 años")
with col2:
    q3 = st.slider("Conocimiento financiero", 1, 5, 3, help="1: Nulo, 5: Experto")
    q4 = st.slider("Importancia de la seguridad vs retorno", 1, 5, 3, help="1: Seguridad, 5: Retorno")

if st.button("🚀 Calcular Portafolio Optimizado"):
    score = calculate_risk_score([q1, q2, q3, q4])
    profile = get_risk_profile(score)
    
    st.subheader(f"Tu Perfil: {profile['emoji']} {profile['name']}")
    st.info(profile['desc'])
    
    tickers = get_selected_tickers(markets, assets, custom_list)
    with st.spinner("Descargando datos y optimizando..."):
        data = download_price_data(tickers)
        returns = data.pct_change().dropna()
        weights = optimize_portfolio(returns, score)
        
    col_a, col_b = st.columns([1, 1])
    
    with col_a:
        st.write("### Asignación Sugerida")
        alloc_df = pd.DataFrame({'Activo': tickers, 'Peso (%)': (weights * 100).round(2)})
        fig = px.pie(alloc_df, values='Peso (%)', names='Activo', hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
        st.plotly_chart(fig)
        
    with col_b:
        st.write("### Desempeño Histórico")
        portfolio_val = (returns @ weights).add(1).cumprod() * investment
        st.line_chart(portfolio_val)
