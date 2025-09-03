import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Topografía",
    page_icon="🗺️",
    layout="wide"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #FFFFFF;
    }
    .stMetric {
        border-radius: 10px;
        background-color: #FFFFFF;
        padding: 15px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --- BARRA LATERAL PARA CARGA DE ARCHIVOS ---
with st.sidebar:
    st.image("https://i.imgur.com/8rq4XwB.png", width=100) # Un logo genérico
    st.header("Cargar Archivos CSV")
    st.write("Arrastra y suelta los archivos de cada cuadrante aquí.")
    
    uploaded_q1 = st.file_uploader("Cuadrante 1 (Vías)", type="csv")
    uploaded_q2 = st.file_uploader("Cuadrante 2 (Interferencias)", type="csv")
    uploaded_q3 = st.file_uploader("Cuadrante 3 (Interferencias)", type="csv")
    uploaded_q4 = st.file_uploader("Cuadrante 4 (Vías)", type="csv")


# --- TÍTULO Y ENCABEZADO ---
st.title("🗺️ Dashboard Interactivo de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")
st.markdown("---")

# --- VERIFICACIÓN DE ARCHIVOS CARGADOS ---
if not all([uploaded_q1, uploaded_q2, uploaded_q3, uploaded_q4]):
    st.warning("Por favor, carga los cuatro archivos CSV en la barra lateral para visualizar el dashboard.")
    st.image("https://i.imgur.com/sETiL2C.gif", caption="Ejemplo de cómo cargar los archivos.")
    st.stop()


# --- FUNCIÓN PARA PROCESAR LOS DATOS ---
def process_dataframes(upload_q1, upload_q2, upload_q3, upload_q4):
    """Procesa los archivos CSV cargados y los almacena en el estado de la sesión."""
    if 'data_loaded' not in st.session_state or st.session_state.upload_ids != [id(f) for f in [upload_q1, upload_q2, upload_q3, upload_q4]]:
        
        # --- Procesamiento Cuadrante 1 ---
        df1 = pd.read_csv(upload_q1, skiprows=7)
        df1.columns = ['idx', 'Cuadrante', 'Vial', 'Levantamiento_m', 'Dibujo', 'As_Built']
        df1 = df1[['Vial', 'Levantamiento_m']].dropna(subset=['Vial'])
        df1 = df1[df1['Vial'] != 'TOTAL']
        df1['Levantamiento_m'] = pd.to_numeric(df1['Levantamiento_m'], errors='coerce').fillna(0)
        df1['Cuadrante'] = '1'
        st.session_state['df_q1'] = df1

        # --- Procesamiento Cuadrante 2 ---
        df2 = pd.read_csv(upload_q2, skiprows=8)
        df2.columns = ['Cuadrante', 'Subcampo', 'Interferencia', 'Tension', 'Estado_vacio', 'Localizacion', 'Georradar', 'Levantamiento']
        df2 = df2[['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']]
        df2[['Subcampo']] = df2[['Subcampo']].ffill()
        df2.dropna(subset=['Interferencia'], inplace=True)
        df2['Cuadrante'] = '2'
        st.session_state['df_q2'] = df2

        # --- Procesamiento Cuadrante 3 ---
        df3 = pd.read_csv(upload_q3, skiprows=8)
        df3.columns = ['Cuadrante', 'Subcampo', 'Interferencia', 'Tension', 'Estado_vacio', 'Localizacion', 'Georradar', 'Levantamiento']
        df3 = df3[['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']]
        df3[['Subcampo']] = df3[['Subcampo']].ffill()
        df3.dropna(subset=['Interferencia'], inplace=True)
        df3['Cuadrante'] = '3'
        st.session_state['df_q3'] = df3

        # --- Procesamiento Cuadrante 4 ---
        df4 = pd.read_csv(upload_q4, skiprows=7)
        df4.columns = ['idx', 'Cuadrante', 'Vial', 'Levantamiento_m', 'Dibujo', 'As_Built']
        df4 = df4[['Vial', 'Levantamiento_m']].dropna(subset=['Vial'])
        df4 = df4[df4['Vial'] != 'TOTAL']
        df4['Levantamiento_m'] = pd.to_numeric(df4['Levantamiento_m'], errors='coerce').fillna(0)
        df4['Cuadrante'] = '4'
        st.session_state['df_q4'] = df4
        
        st.session_state.data_loaded = True
        st.session_state.upload_ids = [id(f) for f in [upload_q1, upload_q2, upload_q3, upload_q4]]


# --- PROCESAR DATOS Y ALMACENAR EN SESIÓN ---
process_dataframes(uploaded_q1, uploaded_q2, uploaded_q3, uploaded_q4)

# --- OBTENER DATAFRAMES DEL ESTADO DE LA SESIÓN ---
df_q1 = st.session_state['df_q1']
df_q2 = st.session_state['df_q2']
df_q3 = st.session_state['df_q3']
df_q4 = st.session_state['df_q4']


# --- LÓGICA PARA EL RESUMEN GENERAL ---
total_vias_objetivo = 31588
vias_levantadas = df_q1['Levantamiento_m'].sum() + df_q4['Levantamiento_m'].sum()
porcentaje_vias = (vias_levantadas / total_vias_objetivo) if total_vias_objetivo > 0 else 0

total_interferencias = len(df_q2) + len(df_q3)
interferencias_completadas = df_q2['Levantamiento'].notna().sum() + df_q3['Levantamiento'].notna().sum()
porcentaje_interferencias = (interferencias_completadas / total_interferencias) if total_interferencias > 0 else 0

# --- MOSTRAR RESUMEN GENERAL ---
st.header("Resumen General del Proyecto")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="Avance de Vías (Metros)", value=f"{int(vias_levantadas)} / {total_vias_objetivo} m")
    st.progress(porcentaje_vias)
with col2:
    st.metric(label="Avance de Interferencias", value=f"{interferencias_completadas} / {total_interferencias}")
    st.progress(porcentaje_interferencias)

df_interferencias_total = pd.concat([df_q2, df_q3])
tension_counts = df_interferencias_total['Tension'].value_counts().reset_index()
tension_counts.columns = ['Tension', 'Cantidad']

fig_pie = px.pie(
    tension_counts, names='Tension', values='Cantidad',
    title='Distribución de Interferencias por Tensión',
    color_discrete_sequence=px.colors.sequential.RdBu
)
with col3:
    st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- SECCIONES POR CUADRANTE ---
st.header("Análisis y Edición por Cuadrante")

# --- Cuadrante 1 ---
with st.expander("📍 Cuadrante 1 - Topografía de Vías", expanded=True):
    total_m_q1 = st.session_state.df_q1['Levantamiento_m'].sum()
    st.metric("Total Levantado en Cuadrante 1", f"{int(total_m_q1)} m")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("**Editar Tabla (Cuadrante 1)**")
        st.session_state.df_q1 = st.data_editor(st.session_state.df_q1, num_rows="dynamic")
    with c2:
        fig1 = px.bar(
            st.session_state.df_q1, x='Vial', y='Levantamiento_m',
            title='Metros Levantados por Vial - Cuadrante 1', text_auto=True
        )
        st.plotly_chart(fig1, use_container_width=True)

# --- Cuadrante 4 ---
with st.expander("📍 Cuadrante 4 - Topografía de Vías", expanded=True):
    total_m_q4 = st.session_state.df_q4['Levantamiento_m'].sum()
    st.metric("Total Levantado en Cuadrante 4", f"{int(total_m_q4)} m")
    
    c1, c2 = st.columns([1, 2])
    with c1:
        st.write("**Editar Tabla (Cuadrante 4)**")
        st.session_state.df_q4 = st.data_editor(st.session_state.df_q4, num_rows="dynamic")
    with c2:
        fig4 = px.bar(
            st.session_state.df_q4, x='Vial', y='Levantamiento_m',
            title='Metros Levantados por Vial - Cuadrante 4', text_auto=True
        )
        st.plotly_chart(fig4, use_container_width=True)

# --- Cuadrante 2 ---
with st.expander("⚡ Cuadrante 2 - Interferencias", expanded=False):
    st.write("**Editar Tabla (Cuadrante 2)**")
    st.session_state.df_q2 = st.data_editor(st.session_state.df_q2, height=300)

# --- Cuadrante 3 ---
with st.expander("⚡ Cuadrante 3 - Interferencias", expanded=False):
    st.write("**Editar Tabla (Cuadrante 3)**")
    st.session_state.df_q3 = st.data_editor(st.session_state.df_q3, height=300)

