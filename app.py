import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from financial_engine import *

st.set_page_config(page_title="JPMC Wealth Terminal", layout="wide")

# Estilo Institucional
st.markdown("""
<style>
    .main { background-color: #001e38; color: white; }
    .stButton>button { background-color: #9d8553; color: white; border-radius: 0px; font-weight: bold; width: 100%; height: 3.5em; }
    h1, h2, h3 { color: #9d8553; }
    .card { background-color: #002b4d; padding: 20px; border-left: 5px solid #9d8553; }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ J.P. MORGAN CHASE PRIVATE CLIENT")
st.caption("Strategic Investment Advisory Protocol | Quantitative Analysis")

nombre = st.text_input("IDENTIFICACIÓN DEL TITULAR:")

if nombre:
    st.header(f"Expediente de Inversión: {nombre}")
    
    with st.expander("📝 CUESTIONARIO DE PERFILAMIENTO E IDONEIDAD", expanded=True):
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Datos Financieros")
            edad = st.number_input("Edad:", 18, 95, 25)
            horizonte = st.slider("Horizonte de Inversión (Años):", 1, 40, 15)
            ahorro = st.slider("% Ahorro Mensual del Ingreso:", 0, 100, 20)
            estabilidad = st.radio("Estabilidad de Ingresos:", ["Baja", "Media", "Alta"], index=2)
            
        with c2:
            st.subheader("🧠 Psicología y Conocimiento")
            conocimiento = st.select_slider("Conocimiento Financiero:", options=range(0, 11))
            reaccion = st.selectbox("Si su inversión cae 20%, ¿qué hace?", ["Vender todo", "Dudar", "Comprar más"])
            obj = st.selectbox("Objetivo Principal:", ["Preservar", "Crecer", "Especular"])

    if st.button("GENERAR ESTRATEGIA PATRIMONIAL"):
        data = {'edad': edad, 'horizonte': horizonte, 'ahorro': ahorro, 'estabilidad': estabilidad, 'reaccion': reaccion}
        score = calculate_score(data)
        profile = get_detailed_profile(score, conocimiento)
        
        st.markdown("---")
        st.markdown(f"<div class='card'><h3>RESULTADO: {profile['name']}</h3><p>Score de Riesgo: {int(score)}/100</p></div>", unsafe_allow_html=True)
        
        col_res1, col_res2 = st.columns([1.5, 1])
        with col_res1:
            df = pd.DataFrame(list(profile['weights'].items()), columns=['Activo', 'Peso'])
            fig = px.pie(df, values='Peso', names='Activo', hole=0.5, color_discrete_sequence=['#9d8553', '#004a99', '#0070e0', '#306896'])
            st.plotly_chart(fig, use_container_width=True)
            
        with col_res2:
            st.write("### Desglose de Inversión")
            for k, v in profile['weights'].items():
                st.write(f"**{k}:** {v*100:.1f}%")
                st.progress(v)

        # Reporte
        reporte = f"JPMC WEALTH REPORT - {nombre.upper()}\nPerfil: {profile['name']}\n\nDistribución:\n"
        for k, v in profile['weights'].items(): reporte += f"- {k}: {v*100:.1f}%\n"
        st.download_button("📥 DESCARGAR GUÍA ESTRATÉGICA", data=reporte, file_name=f"Estrategia_{nombre}.txt")
