import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Page config
st.set_page_config(
    page_title="Job Salary Explorer",
    page_icon="💼",
    layout="centered"
)

st.title("Job Salary Explorer")
st.write("A simple dashboard to explore salary data from RemoteOK jobs.")

# Data
df = pd.read_csv("data/remoteok_jobs_final.csv")

df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")
df["avg_salary"] = (df["salary_min"] + df["salary_max"]) / 2

df_salary = df[df["avg_salary"] > 0]

# Filter slider
salary_min = int(df_salary["avg_salary"].min())
salary_max = int(df_salary["avg_salary"].max())

salary_range = st.slider(
    "Select salary range($)",
    min_value=salary_min,
    max_value=salary_max,
    value=(salary_min, salary_max),
    step=1000
)

filtered = df_salary[
    (df_salary["avg_salary"] >= salary_range[0]) &
    (df_salary["avg_salary"] <= salary_range[1])
]

st.write(f"Showing {len(filtered)} jobs in selected range.")

# Show salary distribution
fig, ax = plt.subplots(figsize=(10, 4))
sns.histplot(filtered["avg_salary"], bins=30, kde=True, ax=ax)
ax.set_title("Salary Distribution")
ax.set_xlabel("Average Anual Salary ($)")
st.pyplot(fig)

# Top tags
st.write("### Top Tags by Count")
import ast
from collections import Counter

filtered["tags"] = filtered["tags"].apply(ast.literal_eval)

flat_tags = [tag for sublist in filtered["tags"] for tag in sublist]
tag_counts = Counter(flat_tags)
top_tags = tag_counts.most_common(10)

tags_df = pd.DataFrame(top_tags, columns=["Tag", "Count"])

st.bar_chart(tags_df.set_index("Tag"))