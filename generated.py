import streamlit as st
import pandas as pd
import plotly.express as px
import altair as alt
import os

# --- Load the dataset ---
@st.cache_data  # Cache data to speed up re-runs
def load_data():
    # Dynamically get the path to the CSV file (same folder as this script)
    base_path = os.path.dirname(__file__)
    csv_path = os.path.join(base_path, "imdb_movie_dataset.csv")
    
    df = pd.read_csv(csv_path)
    return df

df = load_data()

# --- Streamlit app title ---
st.title("IMDb Movie Dataset Dashboard")

# --- Data Overview ---
st.header("Data Overview")
st.write(df)
st.write(df.describe())

# --- Visualization Section ---
st.header("Visualizations")

# 1. Rating Distribution
st.subheader("Rating Distribution")
fig_hist = px.histogram(df, x="Rating", title="Distribution of Movie Ratings")
st.plotly_chart(fig_hist)

# 2. Revenue vs. Rating Scatter Plot
st.subheader("Revenue vs. Rating")
fig_scatter = px.scatter(df, x="Rating", y="Revenue (Millions)", 
                         title="Revenue vs. Rating", hover_data=['Title'])
st.plotly_chart(fig_scatter)

# 3. Revenue by Genre (Bar Chart)
st.subheader("Revenue by Genre")
genre_df = df.copy()
genre_df['Genre'] = genre_df['Genre'].str.split(',')
genre_df = genre_df.explode('Genre')
genre_df = genre_df.groupby('Genre')['Revenue (Millions)'].sum().reset_index()

fig_bar = px.bar(genre_df, x='Genre', y='Revenue (Millions)', title='Total Revenue by Genre')
st.plotly_chart(fig_bar)

# 4. Runtime Distribution (Box Plot)
st.subheader("Runtime Distribution")
fig_box = px.box(df, y="Runtime (Minutes)", title="Distribution of Movie Runtimes")
st.plotly_chart(fig_box)

# 5. Metascore vs. Rating (Scatter Plot with Altair)
st.subheader("Metascore vs. Rating (Altair)")
chart = alt.Chart(df).mark_circle().encode(
    x='Metascore',
    y='Rating',
    tooltip=['Title', 'Metascore', 'Rating']
).interactive()
st.altair_chart(chart, use_container_width=True)

# 6. Top 5 Movies by Revenue
st.subheader("Top 5 Movies by Revenue")
top_5_revenue = df.dropna(subset=['Revenue (Millions)']).nlargest(5, 'Revenue (Millions)')
fig_top5 = px.bar(top_5_revenue, x='Title', y='Revenue (Millions)', 
                  title='Top 5 Highest-Grossing Movies')
st.plotly_chart(fig_top5)

# --- Add more visualizations as needed ---
