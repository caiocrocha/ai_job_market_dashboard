import streamlit as st
import pandas as pd
import plotly.express as px
import ast

st.set_page_config(layout="wide")
st.title("Job Market Intelligence Dashboard")

# -----------------------------
# Load data
# -----------------------------
df = pd.read_csv("jobs_normalized.csv")

# -----------------------------
# Parse required_skills column
# (stored as stringified Python list)
# -----------------------------
def parse_skills(x):
    try:
        return ast.literal_eval(x)
    except Exception:
        return []

df["required_skills"] = df["required_skills"].apply(parse_skills)

# -----------------------------
# Filters
# -----------------------------
roles = st.multiselect(
    "Role",
    sorted(df["role"].dropna().unique()),
    default=sorted(df["role"].dropna().unique())
)

experience_levels = st.multiselect(
    "Experience Level",
    sorted(df["required_experience"].dropna().unique()),
    default=sorted(df["required_experience"].dropna().unique())
)

filtered = df[
    (df["role"].isin(roles)) &
    (df["required_experience"].isin(experience_levels))
]

# -----------------------------
# Explode skills
# -----------------------------
skills_df = filtered.explode("required_skills")
skills_df = skills_df[skills_df["required_skills"].notna()]

# -----------------------------
# Count skills (SAFE)
# -----------------------------
skill_counts = (
    skills_df["required_skills"]
    .value_counts()
    .rename_axis("Skill")
    .reset_index(name="Count")
)

# -----------------------------
# Plot: Top skills
# -----------------------------
fig = px.bar(
    skill_counts.head(20),
    x="Count",
    y="Skill",
    orientation="h",
    title="Top Required Skills"
)


fig.update_yaxes(
    tickmode="linear",
    automargin=True
)

fig.update_layout(
    yaxis=dict(
        tickfont=dict(size=11)
    )
)

st.plotly_chart(fig, use_container_width=True)

# -----------------------------
# Plot: Skills by role
# -----------------------------
role_skill_counts = (
    skills_df
    .groupby(["role", "required_skills"])
    .size()
    .reset_index(name="count")
)

fig2 = px.density_heatmap(
    role_skill_counts,
    x="required_skills",
    y="role",
    z="count",
    title="Skill Demand by Role",
    color_continuous_scale="Viridis"
)

fig2.update_layout(
    xaxis_tickangle=45,
    height=600
)

st.plotly_chart(fig2, use_container_width=True)