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
</style>
""", unsafe_allow_html=True)


# --- INICIALIZACIÓN DEL ESTADO DE LA SESIÓN ---
def initialize_state():
    """Inicializa los DataFrames en el estado de la sesión si no existen."""
    if 'df_q1' not in st.session_state:
        st.session_state.df_q1 = pd.DataFrame(columns=['Vial', 'Levantamiento (m)'])
    if 'df_q2' not in st.session_state:
        st.session_state.df_q2 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento'])
    if 'df_q3' not in st.session_state:
        st.session_state.df_q3 = pd.DataFrame(columns=['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento'])
    if 'df_q4' not in st.session_state:
        st.session_state.df_q4 = pd.DataFrame(columns=['Vial', 'Levantamiento (m)'])

initialize_state()

# --- BARRA LATERAL ---
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
        
        st.download_button(
            label="📥 Descargar Datos",
            data=zip_buffer.getvalue(),
            file_name="progreso_topografia.zip",
            mime="application/zip",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"Error al crear el archivo de guardado: {e}")
    
    st.markdown("---")
    st.header("Cargar Progreso")
    uploaded_zip = st.file_uploader("Sube un archivo .zip para restaurar los datos.", type="zip")
    if uploaded_zip:
        try:
            with zipfile.ZipFile(uploaded_zip, 'r') as z:
                # Nombres de columnas esperados para estandarizar los datos
                cols_vias = ['Vial', 'Levantamiento (m)']
                cols_interf = ['Subcampo', 'Interferencia', 'Tensión', 'Localización', 'Georradar', 'Levantamiento']

                # Procesar Cuadrantes 1 y 4
                for i in [1, 4]:
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        with z.open(filename) as f:
                            df = pd.read_csv(f, sep=';')
                            if len(df.columns) == len(cols_vias):
                                df.columns = cols_vias
                                st.session_state[f'df_q{i}'] = df
                            else:
                                st.warning(f"El archivo '{filename}' tiene un formato inesperado y fue omitido.")
                    
                # Procesar Cuadrantes 2 y 3
                for i in [2, 3]:
                    filename = f'cuadrante_{i}.csv'
                    if filename in z.namelist():
                        with z.open(filename) as f:
                            df = pd.read_csv(f, sep=';')
                            if len(df.columns) == len(cols_interf):
                                df.columns = cols_interf
                                st.session_state[f'df_q{i}'] = df
                            else:
                                st.warning(f"El archivo '{filename}' tiene un formato inesperado y fue omitido.")
            st.success("¡Datos restaurados!")
            st.rerun()
        except Exception as e:
            st.error(f"Ocurrió un error al leer el archivo .zip: {e}")

# --- TÍTULO PRINCIPAL ---
st.title("🚧 Gestor de Avance de Topografía")
st.markdown("### **Proyecto:** GUAYEPO I & II")
st.markdown("---")

# --- DASHBOARD DE RESUMEN ---
st.header("Dashboard de Avance General")

# Lógica de cálculo
total_vias_objetivo = 31588
df_q1_numeric = pd.to_numeric(st.session_state.df_q1.get('Levantamiento (m)'), errors='coerce').fillna(0)
df_q4_numeric = pd.to_numeric(st.session_state.df_q4.get('Levantamiento (m)'), errors='coerce').fillna(0)
vias_levantadas = df_q1_numeric.sum() + df_q4_numeric.sum()
porcentaje_vias = (vias_levantadas / total_vias_objetivo) if total_vias_objetivo > 0 else 0

total_interferencias = len(st.session_state.df_q2) + len(st.session_state.df_q3)
interferencias_completadas = st.session_state.df_q2.get('Levantamiento', pd.Series(dtype=str)).notna().sum() + st.session_state.df_q3.get('Levantamiento', pd.Series(dtype=str)).notna().sum()
porcentaje_interferencias = (interferencias_completadas / total_interferencias) if total_interferencias > 0 else 0

if vias_levantadas == 0 and total_interferencias == 0:
    st.info("Aún no hay datos para mostrar. Ingresa registros en las pestañas de abajo para comenzar.")
else:
    col1, col2, col3 = st.columns(3, gap="large")
    col1.metric("Avance de Vías (Metros)", f"{int(vias_levantadas):,} / {total_vias_objetivo:,} m", f"{porcentaje_vias:.1%} Progreso")
    col2.metric("Avance de Interferencias", f"{interferencias_completadas} / {total_interferencias}", f"{porcentaje_interferencias:.1%} Progreso")

    if total_interferencias > 0:
        df_interferencias_total = pd.concat([st.session_state.df_q2, st.session_state.df_q3])
        
        # VERIFICACIÓN: Revisa si la columna 'Tensión' existe antes de crear el gráfico
        if 'Tensión' in df_interferencias_total.columns and not df_interferencias_total['Tensión'].dropna().empty:
            tension_counts = df_interferencias_total['Tensión'].value_counts().reset_index()
            tension_counts.columns = ['Tensión', 'count']
            
            fig_pie = px.pie(tension_counts, names='Tensión', values='count', title='Distribución por Tensión', color_discrete_sequence=px.colors.qualitative.Pastel)
            col3.plotly_chart(fig_pie, use_container_width=True)
        else:
            col3.info("No hay datos de 'Tensión' para mostrar el gráfico circular.")

st.markdown("---")
st.header("Gestión de Datos por Cuadrante")

# --- PESTAÑAS PARA CADA CUADRANTE ---
tab1, tab2, tab3, tab4 = st.tabs(["📍 Cuadrante 1", "⚡ Cuadrante 2", "⚡ Cuadrante 3", "📍 Cuadrante 4"])

# --- Lógica para Cuadrantes de Vías (1 y 4) ---
def render_vias_tab(tab, df_key, cuadrante_num):
    with tab:
        st.subheader(f"Formulario de Ingreso - Cuadrante {cuadrante_num}")
        with st.form(key=f"form_q{cuadrante_num}", clear_on_submit=True):
            col_form1, col_form2 = st.columns(2)
            vial = col_form1.text_input("Nombre del Vial (Ej: VIAL 1)")
            metros = col_form2.number_input("Metros Levantados", min_value=0.0, format="%.2f")
            submitted = st.form_submit_button("➕ Agregar Registro")
            if submitted and vial:
                new_data = pd.DataFrame([{'Vial': vial, 'Levantamiento (m)': metros}])
                st.session_state[df_key] = pd.concat([st.session_state[df_key], new_data], ignore_index=True)
                st.success(f"¡Vial '{vial}' agregado al Cuadrante {cuadrante_num}!")

        st.subheader(f"Datos Registrados - Cuadrante {cuadrante_num}")
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{cuadrante_num}")

# --- Lógica para Cuadrantes de Interferencias (2 y 3) ---
def render_interferencias_tab(tab, df_key, cuadrante_num):
    with tab:
        st.subheader(f"Formulario de Ingreso - Cuadrante {cuadrante_num}")
        with st.form(key=f"form_q{cuadrante_num}", clear_on_submit=True):
            c1, c2, c3 = st.columns(3)
            subcampo = c1.text_input("Subcampo")
            interferencia = c2.text_input("Interferencia")
            tension = c3.selectbox("Tensión", ["Baja", "Media", "Otra"])
            c4, c5, c6 = st.columns(3)
            localizacion = c4.text_input("Localización (Ej: OK, fecha)")
            georradar = c5.text_input("Georradar (Ej: OK, fecha)")
            levantamiento = c6.text_input("Levantamiento (Ej: OK, fecha)")
            submitted = st.form_submit_button("➕ Agregar Registro")
            if submitted and subcampo and interferencia:
                new_data = pd.DataFrame([{'Subcampo': subcampo, 'Interferencia': interferencia, 'Tensión': tension, 'Localización': localizacion, 'Georradar': georradar, 'Levantamiento': levantamiento}])
                st.session_state[df_key] = pd.concat([st.session_state[df_key], new_data], ignore_index=True)
                st.success(f"¡Interferencia '{interferencia}' agregada al Cuadrante {cuadrante_num}!")

        st.subheader(f"Datos Registrados - Cuadrante {cuadrante_num}")
        st.data_editor(st.session_state[df_key], num_rows="dynamic", use_container_width=True, key=f"editor_q{cuadrante_num}")

# Renderizar cada pestaña
render_vias_tab(tab1, 'df_q1', 1)
render_interferencias_tab(tab2, 'df_q2', 2)
render_interferencias_tab(tab3, 'df_q3', 3)
render_vias_tab(tab4, 'df_q4', 4)

