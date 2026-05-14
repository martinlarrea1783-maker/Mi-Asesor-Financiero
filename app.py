import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from financial_engine import *

st.set_page_config(page_title="Institutional Wealth Advisor", layout="wide")

# Estética de Terminal Financiera
st.markdown("""
<style>
    .main { background-color: #0b0d10; color: #ffffff; }
    .stNumberInput input { background-color: #1c1f26; color: white; border: 1px solid #30363d; }
    .stButton>button { background-color: #1a3a5a; color: white; border: 1px solid #d4af37; border-radius: 5px; width: 100%; font-weight: bold; }
    .stMetric { background-color: #161b22; border: 1px solid #30363d; padding: 10px; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

st.title("🏛️ Wealth Strategy & Management Terminal")
st.caption("Quantitative Advisory Engine v4.0 | Asset Allocation Intelligence")
st.markdown("---")

# Registro e Identificación
user_name = st.text_input("Nombre del Inversionista:", placeholder="Ej. Martín Larrea")

if user_name:
    st.header(f"Expediente Digital: {user_name}")
    
    # Cuestionario de Suitability
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.subheader("👤 Perfil Demográfico")
            edad = st.number_input("Edad:", 18, 95, 25)
            obj = st.selectbox("Objetivo Principal:", ["Libertad Financiera", "Retiro Anticipado", "Protección de Patrimonio", "Educación/Hijos"])
            horizonte = st.slider("Horizonte de Inversión (Años):", 1, 40, 10)

        with col2:
            st.subheader("💰 Salud Financiera")
            ingresos = st.number_input("Ingresos Mensuales (USD):", value=2000)
            ahorro = st.slider("% Ahorro Mensual sobre Ingresos:", 0, 100, 20)
            estabilidad = st.radio("Estabilidad de Ingresos:", ["Baja", "Media", "Alta"], index=2)
            deuda = st.radio("Carga de Deuda Actual:", ["Ninguna", "Moderada", "Alta"], index=0)

        with col3:
            st.subheader("🧠 Psicología del Riesgo")
            tolerancia = st.select_slider("Tolerancia a la Volatilidad:", options=["Baja", "Media", "Alta"], value="Media")
            reaccion = st.selectbox("Si el mercado cae 25% en un mes:", ["Vendería por seguridad", "Mantendría la posición", "Aumentaría mi inversión"])

    if st.button("GENERAR DIAGNÓSTICO Y ESTRATEGIA"):
        # Preparación de datos para el motor
        data_input = {
            'edad': edad, 'horizonte': horizonte, 'ahorro_perc': ahorro,
            'estabilidad': estabilidad, 'deudas': deuda, 'tolerancia': tolerancia
        }
        
        score = calculate_professional_score(data_input)
        profile = get_detailed_profile(score)
        
        st.markdown("---")
        st.header(f"Análisis Estratégico para {user_name}")
        st.info(f"**Perfil Asignado:** {profile['name']} | **Score de Riesgo:** {int(score)}/100")
        st.write(profile['desc'])

        # Visualización de la Torta de Inversión
        c_res1, c_res2 = st.columns([1.2, 1])
        
        with c_res1:
            df_plot = pd.DataFrame(list(profile['weights'].items()), columns=['Área de Inversión', 'Peso'])
            fig = px.pie(df_plot, values='Peso', names='Área de Inversión', hole=0.6,
                         color_discrete_sequence=px.colors.sequential.Blues_r,
                         title=f"Distribución Patrimonial Sugerida")
            fig.update_layout(template="plotly_dark", title_x=0.2)
            st.plotly_chart(fig, use_container_width=True)
            
        with c_res2:
            st.write("### Desglose por Clase de Activo")
            monto_ahorro = ingresos * (ahorro / 100)
            for asset, weight in profile['weights'].items():
                monto_mensual = monto_ahorro * weight
                st.write(f"**{asset}:** {weight*100:.0f}%")
                st.caption(f"Inversión mensual recomendada: ${monto_mensual:,.2f}")
                st.progress(weight)

        # Generación de la Guía Descargable
        st.markdown("---")
        fecha_actual = datetime.now().strftime('%d/%m/%Y')
        report_txt = f"""GUÍA DE ESTRATEGIA PATRIMONIAL PERSONALIZADA
-----------------------------------------------------
PREPARADO PARA: {user_name.upper()}
FECHA DE EMISIÓN: {fecha_actual}
ASENSOR: QuantAdvisor AI Terminal
-----------------------------------------------------

1. DIAGNÓSTICO DEL PERFIL
- Edad: {edad} años
- Objetivo Declarado: {obj}
- Perfil de Riesgo: {profile['name']}
- Capacidad de Ahorro: {ahorro}% de los ingresos mensuales.

2. HOJA DE RUTA ESTRATÉGICA (ASSET ALLOCATION)
La inteligencia artificial ha determinado que su portafolio óptimo 
debe diversificarse en las siguientes áreas:

"""
        for a, w in profile['weights'].items():
            report_txt += f"- {a}: {w*100:.0f}%\n"
            
        report_txt += f"""
3. RECOMENDACIONES DE IMPLEMENTACIÓN
- Inversión Mensual Sugerida: ${monto_ahorro:,.2f}
- Rebalanceo: Se recomienda revisar estos pesos cada 12 meses.
- Fondo de Emergencia: Antes de iniciar, asegure tener 3 a 6 meses de gastos en efectivo.

--- 
Documento generado con fines educativos basado en análisis de mercado moderno.
"""
        st.download_button(
            label="📥 DESCARGAR GUÍA DE INVERSIÓN (TXT/PDF)",
            data=report_txt,
            file_name=f"Guia_Inversion_{user_name.replace(' ', '_')}.txt",
            mime="text/plain"
        )
else:
    st.warning("Por favor, introduzca su nombre para iniciar el proceso de asesoría.")
