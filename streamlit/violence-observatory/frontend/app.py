import streamlit as st
import plotly.express as px

from src.data import load_app_data

# --- setup
BUCKET = "itam-anlytics-karla"


################################# App #################################
st.set_page_config(
    page_title="Observatorio de Seguridad Pública en México",
    page_icon="📍",
    layout="wide",
)

st.title("Observatorio de Seguridad Pública en México")
st.caption(
    "Plataforma interactiva para visualizar y comparar los niveles de violencia " \
    "en los estados de México."
)

year_scores, violence_scores = load_app_data(BUCKET)

# Sidebar
st.sidebar.header("Filtros")

states = sorted(year_scores["entidad_nombre"].unique())
selected_states = st.sidebar.multiselect(
    "Estado(s)",
    options=states,
    default=["Aguascalientes"],
)

levels = sorted(violence_scores["nivel"].unique())
selected_levels = st.sidebar.multiselect(
    "Nivel de violencia",
    options=levels,
    default=levels,
)

min_year = int(year_scores["anio"].min())
max_year = int(year_scores["anio"].max())

selected_years = st.sidebar.slider(
    "Rango de años",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year),
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
    violence_scores["entidad_nombre"].nunique(),
)

col2.metric(
    "Índice promedio",
    round(violence_scores["violence_score"].mean(), 1),
)

top_state = violence_scores.sort_values(
    "violence_score",
    ascending=False,
).iloc[0]

col3.metric(
    "Mayor índice",
    top_state["entidad_nombre"],
    round(top_state["violence_score"], 1),
)

critical_states = (violence_scores["nivel"] == "Crítico").sum()

col4.metric(
    "Estados críticos",
    int(critical_states),
)

st.divider()

# Ranking
st.subheader("Ranking actual del índice de violencia")

ranking = filtered_scores.sort_values(
    "violence_score",
    ascending=False,
)

fig_ranking = px.bar(
    ranking,
    x="violence_score",
    y="entidad_nombre",
    color="nivel",
    orientation="h",
    labels={
        "violence_score": "Índice de violencia",
        "entidad_nombre": "Estado",
        "nivel": "Nivel",
    },
)

fig_ranking.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig_ranking, use_container_width=True)

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
        "entidad_nombre": "Estado",
    },
)

st.plotly_chart(fig_line, use_container_width=True)