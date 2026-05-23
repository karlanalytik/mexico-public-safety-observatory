"""
Streamlit frontend for the Mexico Public Safety Observatory.

This application provides an interactive dashboard to explore violence levels
across Mexican states using a PCA-based violence index. Users can visualize
current rankings, geographic distribution, historical trends, and state-level
summaries through interactive charts and filters.
"""

import json
from pathlib import Path
import plotly.express as px
import streamlit as st

from src.data import load_app_data

# --- setup
BUCKET = "mexico-public-safety-observatory"
GEOJSON_PATH = Path(__file__).resolve().parents[1] / "data" / "estados-poligonos.geojson"

# --- Read data
year_scores, violence_scores = load_app_data(BUCKET)
with open(GEOJSON_PATH, encoding="utf-8") as file:
    mexico_geojson = json.load(file)


################################# App #################################
st.set_page_config(
    page_title="Observatorio de Seguridad Pública en México",
    page_icon="📍",
    layout="wide"
)

st.title("Observatorio de Seguridad Pública en México")
st.caption(
    "Plataforma interactiva para visualizar y comparar los niveles de violencia " \
    "en los estados de México."
)

# Sidebar
st.sidebar.header("Filtros")

states = sorted(year_scores["entidad_nombre"].unique())
selected_states = st.sidebar.multiselect(
    "Estado(s)",
    options=states,
    default=states[:3]
)

levels = sorted(violence_scores["nivel"].unique())
selected_levels = st.sidebar.multiselect(
    "Nivel de violencia",
    options=levels,
    default=levels
)

min_year = int(year_scores["anio"].min())
max_year = int(year_scores["anio"].max())

selected_years = st.sidebar.slider(
    "Rango de años",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)

# Filters
filtered_year_scores = year_scores[
    (year_scores["entidad_nombre"].isin(selected_states))
    & (year_scores["anio"].between(selected_years[0], selected_years[1]))
]

filtered_scores = violence_scores[
    violence_scores["nivel"].isin(selected_levels)
]

# KPIs
col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Estados analizados",
    violence_scores["entidad_nombre"].nunique()
)

col2.metric(
    "Índice promedio",
    round(violence_scores["violence_score"].mean(), 1)
)

top_state = violence_scores.sort_values(
    "violence_score",
    ascending=False
).iloc[0]

col3.metric(
    "Mayor índice",
    top_state["entidad_nombre"],
    round(top_state["violence_score"], 1),
    "inverse",
    delta_arrow="off"
)

critical_states = (violence_scores["nivel"] == "Crítico").sum()

col4.metric(
    "Estados críticos",
    int(critical_states)
)

st.divider()

# Map
st.subheader("Mapa nacional por nivel de violencia")

fig_map = px.choropleth(
    violence_scores,
    geojson=mexico_geojson,
    locations="entidad_nombre",
    featureidkey="properties.nom_edo",
    color="nivel",
    color_discrete_map={
        "Bajo": "#E9D5FF",
        "Medio": "#C084FC",
        "Alto": "#9333EA",
        "Crítico": "#581C87",
    },
    hover_data={
        "entidad_nombre": True,
        "violence_score": ":.1f",
        "nivel": True,
    },
    labels={
        "entidad_nombre": "Estado",
        "violence_score": "Índice de violencia",
        "nivel": "Nivel",
    },
)

fig_map.update_geos(
    fitbounds="locations",
    visible=False,
)

fig_map.update_layout(
    height=650,
    margin=dict(l=0, r=0, t=0, b=0),
)

st.plotly_chart(fig_map, use_container_width=True)

# Ranking
st.subheader("Ranking actual del índice de violencia")

ranking = filtered_scores.sort_values(
    "violence_score",
    ascending=False
)

fig_ranking = px.bar(
    ranking,
    x="violence_score",
    y="entidad_nombre",
    color="nivel",
    color_discrete_map={
        "Bajo": "#E9D5FF",
        "Medio": "#C084FC",
        "Alto": "#9333EA",
        "Crítico": "#581C87",
    },
    orientation="h",
    labels={
        "violence_score": "Índice de violencia",
        "entidad_nombre": "Estado",
        "nivel": "Nivel"
    }
)

fig_ranking.update_layout(
    yaxis={"categoryorder": "total ascending"},
    height=800
)

st.plotly_chart(fig_ranking, use_container_width=True)

st.divider()

# Time series
st.subheader("Evolución histórica del índice")

fig_line = px.line(
    filtered_year_scores,
    x="anio",
    y="violence_score",
    color="entidad_nombre",
    markers=True,
    labels={
        "anio": "Año",
        "violence_score": "Índice de violencia",
        "entidad_nombre": "Estado"
    }
)

st.plotly_chart(fig_line, use_container_width=True)

st.divider()

# State details
st.subheader("Resumen del estado seleccionado")

selected_state_summary = st.selectbox(
    "Selecciona un estado para ver su resumen",
    options=states,
)

state_history = year_scores[
    year_scores["entidad_nombre"] == selected_state_summary
].sort_values("anio")

latest_state_score = violence_scores[
    violence_scores["entidad_nombre"] == selected_state_summary
].iloc[0]

first_score = state_history.iloc[0]["violence_score"]
last_score = state_history.iloc[-1]["violence_score"]
change = last_score - first_score

filtered_state_history = state_history[
    state_history["anio"].between(selected_years[0], selected_years[1])
    ]
filtered_first_score = filtered_state_history.iloc[0]["violence_score"]
filtered_last_score = filtered_state_history.iloc[-1]["violence_score"]
filtered_change = filtered_last_score - filtered_first_score

col1, col2, col3 = st.columns(3)

col1.metric(
    "Índice actual",
    f"{latest_state_score['violence_score']:.1f}",
)

col2.metric(
    "Nivel actual",
    latest_state_score["nivel"],
)

col3.metric(
    "Cambio 2015-2025",
    f"{change:.1f}",
    delta=f"{change:.1f}",
    delta_color="inverse",
)

if filtered_change > 0:
    st.warning(
        f"Entre {int(filtered_state_history.iloc[0]['anio'])} y "
        f"{int(filtered_state_history.iloc[-1]['anio'])}, el índice de violencia en "
        f"{selected_state_summary} aumentó {filtered_change:.1f} puntos."
    )
elif filtered_change < 0:
    st.success(
        f"Entre {int(filtered_state_history.iloc[0]['anio'])} y "
        f"{int(filtered_state_history.iloc[-1]['anio'])}, el índice de violencia en "
        f"{selected_state_summary} disminuyó {abs(filtered_change):.1f} puntos."
    )
else:
    st.info(
        f"El índice de violencia en {selected_state_summary} se mantuvo sin cambios."
    )
