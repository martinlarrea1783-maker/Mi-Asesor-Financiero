import streamlit as st
import plotly.express as px
from datetime import datetime
import financial_engine as engine

# Configuración de Marca JPMC
st.set_page_config(page_title="JPMC Wealth Advisor", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #001e38; color: white; }
    .stMetric { background-color: #002a4d; padding: 15px; border-radius: 10px; border-left: 5px solid #9d8553; }
    h1, h2, h3 { color: #9d8553 !important; }
    </style>
    """, unsafe_allow_html=True)

st.title("🏦 Private Banking Terminal | Portfolio Strategy")

# Inicio de Identidad
nombre = st.text_input("Introduzca el nombre del titular de la cuenta:", "Inversionista")
st.subheader(f"Bienvenido, {nombre}")

with st.expander("📝 Cuestionario de Perfilamiento Profundo", expanded=True):
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write("**Datos Financieros**")
        edad = st.number_input("Edad", 18, 100, 30)
        ingresos = st.number_input("Ingresos Anuales (USD)", 0, 1000000, 50000)
        ahorro_mensual = st.number_input("Capacidad de Ahorro Mensual (USD)", 0, 50000, 1000)
        
    with col2:
        st.write("**Perfil Psicológico**")
        horizonte = st.slider("Horizonte de Inversión (Años)", 1, 40, 10)
        crisis = st.select_slider("Reacción ante caída del 20%", options=[1, 2, 3, 4, 5], value=3, 
                                 help="1: Pánico/Venta, 5: Comprar más")
        estabilidad = st.slider("Estabilidad Laboral (1-10)", 1, 10, 7)
        
    with col3:
        st.write("**Conocimiento Técnico**")
        knowledge = st.select_slider("Nivel de Conocimiento Financiero", options=list(range(11)), value=5)

if st.button("Generar Estrategia de Inversión"):
    data = {
        'edad': edad, 'horizonte': horizonte * 2.5, # Escalamiento para scoring
        'ahorro_mensual': ahorro_mensual, 
        'estabilidad': estabilidad * 10, 
        'reaccion_crisis': crisis * 20
    }
    
    score = engine.calculate_score(data)
    perfil, pesos = engine.get_detailed_profile(score, knowledge)
    
    st.divider()
    
    # Resultados
    c_res1, c_res2 = st.columns([1, 1])
    
    with c_res1:
        st.metric("Puntaje de Riesgo", f"{int(score)}/100")
        st.subheader(f"Perfil Asignado: {perfil}")
        
        # Gráfico
        fig = px.pie(values=list(pesos.values()), names=list(pesos.keys()), 
                     color_discrete_sequence=px.colors.sequential.Aggrnyl)
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_color="white")
        st.plotly_chart(fig)
        
    with c_res2:
        st.write("### Desglose de Inversión Mensual")
        for activo, peso in pesos.items():
            monto = ahorro_mensual * peso
            if peso > 0:
                st.write(f"**{activo}:** ${monto:,.2f} ({peso*100:.1f}%)")
        
        # Generar Reporte TXT
        reporte_content = f"""
        GUÍA ESTRATÉGICA DE INVERSIÓN - JPMC TERMINAL
        Fecha: {datetime.now().strftime('%Y-%m-%d')}
        Titular: {nombre}
        Perfil: {perfil} (Score: {int(score)})
        -------------------------------------------
        DISTRIBUCIÓN RECOMENDADA:
        """
        for k, v in pesos.items():
            if v > 0: reporte_content += f"\n- {k}: {v*100}%"
            
        st.download_button("Descargar Guía Estratégica", reporte_content, file_name="Estrategia_Inversion.txt")
