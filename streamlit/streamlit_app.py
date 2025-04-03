import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import psycopg


# Get the database connection string from .env
dbconn = st.secrets["DB_CONN"]

# Verify if the connection string is loaded correctly
if dbconn is None:
    st.error("Database connection string not found. Please check your .env file.")
else:
    st.write("Database connection string loaded successfully!")

@st.cache_data
def load_data(table_name):
    """Load data from the PostgreSQL database."""
    try:
        with psycopg.connect(dbconn) as conn:
            query = f"SELECT * FROM {table_name} ORDER BY date DESC;"
            df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# User input for data selection
st.subheader("Select Forex Data")
data_type = st.selectbox("Choose currency pair", ["INR to EUR"])

# Map the selection to table names
table_name = "forex_data" if data_type == "INR to EUR" else "forex_data_inr"

# Load the data from Railway PostgreSQL
df = load_data(table_name)

# Check if data is loaded
if df.empty:
    st.warning("No data available. Please check your database.")
else:
    # Data preview
    st.subheader(f"Data Preview: {data_type}")
    st.dataframe(df.head())

    # User input for visualization
    st.subheader("Choose Visualization")
    chart_type = st.selectbox("Select chart type", ["Line Chart", "Bar Chart"])

    # Plot the selected chart
    fig, ax = plt.subplots()

    if chart_type == "Line Chart":
        ax.plot(df['date'], df['close'], label='Close Price', marker='o')
        ax.set_title(f"{data_type} - Daily Close Prices")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price")
        ax.grid(True)

    elif chart_type == "Bar Chart":
        ax.bar(df['date'], df['close'], label='Close Price')
        ax.set_title(f"{data_type} - Daily Close Prices")
        ax.set_xlabel("Date")
        ax.set_ylabel("Close Price")
        ax.grid(True)

    st.pyplot(fig)