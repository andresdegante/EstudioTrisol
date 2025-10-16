import streamlit as st
import pandas as pd
import numpy as np
import warnings
import altair as alt

# --- Configuración de la Página ---
st.set_page_config(
    page_title="Dashboard Estratégico - Trisol Estudios",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Estilos CSS para un look más profesional ---
st.markdown("""
<style>
    .st-emotion-cache-16txtl3 {padding-top: 2rem;}
    .st-emotion-cache-1v0mbdj {border: 1px solid #333; border-radius: 0.5rem; padding: 1rem; margin-bottom: 1rem;}
    h1 {font-size: 2.5em; font-weight: bold;}
    h2 {font-size: 2em; font-weight: bold;}
    h3 {font-size: 1.5em; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Suprimir advertencias
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')
warnings.filterwarnings('ignore', category=FutureWarning)

# --- Función de Carga Simplificada (Cacheada) ---
@st.cache_data
def load_cleaned_data(csv_path='datos_limpios_peliculas.csv'):
    try:
        df = pd.read_csv(csv_path)
        valid_genres = sorted(list(df['main_genre'].unique()))
        return df, valid_genres
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de datos limpios '{csv_path}'.")
        st.error("Por favor, asegúrate de que este archivo esté en tu repositorio de GitHub.")
        return pd.DataFrame(), []

# --- Función para formatear números grandes ---
def format_number(num):
    if num >= 1_000_000_000:
        return f"${num / 1_000_000_000:.2f} B"
    elif num >= 1_000_000:
        return f"${num / 1_000_000:.1f} M"
    else:
        return f"${num:,.0f}"

# --- Carga de Datos Limpios ---
df_clean, valid_genres = load_cleaned_data()

# --- Encabezado ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image('UdeO_logo.png', width=120)
    except Exception:
        st.warning("Logo 'UdeO_logo.png' no encontrado.")
with col2:
    st.title("Dashboard Estratégico de Análisis Cinematográfico")
    st.markdown("""
    **Maestría en Inteligencia Artificial Aplicada** | Inteligencia de Negocios  
    **Alumno:** Andres Cruz Degante | **Profesor:** Dr. Diego Alonso Gastelum Chavira
    """)

# --- Comprobación de Seguridad ---
if df_clean.empty:
    st.stop() 

# --- Barra Lateral (Filtros Globales) ---
st.sidebar.title("Panel de Filtros")
st.sidebar.markdown("Use estos controles para explorar los datos históricos y descubrir patrones de éxito.")

year_range = st.sidebar.slider(
    "Rango de Años de Estreno",
    min_value=int(df_clean['release_year'].min()),
    max_value=int(df_clean['release_year'].max()),
    value=(2010, int(df_clean['release_year'].max()))
)

budget_range = st.sidebar.slider(
    "Rango de Presupuesto (en millones de USD)",
    min_value=1,
    max_value=int(df_clean['budget'].max() / 1_000_000),
    value=(20, 150),
    step=5
)
budget_min = budget_range[0] * 1_000_000
budget_max = budget_range[1] * 1_000_000

genres_selected = st.sidebar.multiselect(
    "Seleccionar Géneros",
    options=valid_genres,
    default=['Action', 'Comedy', 'Drama', 'Horror', 'Science Fiction']
)

# --- Aplicar Filtros al DataFrame ---
df_filtered = df_clean[
    (df_clean['release_year'] >= year_range[0]) &
    (df_clean['release_year'] <= year_range[1]) &
    (df_clean['budget'] >= budget_min) &
    (df_clean['budget'] <= budget_max) &
    (df_clean['main_genre'].isin(genres_selected))
]

if df_filtered.empty:
    st.warning("No se encontraron películas con los filtros seleccionados. Por favor, ajuste su selección en la barra lateral.")
    st.stop() 

# --- PÁGINA PRINCIPAL (Dashboard) ---

st.header(f"Análisis para Trisol Estudios: {year_range[0]}-{year_range[1]}")
st.markdown(f"Analizando **{len(df_filtered):,}** películas que coinciden con los filtros.")

st.divider()

# --- Fila 1: KPIs de Alto Nivel (CORREGIDO CON FORMATO) ---
st.subheader("Indicadores Clave de Rendimiento (KPIs)")
with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Películas en Selección", f"{len(df_filtered):,}")
    col2.metric("Recaudación Total", format_number(df_filtered['revenue'].sum()))
    col3.metric("Presupuesto Promedio", format_number(df_filtered['budget'].mean()))
    col4.metric("ROI Promedio", f"{df_filtered['roi'].mean():.1%}")

st.divider()

# --- Fila 2: Análisis de Rentabilidad vs. Inversión ---
st.subheader("Análisis de Rentabilidad vs. Inversión")
col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Presupuesto vs. Recaudación")
    chart_revenue = alt.Chart(df_filtered.sample(n=min(1000, len(df_filtered)))).mark_circle(opacity=0.6).encode(
        x=alt.X('budget:Q', title='Presupuesto', axis=alt.Axis(format='$,.0s')),
        y=alt.Y('revenue:Q', title='Recaudación', axis=alt.Axis(format='$,.0s')),
        color=alt.Color('main_genre:N', title='Género', scale=alt.Scale(scheme='tableau10')),
        tooltip=[
            alt.Tooltip('title', title='Título'),
            alt.Tooltip('budget', title='Presupuesto', format='$,.2s'),
            alt.Tooltip('revenue', title='Recaudación', format='$,.2s'),
            alt.Tooltip('main_genre', title='Género')
        ]
    ).interactive()
    st.altair_chart(chart_revenue, use_container_width=True)
    st.caption("Correlación entre inversión y ganancia bruta. (Muestra de hasta 1000 películas)")

with col2:
    st.markdown("##### Presupuesto vs. Retorno de Inversión (ROI)")
    df_filtered_roi = df_filtered[df_filtered['roi'].between(-1, 20)] 
    chart_roi = alt.Chart(df_filtered_roi.sample(n=min(1000, len(df_filtered_roi)))).mark_circle(opacity=0.6).encode(
        x=alt.X('budget:Q', title='Presupuesto', axis=alt.Axis(format='$,.0s')),
        y=alt.Y('roi:Q', title='ROI', axis=alt.Axis(format='.0%')),
        color=alt.Color('main_genre:N', title='Género', scale=alt.Scale(scheme='tableau10')),
        tooltip=[
            alt.Tooltip('title', title='Título'),
            alt.Tooltip('budget', title='Presupuesto', format='$,.2s'),
            alt.Tooltip('roi', title='ROI', format='.1%'),
            alt.Tooltip('main_genre', title='Género')
        ]
    ).interactive()
    st.altair_chart(chart_roi, use_container_width=True)
    st.caption("Análisis clave: el mayor ROI no siempre corresponde a los mayores presupuestos.")

st.divider()

# --- Fila 3: Análisis de Contenido ---
st.subheader("Análisis de Contenido y Audiencia")
col1, col2 = st.columns(2)

with col1:
    st.markdown("##### Rentabilidad Promedio por Género")
    genre_roi_filtered = df_filtered.groupby('main_genre')['roi'].mean().sort_values(ascending=False)
    st.bar_chart(genre_roi_filtered)
    st.caption("Permite identificar qué géneros son más rentables para el rango de presupuesto seleccionado.")

with col2:
    st.markdown("##### Recaudación vs. Calificación de la Audiencia")
    df_chart = df_filtered.copy()
    df_chart['rating_bucket'] = pd.cut(df_chart['vote_average'], bins=np.arange(0, 11, 1), right=False, labels=[f"{i}-{i+1}" for i in range(10)])
    revenue_by_rating = df_chart.groupby('rating_bucket', observed=True)['revenue'].mean()
    st.bar_chart(revenue_by_rating)
    st.caption("Impacto de la calificación del público en el rendimiento en taquilla.")



st.divider()
st.caption("Este dashboard utiliza un subconjunto procesado del TMDB Movies Dataset 2023 disponible en Kaggle. Es fundamental destacar que, aunque el dataset original contiene ~930,000 registros, para un análisis financiero estratégico es crucial trabajar con datos de alta calidad. Después de un riguroso proceso de ETL (Extracción, Transformación y Carga) —que incluyó la limpieza de datos, la eliminación de registros sin información financiera (presupuesto y recaudación con valores mayores a cero), sin fecha de estreno, y la estandarización de géneros— el universo de películas viables para este análisis se consolidó en 8,467 registros.")
