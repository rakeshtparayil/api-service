import os
import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Search Engine Land Articles",
    page_icon="🔍",
    layout="wide"
)

st.title("Search Engine Land Articles")

# Database connection function
@st.cache_resource
def get_connection():
    db_url = os.getenv("DB_CONN")
    if not db_url:
        st.error("Database connection URL not found in environment variables")
        st.stop()

    result = urlparse(db_url)
    conn_params = {
        'dbname': result.path[1:],
        'user': result.username,
        'password': result.password,
        'host': result.hostname,
        'port': result.port
    }
    return psycopg2.connect(**conn_params)

# Function to fetch articles
def fetch_articles(category_filter=None, limit=100):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    base_query = """
        SELECT id, title, url, 
               COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') AS category, 
               category_confidence
        FROM search_engine_land_articles
    """
    params = []

    if category_filter and category_filter != "All":
        base_query += " WHERE COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') = %s"
        params.append(category_filter)

    base_query += " ORDER BY id DESC LIMIT %s"
    params.append(limit)

    cursor.execute(base_query, params)
    articles = cursor.fetchall()
    cursor.close()
    return articles

# Function to get available categories
def get_categories():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT DISTINCT COALESCE(NULLIF(TRIM(category), ''), 'Uncategorized') AS category
        FROM search_engine_land_articles
        ORDER BY category
    """)
    categories = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return categories

# Sidebar filters
st.sidebar.title("Filters")
categories = get_categories()
category_filter = st.sidebar.selectbox("Filter by category", ["All"] + categories)
limit = st.sidebar.slider("Number of articles to display", 10, 100, 50)

# Fetch articles based on filters
articles = fetch_articles(category_filter=category_filter, limit=limit)

# Display results
if articles:
    df = pd.DataFrame(articles)

    # Clean up missing values just in case
    df["category"] = df["category"].fillna("Uncategorized")

    # Show summary
    st.write(f"Displaying {len(df)} articles")

    # Display table
    st.dataframe(
        df[["id", "title", "url", "category", "category_confidence"]],
        column_config={
            "id": "ID",
            "title": "Article Title",
            "url": st.column_config.LinkColumn("URL"),
            "category": "Category",
            "category_confidence": st.column_config.ProgressColumn(
                "Confidence", format="%.2f", min_value=0, max_value=1
            )
        },
        use_container_width=True
    )
else:
    st.write("No articles found for the selected filter.")

# Footer
st.write("---")
st.caption("Database connection: Railway PostgreSQL")