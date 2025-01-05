import streamlit as st
import pandas as pd
import asyncpg
import plotly.express as px
import asyncio
import os

# Database connection string
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres/dbname")

# Async function to fetch data
async def fetch_data():
    try:
        conn = await asyncpg.connect(DATABASE_URL)
        query = """
            SELECT created_at, sentiment, emotion, user_name, message
            FROM sentiment_analysis
            ORDER BY created_at DESC
        """
        data = await conn.fetch(query)
        await conn.close()
        df = pd.DataFrame(data, columns=["created_at", "sentiment", "emotion", "user_name", "message"])
        df["created_at"] = pd.to_datetime(df["created_at"])
        return df
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()

# Clean sentiment strings
def clean_sentiments(df):
    df["sentiment"] = df["sentiment"].str.split(",").str[0].str.strip()  # Extract primary sentiment
    return df

# Streamlit UI
st.set_page_config(page_title="Community Sentiment Dashboard", layout="wide")
st.title("🌟 Community Sentiment Dashboard")
st.markdown("---")

# Sidebar filters
st.sidebar.header("📊 Dashboard Filters")
date_range = st.sidebar.date_input("Filter by Date Range", [])
sentiment_filter = st.sidebar.multiselect("Filter by Sentiment", options=["Positive", "Neutral", "Negative"])
show_stacked_chart = st.sidebar.checkbox("Show Sentiment Stacked Chart", value=True)

# Fetch and process data
st.text("Fetching data from the database...")
data = asyncio.run(fetch_data())

if not data.empty:
    data = clean_sentiments(data)  # Clean sentiment strings

    # Apply filters
    if date_range and len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range)
        data = data[(data["created_at"] >= start_date) & (data["created_at"] <= end_date)]

    if sentiment_filter:
        data = data[data["sentiment"].isin(sentiment_filter)]

    if data.empty:
        st.warning("No data available for the selected filters.")
    else:
        # Summary Section
        st.subheader("📌 Key Insights")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("💬 Total Messages", len(data))
        with col2:
            st.metric("👥 Unique Users", data["user_name"].nunique())
        with col3:
            st.metric("🔝 Top Sentiment", data["sentiment"].mode().iloc[0])
        with col4:
            st.metric("🌟 Current Vibe", data.iloc[0]["sentiment"])

        st.markdown("---")

        # Sentiment Trends (Stacked Chart)
        if show_stacked_chart:
            st.subheader("📈 Sentiment Trends (Stacked Chart)")
            sentiment_trends = (
                data.groupby([data["created_at"].dt.date, "sentiment"])
                .size()
                .reset_index(name="count")
            )
            fig = px.bar(
                sentiment_trends,
                x="created_at",
                y="count",
                color="sentiment",
                title="Sentiment Distribution Over Time",
                labels={"created_at": "Date", "count": "Messages"},
                text="count",
                color_discrete_map={"Positive": "#4CAF50", "Negative": "#F44336", "Neutral": "#2196F3"},
            )
            fig.update_layout(
                barmode="stack",
                xaxis=dict(tickformat="%b %d", tickangle=45),
                plot_bgcolor="rgba(0, 0, 0, 0)",
                paper_bgcolor="rgba(0, 0, 0, 0)"
            )
            st.plotly_chart(fig, use_container_width=True)

        # Emotion Distribution
        st.subheader("🎭 Emotion Distribution")
        emotion_counts = data["emotion"].value_counts().reset_index()
        emotion_counts.columns = ["emotion", "count"]
        fig = px.pie(
            emotion_counts,
            names="emotion",
            values="count",
            title="Emotion Distribution",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        st.plotly_chart(fig)

        # Top User Contributions
        st.subheader("👤 Top Users by Contributions")
        user_counts = data["user_name"].value_counts().reset_index()
        user_counts.columns = ["user_name", "count"]
        fig = px.bar(
            user_counts.head(10),
            x="user_name",
            y="count",
            title="Top Users by Message Count",
            labels={"user_name": "User", "count": "Messages"},
            color="count",
            color_continuous_scale="Blues",
        )
        st.plotly_chart(fig, use_container_width=True)

        # Data Table
        st.subheader("📋 Detailed Data Table")
        st.dataframe(data, use_container_width=True)
else:
    st.warning("No data available to display.")
