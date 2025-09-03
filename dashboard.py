import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Dashboard de Topografía",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- ESTILOS CSS PERSONALIZADOS ---
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6;
    }
    .sidebar .sidebar-content {
        background: #f0f2f6;
    }
    .stMetric {
        border-radius: 10px;
        background-color: #FFFFFF;
        padding: 15px;
        box-shadow: 0 4px 8px 0 rgba(0,0,0,0.1);
    }
    .st-emotion-cache-1avp4 N1 {
        font-size: 1.2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# --- FUNCIÓN PARA CARGAR Y PROCESAR LOS DATOS ---
@st.cache_data
def load_data():
    """Carga, limpia y procesa los datos de los archivos CSV."""
    data = {}
    
    # --- Procesamiento Cuadrante 1 ---
    file_path = 'TABLAS JAVIER.xlsx - CUADRANTE 1.csv'
    if os.path.exists(file_path):
        df1 = pd.read_csv(file_path, skiprows=7)
        df1.columns = ['idx', 'Cuadrante', 'Vial', 'Levantamiento_m', 'Dibujo', 'As_Built']
        df1 = df1[['Cuadrante', 'Vial', 'Levantamiento_m']].dropna(subset=['Vial'])
        df1 = df1[df1['Vial'] != 'TOTAL']
        df1['Levantamiento_m'] = pd.to_numeric(df1['Levantamiento_m'], errors='coerce')
        df1['Cuadrante'] = '1'
        data['q1'] = df1

    # --- Procesamiento Cuadrante 2 ---
    file_path = 'TABLAS JAVIER.xlsx - CUADRANTE 2.csv'
    if os.path.exists(file_path):
        df2 = pd.read_csv(file_path, skiprows=8)
        df2.columns = ['Cuadrante', 'Subcampo', 'Interferencia', 'Tension', 'Estado_vacio', 'Localizacion', 'Georradar', 'Levantamiento']
        df2 = df2[['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']]
        df2[['Subcampo']] = df2[['Subcampo']].fillna(method='ffill')
        df2.dropna(subset=['Interferencia'], inplace=True)
        df2['Cuadrante'] = '2'
        data['q2'] = df2

    # --- Procesamiento Cuadrante 3 ---
    file_path = 'TABLAS JAVIER.xlsx - CUADRANTE 3.csv'
    if os.path.exists(file_path):
        df3 = pd.read_csv(file_path, skiprows=8)
        df3.columns = ['Cuadrante', 'Subcampo', 'Interferencia', 'Tension', 'Estado_vacio', 'Localizacion', 'Georradar', 'Levantamiento']
        df3 = df3[['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']]
        df3[['Subcampo']] = df3[['Subcampo']].fillna(method='ffill')
        df3.dropna(subset=['Interferencia'], inplace=True)
        df3['Cuadrante'] = '3'
        data['q3'] = df3

    # --- Procesamiento Cuadrante 4 ---
    file_path = 'TABLAS JAVIER.xlsx - CUADRANTE 4.csv'
    if os.path.exists(file_path):
        df4 = pd.read_csv(file_path, skiprows=7)
        df4.columns = ['idx', 'Cuadrante', 'Vial', 'Levantamiento_m', 'Dibujo', 'As_Built']
        df4 = df4[['Cuadrante', 'Vial', 'Levantamiento_m']].dropna(subset=['Vial'])
        df4 = df4[df4['Vial'] != 'TOTAL']
        df4['Levantamiento_m'] = pd.to_numeric(df4['Levantamiento_m'], errors='coerce')
        df4['Cuadrante'] = '4'
        data['q4'] = df4

    return data

# --- CARGA DE DATOS ---
data_frames = load_data()

# --- TÍTULO Y ENCABEZADO ---
st.title("🗺️ Dashboard de Avance de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")
st.markdown("---")

# --- LÓGICA PARA EL RESUMEN GENERAL ---
total_vias_objetivo = 31588
vias_levantadas = 0
if 'q1' in data_frames:
    vias_levantadas += data_frames['q1']['Levantamiento_m'].sum()
if 'q4' in data_frames:
    vias_levantadas += data_frames['q4']['Levantamiento_m'].sum()

porcentaje_vias = (vias_levantadas / total_vias_objetivo) if total_vias_objetivo > 0 else 0

total_interferencias = 0
interferencias_completadas = 0
if 'q2' in data_frames:
    total_interferencias += len(data_frames['q2'])
    interferencias_completadas += data_frames['q2']['Levantamiento'].notna().sum()
if 'q3' in data_frames:
    total_interferencias += len(data_frames['q3'])
    interferencias_completadas += data_frames['q3']['Levantamiento'].notna().sum()

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

# Combinar datos de interferencias para el gráfico de torta
if 'q2' in data_frames and 'q3' in data_frames:
    df_interferencias_total = pd.concat([data_frames['q2'], data_frames['q3']])
    tension_counts = df_interferencias_total['Tension'].value_counts().reset_index()
    tension_counts.columns = ['Tension', 'Cantidad']
    
    fig_pie = px.pie(
        tension_counts,
        names='Tension',
        values='Cantidad',
        title='Distribución de Interferencias por Tensión',
        color_discrete_sequence=px.colors.sequential.RdBu
    )
    fig_pie.update_layout(legend_title_text='Tensión')
    with col3:
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# --- SECCIONES POR CUADRANTE ---
st.header("Análisis por Cuadrante")

# --- Cuadrantes de Vías (1 y 4) ---
for q_name in ['q1', 'q4']:
    if q_name in data_frames:
        df = data_frames[q_name]
        cuadrante_num = df['Cuadrante'].iloc[0]
        with st.expander(f"📍 Cuadrante {cuadrante_num} - Topografía de Vías", expanded=False):
            total_m_q = df['Levantamiento_m'].sum()
            st.metric(f"Total Levantado en Cuadrante {cuadrante_num}", f"{int(total_m_q)} m")
            
            c1, c2 = st.columns([1, 2])
            with c1:
                st.dataframe(df[['Vial', 'Levantamiento_m']])
            with c2:
                fig = px.bar(
                    df,
                    x='Vial',
                    y='Levantamiento_m',
                    title=f'Metros Levantados por Vial - Cuadrante {cuadrante_num}',
                    labels={'Vial': 'Número de Vial', 'Levantamiento_m': 'Metros Levantados'},
                    text='Levantamiento_m'
                )
                fig.update_traces(texttemplate='%{text:.2s}', textposition='outside')
                st.plotly_chart(fig, use_container_width=True)

# --- Cuadrantes de Interferencias (2 y 3) ---
for q_name in ['q2', 'q3']:
    if q_name in data_frames:
        df = data_frames[q_name]
        cuadrante_num = df['Cuadrante'].iloc[0]
        with st.expander(f"⚡ Cuadrante {cuadrante_num} - Interferencias con Drenajes", expanded=False):
            completadas = df['Levantamiento'].notna().sum()
            total = len(df)
            st.metric(f"Interferencias Completadas en Cuadrante {cuadrante_num}", f"{completadas} de {total}")
            
            # Gráfico de estado
            df_status = df[['Localizacion', 'Georradar', 'Levantamiento']].notna().sum().reset_index()
            df_status.columns = ['Fase', 'Completadas']
            
            c1, c2 = st.columns([1, 1])
            with c1:
                fig_status = px.bar(
                    df_status,
                    x='Fase',
                    y='Completadas',
                    title=f'Avance por Fase - Cuadrante {cuadrante_num}',
                    labels={'Fase': 'Fase del Proceso', 'Completadas': 'Tareas Completadas'},
                    text='Completadas'
                )
                st.plotly_chart(fig_status, use_container_width=True)
            with c2:
                st.dataframe(df)
