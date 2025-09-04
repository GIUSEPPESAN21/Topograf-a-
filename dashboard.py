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
        background-color: #fafafa;
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
    cols_q2_q3 = ['Descripción', 'Tipo', 'Tarea', 'Cantidad'] # Nueva estructura de datos unificada
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
                # Definir columnas esperadas para asegurar compatibilidad
                cols_q1_q4 = ['Vial', 'Levantamiento (m)']
                cols_q2_q3 = ['Descripción', 'Tipo', 'Tarea', 'Cantidad']
                
                # Cargar Q1 y Q4 asegurando la estructura
                for i in [1, 4]:
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        loaded_df = pd.read_csv(z.open(filename), sep=';')
                        st.session_state[f'df_q{i}'] = pd.DataFrame(loaded_df, columns=cols_q1_q4)

                # Cargar Q2 y Q3 asegurando la estructura
                for i in [2, 3]:
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        loaded_df = pd.read_csv(z.open(filename), sep=';')
                        st.session_state[f'df_q{i}'] = pd.DataFrame(loaded_df, columns=cols_q2_q3)

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
    if column_name in df.columns: return pd.to_numeric(df[column_name], errors='coerce').sum()
    return 0

# CÁLCULOS POR CUADRANTE
vias_q1 = safe_sum_numeric_column(st.session_state.df_q1, 'Levantamiento (m)')
vias_q4 = safe_sum_numeric_column(st.session_state.df_q4, 'Levantamiento (m)')

# Cálculos seguros para Cuadrantes 2 y 3
df_q2 = st.session_state.df_q2
vias_q2 = 0
localizacion_q2, georadar_q2, levantamiento_q2 = 0, 0, 0
if 'Tipo' in df_q2.columns and 'Tarea' in df_q2.columns and 'Cantidad' in df_q2.columns:
    df_vias_q2 = df_q2[df_q2['Tipo'] == 'Vía y Drenajes']
    vias_q2 = safe_sum_numeric_column(df_vias_q2, 'Cantidad')
    df_interf_q2 = df_q2[df_q2['Tipo'] == 'Interferencia']
    localizacion_q2 = safe_sum_numeric_column(df_interf_q2[df_interf_q2['Tarea'] == 'Localización'], 'Cantidad')
    georadar_q2 = safe_sum_numeric_column(df_interf_q2[df_interf_q2['Tarea'] == 'Georadar'], 'Cantidad')
    levantamiento_q2 = safe_sum_numeric_column(df_interf_q2[df_interf_q2['Tarea'] == 'Levantamiento'], 'Cantidad')

df_q3 = st.session_state.df_q3
vias_q3 = 0
localizacion_q3, georadar_q3, levantamiento_q3 = 0, 0, 0
if 'Tipo' in df_q3.columns and 'Tarea' in df_q3.columns and 'Cantidad' in df_q3.columns:
    df_vias_q3 = df_q3[df_q3['Tipo'] == 'Vía y Drenajes']
    vias_q3 = safe_sum_numeric_column(df_vias_q3, 'Cantidad')
    df_interf_q3 = df_q3[df_q3['Tipo'] == 'Interferencia']
    localizacion_q3 = safe_sum_numeric_column(df_interf_q3[df_interf_q3['Tarea'] == 'Localización'], 'Cantidad')
    georadar_q3 = safe_sum_numeric_column(df_interf_q3[df_interf_q3['Tarea'] == 'Georadar'], 'Cantidad')
    levantamiento_q3 = safe_sum_numeric_column(df_interf_q3[df_interf_q3['Tarea'] == 'Levantamiento'], 'Cantidad')

# CÁLCULOS TOTALES (SUMA DE CUADRANTES)
vias_levantadas_total = vias_q1 + vias_q2 + vias_q3 + vias_q4
localizacion_total = localizacion_q2 + localizacion_q3
georadar_total = georadar_q2 + georadar_q3
levantamiento_total = levantamiento_q2 + levantamiento_q3

# --- DASHBOARD DE AVANCE GENERAL ---
st.header("Dashboard de Avance General del Proyecto")
col1, col2, col3, col4 = st.columns(4, gap="large")
total_vias_obj = st.session_state.objetivos_generales['vias']
total_interf_obj = st.session_state.objetivos_generales['interferencias']

porc_vias_total = (vias_levantadas_total / total_vias_obj) if total_vias_obj > 0 else 0
col1.metric("Avance de Vías y Drenajes", f"{int(vias_levantadas_total):,} / {total_vias_obj:,} m", f"{porc_vias_total:.1%}")
porc_loc_total = (localizacion_total / total_interf_obj) if total_interf_obj > 0 else 0
col2.metric("Avance Localización", f"{int(localizacion_total)} / {total_interf_obj}", f"{porc_loc_total:.1%}")
porc_geo_total = (georadar_total / total_interf_obj) if total_interf_obj > 0 else 0
col3.metric("Avance Georadar", f"{int(georadar_total)} / {total_interf_obj}", f"{porc_geo_total:.1%}")
porc_lev_total = (levantamiento_total / total_interf_obj) if total_interf_obj > 0 else 0
col4.metric("Avance Levantamiento", f"{int(levantamiento_total)} / {total_interf_obj}", f"{porc_lev_total:.1%}")
st.markdown("---")

# --- CONFIGURACIÓN DE OBJETIVOS (EDITABLE) ---
with st.expander("⚙️ Configurar Objetivos del Proyecto"):
    st.subheader("Objetivos Generales (Usados en el dashboard superior)")
    g_col1, g_col2 = st.columns(2)
    st.session_state.objetivos_generales['vias'] = g_col1.number_input("Total Vías y Drenajes (m)", value=st.session_state.objetivos_generales['vias'], min_value=0, step=1000)
    st.session_state.objetivos_generales['interferencias'] = g_col2.number_input("Total Interferencias", value=st.session_state.objetivos_generales['interferencias'], min_value=0, step=10)
    st.subheader("Objetivos por Cuadrante (Usados en las tarjetas inferiores)")
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
    if total_value == 0:
        progress_percent = 0
    else:
        progress_percent = round((progress_value / total_value) * 100, 1)

    fig = go.Figure(go.Indicator(
        mode = "gauge+number",
        value = progress_percent,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': title, 'font': {'size': 16}},
        gauge = {
            'axis': {'range': [None, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "#0072C6"},
            'steps' : [
                {'range': [0, 100], 'color': "#F0F2F6"}],
        }))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=40, b=10))
    return fig

# --- DISEÑO DE CUADRANTES ---
c1, c2 = st.columns(2, gap="large")
with c1:
    with st.container(border=True):
        st.subheader("📍 Cuadrante 1")
        vias_obj_q1 = st.session_state.objetivos_cuadrante['Q1']['vias']
        st.plotly_chart(create_donut_chart(vias_q1, vias_obj_q1, "Avance de Vías y Drenajes"), use_container_width=True)
        st.info(f"**Progreso:** `{int(vias_q1)} / {vias_obj_q1} m`")
        
        with st.form(key="form_q1"):
            st.write("**Agregar Vía**")
            vial = st.text_input("Nombre del Vial", key="vial_q1")
            metros = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key="metros_q1")
            if st.form_submit_button("✅ Guardar", use_container_width=True):
                if vial:
                    new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                    st.session_state.df_q1 = pd.concat([st.session_state.df_q1, new_data], ignore_index=True)
                    st.toast("¡Vía guardada en Cuadrante 1!")
                    st.rerun()
        with st.expander("Ver/Editar Datos de Cuadrante 1"):
            st.data_editor(st.session_state.df_q1, num_rows="dynamic", use_container_width=True, key="editor_q1")

def render_unified_quadrant(quadrant_num, df_key, vias_progress, levantamiento_progress, vias_obj, interf_obj):
    st.subheader(f"⚡ Cuadrante {quadrant_num}")
    chart_cols = st.columns(2)
    with chart_cols[0]:
        st.plotly_chart(create_donut_chart(vias_progress, vias_obj, f"Vías y Drenajes {' ' * quadrant_num}"), use_container_width=True)
        st.info(f"**Vías:** `{int(vias_progress)} / {vias_obj} m`")
    with chart_cols[1]:
        # Usamos el total de interferencias del cuadrante como referencia para el levantamiento
        total_interferencias_cuadrante = georadar_q2 + localizacion_q2 + levantamiento_progress if quadrant_num == 2 else georadar_q3 + localizacion_q3 + levantamiento_progress
        st.plotly_chart(create_donut_chart(levantamiento_progress, interf_obj, f"Interferencias {' ' * quadrant_num}"), use_container_width=True)
        st.info(f"**Interferencias (Levantamiento):** `{int(levantamiento_progress)} / {interf_obj}`")
    
    with st.form(key=f"form_q{quadrant_num}"):
        st.write("**Agregar Nuevo Registro**")
        tipo = st.selectbox("Tipo de Registro", ["Vía y Drenajes", "Interferencia"], key=f"tipo_q{quadrant_num}")
        descripcion = st.text_input("Descripción (Nombre, ID, etc.)", key=f"desc_q{quadrant_num}")
        
        if tipo == "Interferencia":
            tarea = st.selectbox("Tarea de Interferencia", ["Localización", "Georadar", "Levantamiento"], key=f"tarea_q{quadrant_num}")
            cantidad = st.number_input("Cantidad de Puntos", min_value=1, step=1, key=f"cant_interf_q{quadrant_num}")
        else: # Vía y Drenajes
            tarea = "Vías y Drenajes"
            cantidad = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key=f"cant_via_q{quadrant_num}")

        if st.form_submit_button("✅ Guardar", use_container_width=True):
            if descripcion:
                new_row = {'Descripción': descripcion, 'Tipo': tipo, 'Tarea': tarea, 'Cantidad': cantidad}
                st.session_state[df_key] = pd.concat([st.session_state[df_key], pd.DataFrame([new_row])], ignore_index=True)
                st.toast(f"¡Registro guardado en Cuadrante {quadrant_num}!")
                st.rerun()
    with st.expander(f"Ver/Editar Datos de Cuadrante {quadrant_num}"):
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{quadrant_num}")

with c2:
    with st.container(border=True):
        render_unified_quadrant(2, 'df_q2', vias_q2, levantamiento_q2, 
                                st.session_state.objetivos_cuadrante['Q2']['vias'], 
                                st.session_state.objetivos_cuadrante['Q2']['interferencias'])
        
st.markdown("<br>", unsafe_allow_html=True)

c3, c4 = st.columns(2, gap="large")
with c3:
    with st.container(border=True):
        render_unified_quadrant(3, 'df_q3', vias_q3, levantamiento_q3, 
                                st.session_state.objetivos_cuadrante['Q3']['vias'], 
                                st.session_state.objetivos_cuadrante['Q3']['interferencias'])

with c4:
    with st.container(border=True):
        st.subheader("📍 Cuadrante 4")
        vias_obj_q4 = st.session_state.objetivos_cuadrante['Q4']['vias']
        st.plotly_chart(create_donut_chart(vias_q4, vias_obj_q4, "Avance de Vías y Drenajes  "), use_container_width=True)
        st.info(f"**Progreso:** `{int(vias_q4)} / {vias_obj_q4} m`")

        with st.form(key="form_q4"):
            st.write("**Agregar Vía**")
            vial = st.text_input("Nombre del Vial", key="vial_q4")
            metros = st.number_input("Metros Levantados", min_value=0.0, format="%.2f", key="metros_q4")
            if st.form_submit_button("✅ Guardar", use_container_width=True):
                if vial:
                    new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                    st.session_state.df_q4 = pd.concat([st.session_state.df_q4, new_data], ignore_index=True)
                    st.toast("¡Vía guardada en Cuadrante 4!")
                    st.rerun()
        with st.expander("Ver/Editar Datos de Cuadrante 4"):
            st.data_editor(st.session_state.df_q4, num_rows="dynamic", use_container_width=True, key="editor_q4")

