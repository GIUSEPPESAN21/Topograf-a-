import streamlit as st
import pandas as pd
import io
import zipfile
import plotly.graph_objects as go

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
        background-color: #fafafa;
    }
    /* Asegurar que las columnas se estiren para alinear las tarjetas */
    div[data-testid="stHorizontalBlock"] {
        align-items: stretch;
    }
</style>
""", unsafe_allow_html=True)

# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN Y OBJETIVOS ---
def initialize_state():
    # Estructura de datos unificada para todos los cuadrantes
    cols_unified = ['Descripción', 'Tipo', 'Tarea', 'Cantidad']
    if 'df_q1' not in st.session_state: st.session_state.df_q1 = pd.DataFrame(columns=cols_unified)
    if 'df_q2' not in st.session_state: st.session_state.df_q2 = pd.DataFrame(columns=cols_unified)
    if 'df_q3' not in st.session_state: st.session_state.df_q3 = pd.DataFrame(columns=cols_unified)
    if 'df_q4' not in st.session_state: st.session_state.df_q4 = pd.DataFrame(columns=cols_unified)
    
    if 'objetivos_generales' not in st.session_state: st.session_state.objetivos_generales = {'vias': 31588, 'interferencias': 251}
    if 'objetivos_cuadrante' not in st.session_state:
        st.session_state.objetivos_cuadrante = {
            'Q1': {'vias': 7366, 'interferencias': 87}, 'Q2': {'vias': 13040, 'interferencias': 53},
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
                cols_unified = ['Descripción', 'Tipo', 'Tarea', 'Cantidad']
                for i in range(1, 5):
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        loaded_df = pd.read_csv(z.open(filename), sep=';')
                        st.session_state[f'df_q{i}'] = pd.DataFrame(loaded_df, columns=cols_unified).fillna(0) # Rellenar NaNs
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

# Diccionarios para almacenar el progreso de cada cuadrante
vias_progress = {}
localizacion_progress = {}
georadar_progress = {}
levantamiento_progress = {}

for i in range(1, 5):
    df = st.session_state.get(f'df_q{i}', pd.DataFrame())
    vias_val, loc_val, geo_val, lev_val = 0, 0, 0, 0
    if all(col in df.columns for col in ['Tipo', 'Tarea', 'Cantidad']):
        df_vias = df[df['Tipo'] == 'Vía y Drenajes']
        vias_val = safe_sum_numeric_column(df_vias, 'Cantidad')
        df_interf = df[df['Tipo'] == 'Interferencia']
        loc_val = safe_sum_numeric_column(df_interf[df_interf['Tarea'] == 'Localización'], 'Cantidad')
        geo_val = safe_sum_numeric_column(df_interf[df_interf['Tarea'] == 'Georadar'], 'Cantidad')
        lev_val = safe_sum_numeric_column(df_interf[df_interf['Tarea'] == 'Levantamiento'], 'Cantidad')
    vias_progress[i] = vias_val
    localizacion_progress[i] = loc_val
    georadar_progress[i] = geo_val
    levantamiento_progress[i] = lev_val

# CÁLCULOS TOTALES
vias_levantadas_total = sum(vias_progress.values())
localizacion_total = sum(localizacion_progress.values())
georadar_total = sum(georadar_progress.values())
levantamiento_total = sum(levantamiento_progress.values())

# --- DASHBOARD DE AVANCE GENERAL ---
st.header("Dashboard de Avance General del Proyecto")
d_col1, d_col2, d_col3, d_col4 = st.columns(4, gap="large")
total_vias_obj = st.session_state.objetivos_generales['vias']
total_interf_obj = st.session_state.objetivos_generales['interferencias']
d_col1.metric("Avance de Vías y Drenajes", f"{int(vias_levantadas_total):,} / {total_vias_obj:,} m", f"{(vias_levantadas_total/total_vias_obj if total_vias_obj > 0 else 0):.1%}")
d_col2.metric("Avance Localización", f"{int(localizacion_total)} / {total_interf_obj}", f"{(localizacion_total/total_interf_obj if total_interf_obj > 0 else 0):.1%}")
d_col3.metric("Avance Georadar", f"{int(georadar_total)} / {total_interf_obj}", f"{(georadar_total/total_interf_obj if total_interf_obj > 0 else 0):.1%}")
d_col4.metric("Avance Levantamiento", f"{int(levantamiento_total)} / {total_interf_obj}", f"{(levantamiento_total/total_interf_obj if total_interf_obj > 0 else 0):.1%}")
st.markdown("---")

# --- CONFIGURACIÓN DE OBJETIVOS ---
with st.expander("⚙️ Configurar Objetivos del Proyecto"):
    st.subheader("Objetivos Generales")
    g_col1, g_col2 = st.columns(2)
    st.session_state.objetivos_generales['vias'] = g_col1.number_input("Total Vías y Drenajes (m)", value=st.session_state.objetivos_generales['vias'], min_value=0, step=1000)
    st.session_state.objetivos_generales['interferencias'] = g_col2.number_input("Total Interferencias", value=st.session_state.objetivos_generales['interferencias'], min_value=0, step=10)
    st.subheader("Objetivos por Cuadrante")
    q_conf_cols = st.columns(4)
    for i in range(1, 5):
        with q_conf_cols[i-1]:
            st.markdown(f"**Cuadrante {i}**")
            st.session_state.objetivos_cuadrante[f'Q{i}']['vias'] = st.number_input(f"Vías Q{i} (m)", value=st.session_state.objetivos_cuadrante[f'Q{i}']['vias'], min_value=0, key=f"vias_q{i}_goal")
            st.session_state.objetivos_cuadrante[f'Q{i}']['interferencias'] = st.number_input(f"Interf. Q{i}", value=st.session_state.objetivos_cuadrante[f'Q{i}']['interferencias'], min_value=0, key=f"interf_q{i}_goal")
st.markdown("---")

# --- DASHBOARD Y GESTIÓN POR CUADRANTE ---
st.header("Avance y Gestión por Cuadrante")

def create_donut_chart(progress_value, total_value, title):
    progress_percent = (progress_value / total_value * 100) if total_value > 0 else 0
    fig = go.Figure(go.Indicator(
        mode = "gauge+number", value = progress_percent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 14}},
        gauge = {'axis': {'range': [None, 100]}, 'bar': {'color': "#0072C6"}, 'steps' : [{'range': [0, 100], 'color': "#F0F2F6"}]}))
    fig.update_layout(height=180, margin=dict(l=10, r=10, t=50, b=10))
    return fig

def render_quadrant_card(q_num):
    vias_obj = st.session_state.objetivos_cuadrante[f'Q{q_num}']['vias']
    interf_obj = st.session_state.objetivos_cuadrante[f'Q{q_num}']['interferencias']
    
    with st.container(border=True):
        st.subheader(f"📍 Cuadrante {q_num}")
        chart_cols = st.columns(4)
        
        # FIX: Añadir espacios para hacer los títulos de los gráficos únicos
        with chart_cols[0]:
            st.plotly_chart(create_donut_chart(vias_progress[q_num], vias_obj, f"Vías y Drenajes{' ' * q_num}"), use_container_width=True)
            st.info(f"`{int(vias_progress[q_num])} / {vias_obj} m`")
        with chart_cols[1]:
            st.plotly_chart(create_donut_chart(localizacion_progress[q_num], interf_obj, f"Localización{' ' * q_num}"), use_container_width=True)
            st.info(f"`{int(localizacion_progress[q_num])} / {interf_obj}`")
        with chart_cols[2]:
            st.plotly_chart(create_donut_chart(georadar_progress[q_num], interf_obj, f"Georadar{' ' * q_num}"), use_container_width=True)
            st.info(f"`{int(georadar_progress[q_num])} / {interf_obj}`")
        with chart_cols[3]:
            st.plotly_chart(create_donut_chart(levantamiento_progress[q_num], interf_obj, f"Levantamiento{' ' * q_num}"), use_container_width=True)
            st.info(f"`{int(levantamiento_progress[q_num])} / {interf_obj}`")

        with st.form(key=f"form_q{q_num}"):
            st.write("**Agregar Nuevo Registro**")
            tipo = st.selectbox("Tipo de Registro", ["Vía y Drenajes", "Interferencia"], key=f"tipo_q{q_num}")
            descripcion = st.text_input("Descripción (Nombre, ID, etc.)", key=f"desc_q{q_num}")
            if tipo == "Interferencia":
                tarea = st.selectbox("Tarea de Interferencia", ["Localización", "Georadar", "Levantamiento"], key=f"tarea_q{q_num}")
                cantidad = st.number_input("Cantidad de Puntos", min_value=1, step=1, key=f"cant_interf_q{q_num}")
            else:
                tarea = "Vías y Drenajes"
                cantidad = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key=f"cant_via_q{q_num}")
            if st.form_submit_button("✅ Guardar", use_container_width=True):
                if descripcion:
                    new_row = {'Descripción': descripcion, 'Tipo': tipo, 'Tarea': tarea, 'Cantidad': cantidad}
                    st.session_state[f'df_q{q_num}'] = pd.concat([st.session_state[f'df_q{q_num}'], pd.DataFrame([new_row])], ignore_index=True)
                    st.toast(f"¡Registro guardado en Cuadrante {q_num}!")
                    st.rerun()
        with st.expander(f"Ver/Editar Datos de Cuadrante {q_num}"):
            st.data_editor(st.session_state[f'df_q{q_num}'], num_rows="dynamic", use_container_width=True, key=f"editor_q{q_num}")

# --- RENDERIZADO DE CUADRANTES ---
q_c1, q_c2 = st.columns(2, gap="large")
with q_c1:
    render_quadrant_card(1)
with q_c2:
    render_quadrant_card(2)

q_c3, q_c4 = st.columns(2, gap="large")
with q_c3:
    render_quadrant_card(3)
with q_c4:
    render_quadrant_card(4)

