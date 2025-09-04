import streamlit as st
import pandas as pd
import plotly.express as px

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Gestor de Topografía",
    page_icon="🏗️",
    layout="wide"
)

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
# Esto es crucial para guardar los datos mientras usas la app.
def initialize_session_state():
    """Crea DataFrames vacíos en el estado de la sesión si no existen."""
    if 'df_q1' not in st.session_state:
        st.session_state.df_q1 = pd.DataFrame(columns=['Vial', 'Levantamiento_m']).astype({'Levantamiento_m': 'float64'})
    if 'df_q2' not in st.session_state:
        st.session_state.df_q2 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento'])
    if 'df_q3' not in st.session_state:
        st.session_state.df_q3 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento'])
    if 'df_q4' not in st.session_state:
        st.session_state.df_q4 = pd.DataFrame(columns=['Vial', 'Levantamiento_m']).astype({'Levantamiento_m': 'float64'})

initialize_session_state()

# --- TÍTULO Y ENCABEZADO ---
st.title("🏗️ Gestor de Avance de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")

# --- BARRA LATERAL PARA SELECCIÓN DE MODO ---
with st.sidebar:
    st.image("https://i.imgur.com/v8pZ4Jp.png", width=120)
    st.header("Configuración")
    mode = st.radio(
        "Elige el modo de ingreso de datos:",
        ("Ingreso Manual", "Cargar Archivos CSV")
    )
    st.info("💡 Tus datos se guardan temporalmente. Si recargas la página, los cambios se perderán en modo manual.")

# --- LÓGICA DE INGRESO DE DATOS ---
if mode == "Cargar Archivos CSV":
    st.sidebar.header("Cargar Archivos")
    uploaded_files = st.sidebar.file_uploader(
        "Sube los 4 archivos CSV (delimitados por ';')", 
        accept_multiple_files=True, 
        type="csv"
    )
    if uploaded_files and len(uploaded_files) == 4:
        try:
            for file in uploaded_files:
                if "1" in file.name:
                    df1 = pd.read_csv(file, sep=';', skiprows=7)
                    df1.columns = ['Cuadrante_raw', 'Vial', 'Levantamiento_m', 'Dibujo', 'As_Built']
                    st.session_state.df_q1 = df1[['Vial', 'Levantamiento_m']].dropna(subset=['Vial'])
                    st.session_state.df_q1 = st.session_state.df_q1[st.session_state.df_q1['Vial'] != 'TOTAL']
                elif "2" in file.name:
                    df2 = pd.read_csv(file, sep=';', skiprows=7)
                    df2.columns = ['Cuadrante_raw', 'Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']
                    st.session_state.df_q2 = df2[['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']]
                    st.session_state.df_q2[['Subcampo']] = st.session_state.df_q2[['Subcampo']].ffill()
                elif "3" in file.name:
                    df3 = pd.read_csv(file, sep=';', skiprows=7)
                    df3.columns = ['Cuadrante_raw', 'Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']
                    st.session_state.df_q3 = df3[['Subcampo', 'Interferencia', 'Tension', 'Localizacion', 'Georradar', 'Levantamiento']]
                    st.session_state.df_q3[['Subcampo']] = st.session_state.df_q3[['Subcampo']].ffill()
                elif "4" in file.name:
                    df4 = pd.read_csv(file, sep=';', skiprows=7)
                    df4.columns = ['Cuadrante_raw', 'Vial', 'Levantamiento_m', 'Dibujo', 'As_Built']
                    st.session_state.df_q4 = df4[['Vial', 'Levantamiento_m']].dropna(subset=['Vial'])
                    st.session_state.df_q4 = st.session_state.df_q4[st.session_state.df_q4['Vial'] != 'TOTAL']
            
            # Limpiar NaNs de columnas importantes
            for df_key in ['df_q1', 'df_q2', 'df_q3', 'df_q4']:
                st.session_state[df_key].dropna(subset=st.session_state[df_key].columns[0], inplace=True)

            st.sidebar.success("¡Archivos cargados y procesados correctamente!")
        except Exception as e:
            st.sidebar.error(f"Error al procesar los archivos: {e}. Asegúrate que tengan el formato correcto.")

# --- SECCIONES DE EDICIÓN MANUAL ---
st.markdown("---")
st.header("Tablas de Datos por Cuadrante")

# Cuadrantes de Vías
col_vias1, col_vias2 = st.columns(2)
with col_vias1:
    with st.expander("📍 Cuadrante 1: Topografía de Vías", expanded=(mode=="Ingreso Manual")):
        st.write("Agrega o edita los datos de las vías.")
        st.session_state.df_q1 = st.data_editor(st.session_state.df_q1, num_rows="dynamic", key="editor_q1")
with col_vias2:
    with st.expander("📍 Cuadrante 4: Topografía de Vías", expanded=(mode=="Ingreso Manual")):
        st.write("Agrega o edita los datos de las vías.")
        st.session_state.df_q4 = st.data_editor(st.session_state.df_q4, num_rows="dynamic", key="editor_q4")

# Cuadrantes de Interferencias
col_int1, col_int2 = st.columns(2)
with col_int1:
    with st.expander("⚡ Cuadrante 2: Interferencias", expanded=(mode=="Ingreso Manual")):
        st.write("Agrega o edita los datos de interferencias.")
        st.session_state.df_q2 = st.data_editor(st.session_state.df_q2, num_rows="dynamic", key="editor_q2")
with col_int2:
    with st.expander("⚡ Cuadrante 3: Interferencias", expanded=(mode=="Ingreso Manual")):
        st.write("Agrega o edita los datos de interferencias.")
        st.session_state.df_q3 = st.data_editor(st.session_state.df_q3, num_rows="dynamic", key="editor_q3")


# --- DASHBOARD DE VISUALIZACIÓN ---
st.markdown("---")
st.header("Dashboard de Avance General")

# Convertir a numérico para evitar errores en los cálculos
st.session_state.df_q1['Levantamiento_m'] = pd.to_numeric(st.session_state.df_q1['Levantamiento_m'], errors='coerce').fillna(0)
st.session_state.df_q4['Levantamiento_m'] = pd.to_numeric(st.session_state.df_q4['Levantamiento_m'], errors='coerce').fillna(0)

# Lógica para el resumen general
total_vias_objetivo = 31588
vias_levantadas = st.session_state.df_q1['Levantamiento_m'].sum() + st.session_state.df_q4['Levantamiento_m'].sum()
porcentaje_vias = (vias_levantadas / total_vias_objetivo) if total_vias_objetivo > 0 else 0

total_interferencias = len(st.session_state.df_q2) + len(st.session_state.df_q3)
interferencias_completadas = st.session_state.df_q2['Levantamiento'].notna().sum() + st.session_state.df_q3['Levantamiento'].notna().sum()
porcentaje_interferencias = (interferencias_completadas / total_interferencias) if total_interferencias > 0 else 0

# Mostrar resumen general
if vias_levantadas == 0 and total_interferencias == 0:
    st.info("Aún no hay datos para mostrar en el dashboard. Ingresa datos o carga archivos para comenzar.")
else:
    col1, col2, col3 = st.columns(3)
    col1.metric("Avance de Vías (Metros)", f"{int(vias_levantadas):,} / {total_vias_objetivo:,} m", f"{porcentaje_vias:.1%} Progreso")
    col2.metric("Avance de Interferencias", f"{interferencias_completadas} / {total_interferencias}", f"{porcentaje_interferencias:.1%} Progreso")

    if total_interferencias > 0:
        df_interferencias_total = pd.concat([st.session_state.df_q2, st.session_state.df_q3])
        tension_counts = df_interferencias_total['Tension'].value_counts().reset_index()
        tension_counts.columns = ['Tension', 'Cantidad']
        fig_pie = px.pie(tension_counts, names='Tension', values='Cantidad', title='Distribución por Tensión', color_discrete_sequence=px.colors.qualitative.Pastel)
        col3.plotly_chart(fig_pie, use_container_width=True)

    # Gráficos de barras para Vías
    st.markdown("#### Progreso por Vial")
    c_vias1, c_vias2 = st.columns(2)
    with c_vias1:
        if not st.session_state.df_q1.empty:
            fig1 = px.bar(st.session_state.df_q1, x='Vial', y='Levantamiento_m', title='Cuadrante 1', text_auto=True)
            st.plotly_chart(fig1, use_container_width=True)
    with c_vias2:
        if not st.session_state.df_q4.empty:
            fig4 = px.bar(st.session_state.df_q4, x='Vial', y='Levantamiento_m', title='Cuadrante 4', text_auto=True)
            st.plotly_chart(fig4, use_container_width=True)
