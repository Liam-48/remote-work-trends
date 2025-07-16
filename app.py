import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from collections import defaultdict

# Page config
st.set_page_config(
    page_title="Job Salary Explorer",
    page_icon="💼"
)

DARK_BG = "#0e1117"
TEXT_COLOR = "#FAFAFA"

#seaborn style
sns.set_style({
    "axes.facecolor": DARK_BG,
    "figure.facecolor": DARK_BG,
    "axes.labelcolor": TEXT_COLOR,
    "xtick.color": TEXT_COLOR,
    "ytick.color": TEXT_COLOR,
    "text.color": TEXT_COLOR
})

st.title("Job Salary Explorer")
st.caption("Data scraped from RemoteOK · Built by Liam Gorocica")
st.write("A simple dashboard to explore salary data from RemoteOK jobs.")

# Data
df = pd.read_csv("data/remoteok_jobs_final.csv")

df["salary_min"] = pd.to_numeric(df["salary_min"], errors="coerce")
df["salary_max"] = pd.to_numeric(df["salary_max"], errors="coerce")
df["avg_salary"] = (df["salary_min"] + df["salary_max"]) / 2

df_salary = df[df["avg_salary"] > 0]

# Sidebar config
st.sidebar.header("Filters")

# Filter slider
salary_min = int(df_salary["avg_salary"].min())
salary_max = int(df_salary["avg_salary"].max())

salary_range = st.sidebar.slider(
    "Select salary range($)",
    min_value=salary_min,
    max_value=salary_max,
    value=(salary_min, salary_max),
    step=1000
)

companies = df_salary["company"].dropna().unique().tolist()
selected_companies = st.sidebar.multiselect(
    "Filter by company",
    options=companies,
    default=companies
)

filtered = df_salary[
    (df_salary["avg_salary"] >= salary_range[0]) &
    (df_salary["avg_salary"] <= salary_range[1]) &
    (df_salary["company"].isin(selected_companies))
]

st.sidebar.write(f"**Jobs in current filter:** {len(filtered)}")
st.sidebar.write(f"**Average salary:** ${filtered['avg_salary'].mean():,.0f}")

# Show salary distribution
st.markdown("### Salary Distribution")
fig, ax = plt.subplots(figsize=(10, 4))
sns.histplot(filtered["avg_salary"], bins=30, kde=True, ax=ax, color='#88ccfc', alpha=1.0)
sns.despine(bottom = True, left = True)
ax.set_xlabel("Average Anual Salary ($)")
st.pyplot(fig)

# Top tags
st.write("### Top Tags by Count")
import ast
from collections import Counter

filtered["tags"] = filtered["tags"].apply(ast.literal_eval)

flat_tags = [tag.title() for sublist in filtered["tags"] for tag in sublist]
tag_counts = Counter(flat_tags)
top_tags = tag_counts.most_common(10)

tags_df = pd.DataFrame(top_tags, columns=["Tag", "Count"])

st.bar_chart(tags_df.set_index("Tag"))

# Salary per tags
df_salary = filtered.copy()
tag_salaries = []

for _,row in df_salary.iterrows():
    tags = row["tags"]
    salary = row["avg_salary"]
    if isinstance(tags, list):
        for tag in tags:
            tag_salaries.append((tag.title(), salary))
salary_by_tag = defaultdict(list)

for tag, salary in tag_salaries:
    salary_by_tag[tag].append(salary)

tag_salary_avg = {tag: sum(sals)/len(sals) for tag, sals in salary_by_tag.items()}

top_salary_tags = sorted(tag_salary_avg.items(), key=lambda x: x[1], reverse=True)[:10]
tags_df = pd.DataFrame(top_salary_tags, columns=["Tag", "Avg_Salary"])

st.markdown("### Top 10 Tags by Average Salary")
fig, ax = plt.subplots(figsize=(10, 4))
sns.barplot(x="Avg_Salary", y="Tag", data=tags_df, color='#88ccfc', ax=ax)
ax.set_xlabel("Average Salary ($)")
st.pyplot(fig)

# Dataframe table
st.markdown("### Filtered Jobs")
st.dataframe(filtered[["position", "company", "location", "salary_min", "salary_max", "avg_salary", "tags"]].reset_index(drop=True))