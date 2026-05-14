import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from financial_engine import *

st.set_page_config(page_title="JPMC Private Banking", layout="wide")

# Estética JP Morgan Chase Premium
st.markdown("""
<style>
    .main { background-color: #001221; color: #ffffff; }
    .stSelectbox, .stNumberInput, .stSlider { color: white; }
    .stButton>button { background-color: #a3895d; color: #001221; border-radius: 0px; font-weight: bold; border: none; transition: 0.3s; }
    .stButton>button:hover { background-color: #ffffff; color: #001221; }
    h1, h2, h3 { color: #a3895d; font-family: 'Times New Roman', serif; }
    .status-box { background-color: #00223d; padding: 25px; border-top: 4px solid #a3895d; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ J.P. MORGAN CHASE PRIVATE CLIENT")
st.caption("Strategic Asset Allocation Engine | Global Wealth Management")

user_name = st.text_input("IDENTIFICACIÓN DEL TITULAR:", placeholder="Ej. Martín Larrea")

if user_name:
    st.markdown(f"### Análisis de Portafolio: {user_name}")
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👤 Perfil Personal")
            edad = st.number_input("Edad:", 18, 95, 25)
            horizonte = st.slider("Horizonte de Inversión (Años):", 1, 40, 15)
            conocimiento = st.select_slider("Competencia Financiera:", options=range(0, 11), help="0: Principiante, 10: Profesional")

        with col2:
            st.subheader("💰 Balance Financiero")
            ahorro = st.slider("% Ahorro de Ingresos Mensuales:", 0, 100, 20)
            estabilidad = st.radio("Estabilidad de Flujo:", ["Baja", "Media", "Alta"], index=2)
            deuda = st.selectbox("Nivel de Endeudamiento:", ["Ninguna", "Moderada", "Alta"])
            emergencia = st.checkbox("¿Tiene un fondo de emergencia (3-6 meses)?")

        with col3:
            st.subheader("🧠 Perfil Psicológico")
            reaccion = st.selectbox("Reacción ante caída de mercado (-20%):", ["Vender todo", "Dudar/Mantener", "Comprar más"])
            obj = st.selectbox("Prioridad:", ["Seguridad", "Crecimiento", "Especulación"])

    if st.button("CALCULAR ESTRATEGIA DE INVERSIÓN"):
        data = {
            'edad': edad, 'horizonte': horizonte, 'ahorro': ahorro,
            'estabilidad': estabilidad, 'deuda': deuda, 'emergencia': emergencia,
            'conocimiento': conocimiento, 'reaccion': reaccion
        }
        
        score = calculate_complex_score(data)
        profile = get_detailed_profile(score, conocimiento)
        
        st.markdown("---")
        st.markdown(f"<div class='status-box'><h3>RECOMENDACIÓN ESTRATÉGICA: {profile['name']}</h3>"
                    f"<p>Basado en un Score de Idoneidad de <strong>{int(score)}/100</strong>.</p></div>", unsafe_allow_html=True)
        
        res_col1, res_col2 = st.columns([1.5, 1])
        
        with res_col1:
            df = pd.DataFrame(list(profile['weights'].items()), columns=['Activo', 'Peso'])
            fig = px.pie(df, values='Peso', names='Activo', hole=0.6,
                         color_discrete_sequence=['#a3895d', '#004a99', '#0070e0', '#306896', '#5b89ad', '#86aac4'])
            fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', font_color="white", showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
            
        with res_col2:
            st.write("### Desglose de Asset Allocation")
            for asset, weight in profile['weights'].items():
                st.write(f"**{asset}:** {weight*100:.1f}%")
                st.progress(weight)

        # REPORTE DE DESCARGA
        report = f"""
        J.P. MORGAN PRIVATE CLIENT - INVESTMENT STRATEGY
        -----------------------------------------------
        TITULAR: {user_name.upper()}
        FECHA: {datetime.now().strftime('%Y-%m-%d')}
        SCORE DE IDONEIDAD: {int(score)}/100
        CATEGORÍA: {profile['name']}
        
        1. ANÁLISIS DE RIESGO
        Con un horizonte de {horizonte} años y conocimiento nivel {conocimiento}/10, 
        se ha determinado que su perfil óptimo es {profile['name']}.
        
        2. DISTRIBUCIÓN DE ACTIVOS RECOMENDADA
        """
        for a, w in profile['weights'].items():
            report += f"\n- {a}: {w*100:.1f}%"
            
        report += "\n\n3. NOTAS DE CUMPLIMIENTO\n- Los activos complejos se han ajustado según su nivel de competencia.\n- Se recomienda rebalancear el portafolio cada vez que un activo se desvíe un 5% de su peso objetivo."

        st.download_button("📥 DESCARGAR GUÍA DE INVERSIÓN PDF", data=report, file_name=f"Estrategia_JPMC_{user_name}.txt")
