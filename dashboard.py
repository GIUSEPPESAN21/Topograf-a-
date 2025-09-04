import streamlit as st
import pandas as pd
import plotly.express as px
import io
import zipfile

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Control de Topografía",
    page_icon="🚧",
    layout="wide"
)

# --- ESTILOS CSS PARA MEJORAR LA INTERFAZ ---
st.markdown("""
<style>
    .stApp {
        background-color: #F0F2F6;
    }
    .st-emotion-cache-16txtl3 {
        padding: 1rem 2rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        background-color: #FFFFFF;
        border-radius: 4px 4px 0px 0px;
        gap: 1px;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #0072C6;
        color: white;
    }
    .stProgress > div > div > div > div {
        background-color: #0072C6;
    }
    [data-testid="stMetricValue"] {
        font-size: 24px;
    }
</style>
""", unsafe_allow_html=True)

# --- OBJETIVOS DEL PROYECTO (CONSTANTES) ---
TOTAL_VIAS_GENERAL = 31588
TOTAL_INTERF_GENERAL = 251 # Nuevo total según tu solicitud

# Objetivos por Cuadrante (basados en los archivos Excel)
OBJETIVOS_CUADRANTE = {
    'Q1': {'vias': 7366, 'interferencias': 0},
    'Q2': {'vias': 0, 'interferencias': 53},
    'Q3': {'vias': 0, 'interferencias': 111},
    'Q4': {'vias': 11182, 'interferencias': 0}
}

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
def initialize_state():
    if 'df_q1' not in st.session_state:
        st.session_state.df_q1 = pd.DataFrame(columns=['Vial', 'Levantamiento (m)'])
    if 'df_q2' not in st.session_state:
        st.session_state.df_q2 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento'])
    if 'df_q3' not in st.session_state:
        st.session_state.df_q3 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento'])
    if 'df_q4' not in st.session_state:
        st.session_state.df_q4 = pd.DataFrame(columns=['Vial', 'Levantamiento (m)'])

initialize_state()

# --- BARRA LATERAL (GUARDADO/CARGA) ---
with st.sidebar:
    st.image("https://i.imgur.com/b2d5kSg.png", width=150)
    st.title("Panel de Control")
    st.markdown("---")
    
    st.header("Guardar Progreso")
    st.info("Guarda todos los datos de los 4 cuadrantes en un archivo .zip.")
    zip_buffer = io.BytesIO()
    try:
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
            for i in range(1, 5):
                df_key = f'df_q{i}'
                if not st.session_state[df_key].empty:
                    csv_buffer = st.session_state[df_key].to_csv(index=False, sep=';').encode()
                    zip_file.writestr(f'cuadrante_{i}.csv', csv_buffer)
        st.download_button("📥 Descargar Datos", zip_buffer.getvalue(), "progreso_topografia.zip", "application/zip", use_container_width=True)
    except Exception as e:
        st.error(f"Error al crear el archivo: {e}")
    
    st.markdown("---")
    st.header("Cargar Progreso")
    uploaded_zip = st.file_uploader("Sube un archivo .zip para restaurar los datos.", type="zip")
    if uploaded_zip:
        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as z:
                # Nombres de columnas esperados
                cols_vias = ['Vial', 'Levantamiento (m)']
                cols_interf = ['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento']
                for i in [1, 4]:
                    if f'cuadrante_{i}.csv' in z.namelist():
                        df = pd.read_csv(z.open(f'cuadrante_{i}.csv'), sep=';')
                        df.columns = cols_vias
                        st.session_state[f'df_q{i}'] = df
                for i in [2, 3]:
                    if f'cuadrante_{i}.csv' in z.namelist():
                        df = pd.read_csv(z.open(f'cuadrante_{i}.csv'), sep=';')
                        df.columns = cols_interf
                        st.session_state[f'df_q{i}'] = df
            st.success("¡Datos restaurados!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al leer el .zip: {e}")

# --- TÍTULO PRINCIPAL ---
st.title("🚧 Gestor de Avance de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")
st.markdown("---")

# --- LÓGICA DE CÁLCULO ---
vias_q1 = pd.to_numeric(st.session_state.df_q1.get('Levantamiento (m)'), errors='coerce').sum()
vias_q4 = pd.to_numeric(st.session_state.df_q4.get('Levantamiento (m)'), errors='coerce').sum()
vias_levantadas = vias_q1 + vias_q4

interf_q2 = st.session_state.df_q2.get('Levantamiento', pd.Series(dtype=str)).notna().sum()
interf_q3 = st.session_state.df_q3.get('Levantamiento', pd.Series(dtype=str)).notna().sum()
interferencias_completadas = interf_q2 + interf_q3

# --- DASHBOARD GENERAL ---
st.header("Dashboard de Avance General")
col1, col2, col3 = st.columns(3, gap="large")
porcentaje_vias = (vias_levantadas / TOTAL_VIAS_GENERAL) if TOTAL_VIAS_GENERAL > 0 else 0
col1.metric("Avance de Vías (Metros)", f"{int(vias_levantadas):,} / {TOTAL_VIAS_GENERAL:,} m", f"{porcentaje_vias:.1%} Progreso")

porcentaje_interferencias = (interferencias_completadas / TOTAL_INTERF_GENERAL) if TOTAL_INTERF_GENERAL > 0 else 0
col2.metric("Avance de Interferencias", f"{interferencias_completadas} / {TOTAL_INTERF_GENERAL}", f"{porcentaje_interferencias:.1%} Progreso")

if interferencias_completadas > 0:
    df_interferencias_total = pd.concat([st.session_state.df_q2, st.session_state.df_q3])
    if 'Tensión' in df_interferencias_total.columns and not df_interferencias_total['Tensión'].dropna().empty:
        tension_counts = df_interferencias_total['Tensión'].value_counts().reset_index()
        fig_pie = px.pie(tension_counts, names='Tensión', values='count', title='Distribución por Tensión', color_discrete_sequence=px.colors.qualitative.Pastel)
        col3.plotly_chart(fig_pie, use_container_width=True)
else:
    col3.info("No hay datos para mostrar el gráfico circular.")

st.markdown("---")

# --- DASHBOARD POR CUADRANTE ---
st.header("Dashboard de Avance por Cuadrante")
q_cols = st.columns(4, gap="large")

def render_quadrant_card(column, title, vias_prog, vias_total, interf_prog, interf_total):
    with column:
        st.subheader(title)
        # Vías
        st.write(f"**Vías:** `{int(vias_prog)} / {vias_total} m`")
        prog_v = (vias_prog / vias_total) if vias_total > 0 else 0
        st.progress(prog_v)
        # Interferencias
        st.write(f"**Interferencias:** `{interf_prog} / {interf_total}`")
        prog_i = (interf_prog / interf_total) if interf_total > 0 else 0
        st.progress(prog_i)

render_quadrant_card(q_cols[0], "Cuadrante 1", vias_q1, OBJETIVOS_CUADRANTE['Q1']['vias'], 0, OBJETIVOS_CUADRANTE['Q1']['interferencias'])
render_quadrant_card(q_cols[1], "Cuadrante 2", 0, OBJETIVOS_CUADRANTE['Q2']['vias'], interf_q2, OBJETIVOS_CUADRANTE['Q2']['interferencias'])
render_quadrant_card(q_cols[2], "Cuadrante 3", 0, OBJETIVOS_CUADRANTE['Q3']['vias'], interf_q3, OBJETIVOS_CUADRANTE['Q3']['interferencias'])
render_quadrant_card(q_cols[3], "Cuadrante 4", vias_q4, OBJETIVOS_CUADRANTE['Q4']['vias'], 0, OBJETIVOS_CUADRANTE['Q4']['interferencias'])

st.markdown("---")
st.header("Gestión y Edición de Datos")

# --- PESTAÑAS DE GESTIÓN DE DATOS ---
tab1, tab2, tab3, tab4 = st.tabs(["📍 Cuadrante 1", "⚡ Cuadrante 2", "⚡ Cuadrante 3", "📍 Cuadrante 4"])

# --- Lógica para Cuadrantes de Vías (1 y 4) ---
def render_vias_tab(tab, df_key, cuadrante_num):
    with tab:
        if st.button(f"➕ Agregar Registro a Cuadrante {cuadrante_num}", use_container_width=True):
            st.session_state[f'modal_q{cuadrante_num}'] = True

        if st.session_state.get(f'modal_q{cuadrante_num}', False):
            with st.dialog(f"Nuevo Registro - Cuadrante {cuadrante_num}"):
                with st.form(key=f"form_q{cuadrante_num}", clear_on_submit=True):
                    vial = st.text_input("Nombre del Vial (Ej: VIAL 1)")
                    metros = st.number_input("Metros Levantados", min_value=0.0, format="%.2f")
                    submitted = st.form_submit_button("✅ Guardar")
                    if submitted and vial:
                        new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                        st.session_state[df_key] = pd.concat([st.session_state[df_key], new_data], ignore_index=True)
                        st.session_state[f'modal_q{cuadrante_num}'] = False
                        st.rerun()

        st.subheader(f"Datos Registrados")
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{cuadrante_num}")

# --- Lógica para Cuadrantes de Interferencias (2 y 3) ---
def render_interferencias_tab(tab, df_key, cuadrante_num):
    with tab:
        if st.button(f"➕ Agregar Registro a Cuadrante {cuadrante_num}", use_container_width=True):
            st.session_state[f'modal_q{cuadrante_num}'] = True

        if st.session_state.get(f'modal_q{cuadrante_num}', False):
            with st.dialog(f"Nuevo Registro - Cuadrante {cuadrante_num}"):
                with st.form(key=f"form_q{cuadrante_num}", clear_on_submit=True):
                    subcampo = st.text_input("Subcampo")
                    interferencia = st.text_input("Interferencia")
                    tension = st.selectbox("Tensión", ["Baja", "Media", "Otra"])
                    localizacion = st.text_input("Localización (Ej: OK, fecha)")
                    georradar = st.text_input("Georradar (Ej: OK, fecha)")
                    levantamiento = st.text_input("Levantamiento (Ej: OK, fecha)")
                    submitted = st.form_submit_button("✅ Guardar")
                    if submitted and subcampo and interferencia:
                        new_data = pd.DataFrame([{'Subcampo': subcampo, 'Interferencia': interferencia, 'Tensión': tension, 'Localización': localizacion, 'Georradar': georradar, 'Levantamiento': levantamiento}])
                        st.session_state[df_key] = pd.concat([st.session_state[df_key], new_data], ignore_index=True)
                        st.session_state[f'modal_q{cuadrante_num}'] = False
                        st.rerun()

        st.subheader(f"Datos Registrados")
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{cuadrante_num}")

# Renderizar cada pestaña
render_vias_tab(tab1, 'df_q1', 1)
render_interferencias_tab(tab2, 'df_q2', 2)
render_interferencias_tab(tab3, 'df_q3', 3)
render_vias_tab(tab4, 'df_q4', 4)
