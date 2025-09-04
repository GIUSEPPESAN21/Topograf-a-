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
    .st-expander {
        border: 1px solid #e6e6e6;
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN Y OBJETIVOS ---
def initialize_state():
    # DataFrames de datos
    if 'df_q1' not in st.session_state:
        st.session_state.df_q1 = pd.DataFrame(columns=['Vial', 'Levantamiento (m)'])
    if 'df_q2' not in st.session_state:
        st.session_state.df_q2 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento'])
    if 'df_q3' not in st.session_state:
        st.session_state.df_q3 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento'])
    if 'df_q4' not in st.session_state:
        st.session_state.df_q4 = pd.DataFrame(columns=['Vial', 'Levantamiento (m)'])
        
    # Objetivos del proyecto (editables)
    if 'objetivos_generales' not in st.session_state:
        st.session_state.objetivos_generales = {
            'vias': 31588,
            'interferencias': 251
        }
    if 'objetivos_cuadrante' not in st.session_state:
        st.session_state.objetivos_cuadrante = {
            'Q1': {'vias': 7366, 'interferencias': 0},
            'Q2': {'vias': 0, 'interferencias': 53},
            'Q3': {'vias': 0, 'interferencias': 111},
            'Q4': {'vias': 11182, 'interferencias': 0}
        }

initialize_state()

# --- BARRA LATERAL (GUARDADO/CARGA) ---
with st.sidebar:
    st.image("https://i.imgur.com/b2d5kSg.png", width=150)
    st.title("Panel de Control")
    st.markdown("---")
    
    st.header("Guardar/Cargar Progreso")
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
    
    uploaded_zip = st.file_uploader("Sube un archivo .zip para restaurar los datos.", type="zip")
    if uploaded_zip:
        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as z:
                # Nombres de columnas esperados
                cols_vias = ['Vial', 'Levantamiento (m)']
                cols_interf = ['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento']
                
                # Procesar archivos con validación
                for i in [1, 4]: # Vias
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        df_temp = pd.read_csv(z.open(filename), sep=';')
                        if len(df_temp.columns) == len(cols_vias):
                            df_temp.columns = cols_vias
                            st.session_state[f'df_q{i}'] = df_temp
                        else:
                            st.warning(f"Archivo '{filename}' tiene formato incorrecto. Omitido.")
                
                for i in [2, 3]: # Interferencias
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        df_temp = pd.read_csv(z.open(filename), sep=';')
                        if len(df_temp.columns) == len(cols_interf):
                            df_temp.columns = cols_interf
                            st.session_state[f'df_q{i}'] = df_temp
                        else:
                            st.warning(f"Archivo '{filename}' tiene formato incorrecto. Omitido.")

            st.success("¡Datos restaurados!")
            st.rerun()
        except Exception as e:
            st.error(f"Error al procesar el archivo .zip: {e}")


# --- TÍTULO PRINCIPAL ---
st.title("🚧 Gestor de Avance de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")
st.markdown("---")

# --- LÓGICA DE CÁLCULO ---
def safe_sum_numeric_column(df, column_name):
    """Convierte de forma segura una columna a numérico y la suma, manejando errores."""
    try:
        if column_name in df.columns:
            return pd.to_numeric(df[column_name], errors='coerce').sum()
        return 0
    except Exception:
        return 0

vias_q1 = safe_sum_numeric_column(st.session_state.df_q1, 'Levantamiento (m)')
vias_q4 = safe_sum_numeric_column(st.session_state.df_q4, 'Levantamiento (m)')
vias_levantadas = vias_q1 + vias_q4

def count_completed(df, task_column):
    if task_column in df.columns:
        return df[task_column].notna().sum()
    return 0

localizacion_completadas = count_completed(st.session_state.df_q2, 'Localización') + count_completed(st.session_state.df_q3, 'Localización')
georradar_completadas = count_completed(st.session_state.df_q2, 'Georradar') + count_completed(st.session_state.df_q3, 'Georradar')
levantamiento_completadas = count_completed(st.session_state.df_q2, 'Levantamiento') + count_completed(st.session_state.df_q3, 'Levantamiento')


# --- DASHBOARD GENERAL ---
st.header("Dashboard de Avance General")
col1, col2, col3, col4 = st.columns(4, gap="large")
total_vias = st.session_state.objetivos_generales['vias']
total_interf = st.session_state.objetivos_generales['interferencias']

porcentaje_vias = (vias_levantadas / total_vias) if total_vias > 0 else 0
col1.metric("Avance de Vías (Metros)", f"{int(vias_levantadas):,} / {total_vias:,} m", f"{porcentaje_vias:.1%} Progreso")

porc_localizacion = (localizacion_completadas / total_interf) if total_interf > 0 else 0
col2.metric("Avance Localización", f"{localizacion_completadas} / {total_interf}", f"{porc_localizacion:.1%} Progreso")

porc_georradar = (georradar_completadas / total_interf) if total_interf > 0 else 0
col3.metric("Avance Georradar", f"{georradar_completadas} / {total_interf}", f"{porc_georradar:.1%} Progreso")

porc_levantamiento = (levantamiento_completadas / total_interf) if total_interf > 0 else 0
col4.metric("Avance Levantamiento", f"{levantamiento_completadas} / {total_interf}", f"{porc_levantamiento:.1%} Progreso")

# --- CONFIGURACIÓN DE OBJETIVOS (EDITABLE) ---
with st.expander("⚙️ Configurar Objetivos del Proyecto"):
    st.subheader("Objetivos Generales")
    g_col1, g_col2 = st.columns(2)
    st.session_state.objetivos_generales['vias'] = g_col1.number_input("Total Vías (m)", value=st.session_state.objetivos_generales['vias'], min_value=0, step=1000)
    st.session_state.objetivos_generales['interferencias'] = g_col2.number_input("Total Interferencias", value=st.session_state.objetivos_generales['interferencias'], min_value=0, step=10)
    
    st.subheader("Objetivos por Cuadrante")
    q_conf_cols = st.columns(4)
    for i in range(1, 5):
        with q_conf_cols[i-1]:
            st.markdown(f"**Cuadrante {i}**")
            st.session_state.objetivos_cuadrante[f'Q{i}']['vias'] = st.number_input(f"Vías Q{i} (m)", value=st.session_state.objetivos_cuadrante[f'Q{i}']['vias'], min_value=0, key=f"vias_q{i}_goal")
            st.session_state.objetivos_cuadrante[f'Q{i}']['interferencias'] = st.number_input(f"Interf. Q{i}", value=st.session_state.objetivos_cuadrante[f'Q{i}']['interferencias'], min_value=0, key=f"interf_q{i}_goal")

st.markdown("---")

# --- DASHBOARD POR CUADRANTE ---
st.header("Dashboard de Avance por Cuadrante")
q_cols = st.columns(4, gap="large")

def render_quadrant_card(column, title, vias_prog, interf_prog, q_key):
    with column:
        st.subheader(title)
        vias_total = st.session_state.objetivos_cuadrante[q_key]['vias']
        interf_total = st.session_state.objetivos_cuadrante[q_key]['interferencias']
        
        prog_v = (vias_prog / vias_total) if vias_total > 0 else 0
        st.write(f"**Vías:** `{int(vias_prog)} / {vias_total} m` ({prog_v:.1%})")
        st.progress(prog_v)
        
        prog_i = (interf_prog / interf_total) if interf_total > 0 else 0
        st.write(f"**Interferencias:** `{interf_prog} / {interf_total}` ({prog_i:.1%})")
        st.progress(prog_i)

render_quadrant_card(q_cols[0], "Cuadrante 1", vias_q1, 0, 'Q1')
interf_q2_completed = count_completed(st.session_state.df_q2, 'Levantamiento')
render_quadrant_card(q_cols[1], "Cuadrante 2", 0, interf_q2_completed, 'Q2')
interf_q3_completed = count_completed(st.session_state.df_q3, 'Levantamiento')
render_quadrant_card(q_cols[2], "Cuadrante 3", 0, interf_q3_completed, 'Q3')
render_quadrant_card(q_cols[3], "Cuadrante 4", vias_q4, 0, 'Q4')

st.markdown("---")
st.header("Gestión y Edición de Datos")

# --- PESTAÑAS DE GESTIÓN DE DATOS ---
tab1, tab2, tab3, tab4 = st.tabs(["📍 Cuadrante 1", "⚡ Cuadrante 2", "⚡ Cuadrante 3", "📍 Cuadrante 4"])

def render_vias_tab(tab, df_key, cuadrante_num):
    with tab:
        if st.button(f"➕ Agregar Registro a Cuadrante {cuadrante_num}", use_container_width=True): st.session_state[f'modal_q{cuadrante_num}'] = True
        if st.session_state.get(f'modal_q{cuadrante_num}', False):
            with st.dialog(f"Nuevo Registro - Cuadrante {cuadrante_num}"):
                with st.form(key=f"form_q{cuadrante_num}", clear_on_submit=True):
                    vial = st.text_input("Nombre del Vial")
                    metros = st.number_input("Metros Levantados", min_value=0.0, format="%.2f")
                    if st.form_submit_button("✅ Guardar") and vial:
                        new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                        st.session_state[df_key] = pd.concat([st.session_state[df_key], new_data], ignore_index=True)
                        st.session_state[f'modal_q{cuadrante_num}'] = False
                        st.rerun()
        st.subheader(f"Datos Registrados")
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{cuadrante_num}")

def render_interferencias_tab(tab, df_key, cuadrante_num):
    with tab:
        if st.button(f"➕ Agregar Registro a Cuadrante {cuadrante_num}", use_container_width=True): st.session_state[f'modal_q{cuadrante_num}'] = True
        if st.session_state.get(f'modal_q{cuadrante_num}', False):
            with st.dialog(f"Nuevo Registro - Cuadrante {cuadrante_num}"):
                with st.form(key=f"form_q{cuadrante_num}", clear_on_submit=True):
                    subcampo = st.text_input("Subcampo")
                    interferencia = st.text_input("Interferencia")
                    tension = st.selectbox("Tensión", ["Baja", "Media", "Otra"])
                    localizacion = st.text_input("Localización (Ej: OK, fecha)")
                    georradar = st.text_input("Georradar (Ej: OK, fecha)")
                    levantamiento = st.text_input("Levantamiento (Ej: OK, fecha)")
                    if st.form_submit_button("✅ Guardar") and subcampo and interferencia:
                        new_data = pd.DataFrame([{'Subcampo': subcampo, 'Interferencia': interferencia, 'Tensión': tension, 'Localización': localizacion, 'Georradar': georradar, 'Levantamiento': levantamiento}])
                        st.session_state[df_key] = pd.concat([st.session_state[df_key], new_data], ignore_index=True)
                        st.session_state[f'modal_q{cuadrante_num}'] = False
                        st.rerun()
        st.subheader(f"Datos Registrados")
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{cuadrante_num}")

render_vias_tab(tab1, 'df_q1', 1)
render_interferencias_tab(tab2, 'df_q2', 2)
render_interferencias_tab(tab3, 'df_q3', 3)
render_vias_tab(tab4, 'df_q4', 4)

