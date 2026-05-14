import streamlit as st
import pandas as pd
import plotly.express as px
from financial_engine import *

st.set_page_config(page_title="Personal Wealth Advisor", layout="wide")

# CSS para estilo JP Morgan
st.markdown("<style>.main {background-color: #0b0d0f; color: white;}</style>", unsafe_allow_html=True)

st.title("🏛️ Asesor de Estrategia Patrimonial Inteligente")
st.markdown("---")

# Registro del Cliente
col_n1, col_n2 = st.columns(2)
with col_n1:
    user_name = st.text_input("Introduzca su nombre completo:", placeholder="Ej. Martín Larrea")

if user_name:
    st.sidebar.header(f"Expediente: {user_name}")
    st.sidebar.write("Este sistema utiliza modelos de optimización para sugerir la distribución de su capital.")

    st.header("📊 Perfilamiento de Riesgo y Objetivos")
    c1, c2 = st.columns(2)
    with c1:
        age = st.number_input("Edad:", 18, 100, 25)
        tol = st.select_slider("Tolerancia al riesgo psicológico:", options=["Mínima", "Baja", "Media", "Alta", "Máxima"], value="Media")
    with c2:
        horizon = st.slider("Horizonte de inversión (Años):", 1, 40, 10)
        capital = st.number_input("Capital a distribuir (USD):", value=10000)

    # Lógica de Score
    tol_map = {"Mínima": 10, "Baja": 30, "Media": 50, "Alta": 75, "Máxima": 100}
    final_score = (tol_map[tol] * 0.7) + (horizon * 0.3)

    if st.button("GENERAR GUÍA DE INVERSIÓN"):
        weights = generate_strategic_allocation(final_score)
        
        st.subheader(f"Guía Estratégica para {user_name}")
        
        col_res1, col_res2 = st.columns([1.5, 1])
        
        with col_res1:
            df_plot = pd.DataFrame(list(weights.items()), columns=['Clase de Activo', 'Porcentaje'])
            fig = px.pie(df_plot, values='Porcentaje', names='Clase de Activo', hole=0.5, 
                         color_discrete_sequence=px.colors.sequential.Darkmint)
            st.plotly_chart(fig, use_container_width=True)
            
        with col_res2:
            st.write("### Distribución de Capital Sugerida")
            for asset, weight in weights.items():
                monto = capital * weight
                st.metric(asset, f"{weight*100:.0f}%", f"${monto:,.2f}")

        # Sección de Reporte
        st.markdown("---")
        report_text = f"""
        REPORTE DE ESTRATEGIA PATRIMONIAL
        Cliente: {user_name}
        Fecha: {datetime.now().strftime('%d/%m/%Y')}
        
        Basado en su perfil de riesgo ({tol}) y su horizonte de {horizon} años, 
        la Inteligencia Artificial de QuantAdvisor recomienda la siguiente distribución:
        
        """
        for a, w in weights.items():
            report_text += f"- {a}: {w*100:.0f}% (Aproximadamente ${capital*w:,.2f})\n"
            
        st.download_button(
            label="📥 Descargar Guía en PDF/Texto",
            data=report_text,
            file_name=f"Guia_Inversion_{user_name}.txt",
            mime="text/plain"
        )
