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
    /* Ajusta el padding superior del contenido principal */
    .st-emotion-cache-16txtl3 {
        padding-top: 2rem;
    }
    /* Estilo para los contenedores de KPIs */
    .st-emotion-cache-1v0mbdj {
        border: 1px solid #e1e4e8;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    /* Estilos para los títulos */
    h1 {
        font-size: 2.5em;
        font-weight: bold;
    }
    h2 {
        font-size: 2em;
        font-weight: bold;
    }
    h3 {
        font-size: 1.5em;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


# Suprimir advertencias
warnings.filterwarnings('ignore', category=UserWarning, module='pandas')

# --- Función de Carga Simplificada (Cacheada) ---
@st.cache_data
def load_cleaned_data(csv_path='datos_limpios_peliculas.csv'):
    """Carga el dataset ya transformado y limpio."""
    try:
        df = pd.read_csv(csv_path)
        valid_genres = sorted(list(df['main_genre'].unique()))
        return df, valid_genres
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo de datos limpios '{csv_path}'.")
        st.error("Por favor, asegúrate de que este archivo esté en tu repositorio de GitHub.")
        return pd.DataFrame(), []

# --- Carga de Datos Limpios ---
df_clean, valid_genres = load_cleaned_data()

# --- Encabezado ---
col1, col2 = st.columns([1, 4])
with col1:
    try:
        st.image('UdeO_logo2.jpg', width=120)
    except Exception:
        st.warning("Logo 'UdeO_logo2.jpg' no encontrado.")
with col2:
    st.title("Dashboard Estratégico de Análisis Cinematográfico")
    st.markdown("""
    **Maestría en Inteligencia Artificial Aplicada** | Inteligencia de Negocios  
    **Alumno:** Psic. Andres Cruz Degante | **Profesor:** Dr. Diego Alonso Gastelum Chavira
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

# --- Fila 1: KPIs de Alto Nivel ---
st.subheader("Indicadores Clave de Rendimiento (KPIs)")
with st.container(border=True):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Películas en Selección", f"{len(df_filtered):,}")
    col2.metric("Recaudación Total", f"${df_filtered['revenue'].sum() / 1_000_000_000:.2f} B")
    col3.metric("Presupuesto Promedio", f"${df_filtered['budget'].mean() / 1_000_000:.1f} M")
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
        tooltip=['title', 'budget', 'revenue', 'main_genre']
    ).interactive()
    st.altair_chart(chart_revenue, use_container_width=True)
    st.caption("Correlación entre inversión y ganancia bruta. (Muestra de hasta 1000 películas)")

with col2:
    st.markdown("##### Presupuesto vs. Retorno de Inversión (ROI)")
    # Filtrar ROIs extremos para una mejor visualización en el gráfico
    df_filtered_roi = df_filtered[df_filtered['roi'].between(-1, 20)] 
    chart_roi = alt.Chart(df_filtered_roi.sample(n=min(1000, len(df_filtered_roi)))).mark_circle(opacity=0.6).encode(
        x=alt.X('budget:Q', title='Presupuesto', axis=alt.Axis(format='$,.0s')),
        y=alt.Y('roi:Q', title='ROI', axis=alt.Axis(format='.0%')),
        color=alt.Color('main_genre:N', title='Género', scale=alt.Scale(scheme='tableau10')),
        tooltip=['title', 'budget', 'roi', 'main_genre']
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
    # Agrupar calificaciones en "buckets" o rangos para el gráfico
    df_filtered['rating_bucket'] = pd.cut(df_filtered['vote_average'], bins=range(0, 11), right=False, labels=[f"{i}-{i+1}" for i in range(10)])
    revenue_by_rating = df_filtered.groupby('rating_bucket')['revenue'].mean()
    st.bar_chart(revenue_by_rating)
    st.caption("Impacto de la calificación del público en el rendimiento en taquilla.")

st.divider()
st.sidebar.markdown("Use estos controles para explorar los datos históricos y descubrir patrones de éxito.")


