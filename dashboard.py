import streamlit as st
import pandas as pd
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
    .stForm {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 20px;
        background-color: #ffffff;
    }
    .quadrant-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #e6e6e6;
        height: 100%;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN Y OBJETIVOS ---
def initialize_state():
    cols_q1_q4 = ['Vial', 'Levantamiento (m)']
    cols_q2_q3 = ['Descripción', 'Tipo', 'Valor', 'Localización', 'Georradar', 'Levantamiento']
    if 'df_q1' not in st.session_state: st.session_state.df_q1 = pd.DataFrame(columns=cols_q1_q4)
    if 'df_q2' not in st.session_state: st.session_state.df_q2 = pd.DataFrame(columns=cols_q2_q3)
    if 'df_q3' not in st.session_state: st.session_state.df_q3 = pd.DataFrame(columns=cols_q2_q3)
    if 'df_q4' not in st.session_state: st.session_state.df_q4 = pd.DataFrame(columns=cols_q1_q4)
    if 'objetivos_generales' not in st.session_state: st.session_state.objetivos_generales = {'vias': 31588, 'interferencias': 251}
    if 'objetivos_cuadrante' not in st.session_state:
        st.session_state.objetivos_cuadrante = {
            'Q1': {'vias': 7366, 'interferencias': 0}, 'Q2': {'vias': 13040, 'interferencias': 53},
            'Q3': {'vias': 0, 'interferencias': 111}, 'Q4': {'vias': 11182, 'interferencias': 0}
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
    except Exception as e: st.error(f"Error al crear el archivo: {e}")
    uploaded_zip = st.file_uploader("Sube un archivo .zip para restaurar los datos.", type="zip")
    if uploaded_zip:
        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as z:
                for i in range(1, 5):
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist(): st.session_state[f'df_q{i}'] = pd.read_csv(z.open(filename), sep=';')
            st.success("¡Datos restaurados!")
            st.rerun()
        except Exception as e: st.error(f"Error al procesar el archivo .zip: {e}")

# --- TÍTULO PRINCIPAL ---
st.title("🚧 Gestor de Avance de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")
st.markdown("---")

# --- LÓGICA DE CÁLCULO ---
def safe_sum_numeric_column(df, column_name):
    if column_name in df.columns: return pd.to_numeric(df[column_name], errors='coerce').sum()
    return 0
# Vías
vias_q1 = safe_sum_numeric_column(st.session_state.df_q1, 'Levantamiento (m)')
vias_q4 = safe_sum_numeric_column(st.session_state.df_q4, 'Levantamiento (m)')
df2_vias = st.session_state.df_q2[st.session_state.df_q2['Tipo'] == 'Vía']
df3_vias = st.session_state.df_q3[st.session_state.df_q3['Tipo'] == 'Vía']
vias_q2 = safe_sum_numeric_column(df2_vias, 'Valor')
vias_q3 = safe_sum_numeric_column(df3_vias, 'Valor')
vias_levantadas = vias_q1 + vias_q2 + vias_q3 + vias_q4
# Interferencias (Detallado)
df_interferencias = pd.concat([st.session_state.df_q2[st.session_state.df_q2['Tipo'] == 'Interferencia'], st.session_state.df_q3[st.session_state.df_q3['Tipo'] == 'Interferencia']])
localizacion_completadas = safe_sum_numeric_column(df_interferencias, 'Localización')
georradar_completadas = safe_sum_numeric_column(df_interferencias, 'Georradar')
levantamiento_completadas = safe_sum_numeric_column(df_interferencias, 'Levantamiento')
interf_q2_finalizadas = safe_sum_numeric_column(st.session_state.df_q2[st.session_state.df_q2['Tipo'] == 'Interferencia'], 'Levantamiento')
interf_q3_finalizadas = safe_sum_numeric_column(st.session_state.df_q3[st.session_state.df_q3['Tipo'] == 'Interferencia'], 'Levantamiento')

# --- DASHBOARD GENERAL (DETALLADO) ---
st.header("Dashboard de Avance General")
col1, col2, col3, col4 = st.columns(4, gap="large")
total_vias = st.session_state.objetivos_generales['vias']
total_interf = st.session_state.objetivos_generales['interferencias']
porcentaje_vias = (vias_levantadas / total_vias) if total_vias > 0 else 0
col1.metric("Avance de Vías (Metros)", f"{int(vias_levantadas):,} / {total_vias:,} m", f"{porcentaje_vias:.1%} Progreso")
porc_localizacion = (localizacion_completadas / total_interf) if total_interf > 0 else 0
col2.metric("Avance Localización", f"{int(localizacion_completadas)} / {total_interf}", f"{porc_localizacion:.1%} Progreso")
porc_georradar = (georradar_completadas / total_interf) if total_interf > 0 else 0
col3.metric("Avance Georradar", f"{int(georradar_completadas)} / {total_interf}", f"{porc_georradar:.1%} Progreso")
porc_levantamiento = (levantamiento_completadas / total_interf) if total_interf > 0 else 0
col4.metric("Avance Levantamiento", f"{int(levantamiento_completadas)} / {total_interf}", f"{porc_levantamiento:.1%} Progreso")

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

# --- DASHBOARD POR CUADRANTE Y GESTIÓN DE DATOS ---
st.header("Avance y Gestión por Cuadrante")

def render_progress(vias_prog, interf_prog, q_key):
    vias_total = st.session_state.objetivos_cuadrante[q_key]['vias']
    interf_total = st.session_state.objetivos_cuadrante[q_key]['interferencias']
    prog_v = (vias_prog / vias_total) if vias_total > 0 else 0
    st.write(f"**Vías:** `{int(vias_prog)} / {vias_total} m` ({prog_v:.1%})")
    st.progress(prog_v)
    prog_i = (interf_prog / interf_total) if interf_total > 0 else 0
    st.write(f"**Interferencias:** `{int(interf_prog)} / {interf_total}` ({prog_i:.1%})")
    st.progress(prog_i)
    st.markdown("---")

# --- DISEÑO DE CUADRANTES ---
c1, c2 = st.columns(2, gap="large")
with c1:
    with st.container(border=True):
        st.subheader("📍 Cuadrante 1")
        render_progress(vias_q1, 0, 'Q1')
        with st.form(key="form_q1"):
            st.write("**Agregar Nuevo Registro de Vía**")
            vial = st.text_input("Nombre del Vial", key="vial_q1")
            metros = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key="metros_q1")
            if st.form_submit_button("✅ Guardar Vía", use_container_width=True):
                if vial:
                    new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                    st.session_state.df_q1 = pd.concat([st.session_state.df_q1, new_data], ignore_index=True)
                    st.toast("¡Vía guardada en Cuadrante 1!")
                    st.rerun()
        with st.expander("Ver/Editar Datos Registrados"):
            st.data_editor(st.session_state.df_q1, num_rows="dynamic", use_container_width=True, key="editor_q1")

with c2:
    with st.container(border=True):
        st.subheader("⚡ Cuadrante 2")
        render_progress(vias_q2, interf_q2_finalizadas, 'Q2')
        with st.form(key="form_via_q2"):
            st.write("**Agregar Vía**")
            descripcion = st.text_input("Descripción de la Vía", key="desc_via_q2")
            valor = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key="val_via_q2")
            if st.form_submit_button("✅ Guardar Vía", use_container_width=True):
                if descripcion:
                    new_row = {'Descripción': descripcion, 'Tipo': 'Vía', 'Valor': valor, 'Localización': None, 'Georradar': None, 'Levantamiento': None}
                    st.session_state.df_q2 = pd.concat([st.session_state.df_q2, pd.DataFrame([new_row])], ignore_index=True)
                    st.toast("¡Vía guardada en Cuadrante 2!")
                    st.rerun()
        with st.form(key="form_interf_q2"):
            st.write("**Agregar Interferencia**")
            descripcion = st.text_input("ID o Descripción", key="desc_interf_q2")
            st.write("Marque tareas completadas:")
            check_cols = st.columns(3)
            loc = check_cols[0].checkbox("Localización", key="loc_q2")
            geo = check_cols[1].checkbox("Georradar", key="geo_q2")
            lev = check_cols[2].checkbox("Levantamiento", key="lev_q2")
            if st.form_submit_button("✅ Guardar Interferencia", use_container_width=True):
                if descripcion:
                    new_row = {'Descripción': descripcion, 'Tipo': 'Interferencia', 'Valor': 1, 'Localización': loc, 'Georradar': geo, 'Levantamiento': lev}
                    st.session_state.df_q2 = pd.concat([st.session_state.df_q2, pd.DataFrame([new_row])], ignore_index=True)
                    st.toast("¡Interferencia guardada en Cuadrante 2!")
                    st.rerun()
        with st.expander("Ver/Editar Datos Registrados"):
            st.data_editor(st.session_state.df_q2, num_rows="dynamic", use_container_width=True, key="editor_q2")

st.markdown("<br>", unsafe_allow_html=True) # Espacio vertical

c3, c4 = st.columns(2, gap="large")
with c3:
    with st.container(border=True):
        st.subheader("⚡ Cuadrante 3")
        render_progress(vias_q3, interf_q3_finalizadas, 'Q3')
        with st.form(key="form_via_q3"):
            st.write("**Agregar Vía**")
            descripcion = st.text_input("Descripción de la Vía", key="desc_via_q3")
            valor = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key="val_via_q3")
            if st.form_submit_button("✅ Guardar Vía", use_container_width=True):
                if descripcion:
                    new_row = {'Descripción': descripcion, 'Tipo': 'Vía', 'Valor': valor, 'Localización': None, 'Georradar': None, 'Levantamiento': None}
                    st.session_state.df_q3 = pd.concat([st.session_state.df_q3, pd.DataFrame([new_row])], ignore_index=True)
                    st.toast("¡Vía guardada en Cuadrante 3!")
                    st.rerun()
        with st.form(key="form_interf_q3"):
            st.write("**Agregar Interferencia**")
            descripcion = st.text_input("ID o Descripción", key="desc_interf_q3")
            st.write("Marque tareas completadas:")
            check_cols = st.columns(3)
            loc = check_cols[0].checkbox("Localización", key="loc_q3")
            geo = check_cols[1].checkbox("Georradar", key="geo_q3")
            lev = check_cols[2].checkbox("Levantamiento", key="lev_q3")
            if st.form_submit_button("✅ Guardar Interferencia", use_container_width=True):
                if descripcion:
                    new_row = {'Descripción': descripcion, 'Tipo': 'Interferencia', 'Valor': 1, 'Localización': loc, 'Georradar': geo, 'Levantamiento': lev}
                    st.session_state.df_q3 = pd.concat([st.session_state.df_q3, pd.DataFrame([new_row])], ignore_index=True)
                    st.toast("¡Interferencia guardada en Cuadrante 3!")
                    st.rerun()
        with st.expander("Ver/Editar Datos Registrados"):
            st.data_editor(st.session_state.df_q3, num_rows="dynamic", use_container_width=True, key="editor_q3")

with c4:
    with st.container(border=True):
        st.subheader("📍 Cuadrante 4")
        render_progress(vias_q4, 0, 'Q4')
        with st.form(key="form_q4"):
            st.write("**Agregar Nuevo Registro de Vía**")
            vial = st.text_input("Nombre del Vial", key="vial_q4")
            metros = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key="metros_q4")
            if st.form_submit_button("✅ Guardar Vía", use_container_width=True):
                if vial:
                    new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                    st.session_state.df_q4 = pd.concat([st.session_state.df_q4, new_data], ignore_index=True)
                    st.toast("¡Vía guardada en Cuadrante 4!")
                    st.rerun()
        with st.expander("Ver/Editar Datos Registrados"):
            st.data_editor(st.session_state.df_q4, num_rows="dynamic", use_container_width=True, key="editor_q4")

