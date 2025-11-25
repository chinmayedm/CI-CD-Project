import streamlit as st
import pandas as pd
import time
import plotly.express as px
from datetime import datetime, timedelta
import os

# Configuration
st.set_page_config(
    page_title="🚨 SIEM Anomaly Dashboard",
    layout="wide",
    page_icon="🛡️"
)

# Constants
REFRESH_INTERVAL = 5  # seconds
CSV_PATH = "alerts.csv"

# Sample data matching your format
SAMPLE_DATA = """Timestamp,Sample Index,VAE Score,GNN Label
2025-04-09 16:25:26.985832,2,310.7619,1
2025-04-09 16:25:26.986833,3,310.91617,1
2025-04-09 16:25:26.988834,4,311.12512,1
2025-04-09 16:25:26.988834,5,311.36285,1
2025-04-09 16:25:26.989854,6,311.65887,1
2025-04-09 16:25:26.991138,7,311.98508,1
2025-04-09 16:29:57.548820,0,310.5807800292969,1
2025-04-09 16:29:58.552840,1,310.6549987792969,1
2025-04-09 16:29:59.558027,2,310.76190185546875,1
2025-04-09 16:30:00.561436,3,310.91619873046875,1
2025-04-09 16:30:01.637557,4,311.1253356933594,1
2025-04-09 16:30:02.643728,5,311.3636474609375,1
2025-04-09 16:30:03.647736,6,311.6578063964844,1
2025-04-09 16:41:31.674115,0,310.5807800292969,1
2025-04-09 16:41:32.676806,1,310.6549987792969,1
2025-04-09 16:41:33.689518,2,310.7618713378906,1
2025-04-09 16:41:34.693096,3,310.9161376953125,1
2025-04-09 16:41:35.695667,4,311.1254577636719,1
2025-04-09 16:41:36.697732,5,311.3625183105469,1
2025-04-09 16:41:37.700866,6,311.6585388183594,1
"""

def initialize_sample_data():
    """Create sample data file if it doesn't exist"""
    if not os.path.exists(CSV_PATH):
        with open(CSV_PATH, 'w') as f:
            f.write(SAMPLE_DATA)

@st.cache_data(ttl=REFRESH_INTERVAL)
def load_data():
    """Load and preprocess the data"""
    try:
        df = pd.read_csv(CSV_PATH)
        
        # Clean column names
        df.columns = df.columns.str.strip().str.replace(" ", "_")
        
        # Convert timestamp
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        
        # Add human-readable columns
        df['Time_Ago'] = df['Timestamp'].apply(
            lambda x: str(datetime.now() - x).split('.')[0] + " ago"
        )
        
        # Add severity classification based on VAE Score
        df['Severity'] = pd.cut(
            df['VAE_Score'],
            bins=[0, 310, 311, 312, float('inf')],
            labels=['Low', 'Medium', 'High', 'Critical']
        )
        
        return df.sort_values('Timestamp', ascending=False)
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

def main():
    initialize_sample_data()
    st.title("🚨 SIEM Anomaly Dashboard")
    st.markdown("### Real-time monitoring of anomaly scores")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available. Waiting for alerts...")
        time.sleep(REFRESH_INTERVAL)
        st.rerun()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter Controls")
    
    # Time range filter
    time_range = st.sidebar.selectbox(
        "Time Range",
        options=["Last 15 minutes", "Last hour", "Last 6 hours", "Last 24 hours", "All time"],
        index=1
    )
    
    # Convert time range to datetime
    now = datetime.now()
    if time_range == "Last 15 minutes":
        cutoff = now - timedelta(minutes=15)
    elif time_range == "Last hour":
        cutoff = now - timedelta(hours=1)
    elif time_range == "Last 6 hours":
        cutoff = now - timedelta(hours=6)
    elif time_range == "Last 24 hours":
        cutoff = now - timedelta(hours=24)
    else:
        cutoff = df['Timestamp'].min()
    
    # Score filter
    min_score, max_score = st.sidebar.slider(
        "VAE Score Range",
        min_value=float(df['VAE_Score'].min()),
        max_value=float(df['VAE_Score'].max()),
        value=(310.0, 312.0),
        step=0.1
    )
    
    # Severity filter
    severity_filter = st.sidebar.multiselect(
        "Severity Levels",
        options=df['Severity'].unique(),
        default=df['Severity'].unique()
    )
    
    # Label filter
    label_filter = st.sidebar.radio(
        "Anomaly Status",
        options=["All", "Normal (0)", "Anomaly (1)"],
        index=0
    )
    
    # Apply filters
    filtered_df = df[
        (df['Timestamp'] >= cutoff) &
        (df['VAE_Score'] >= min_score) &
        (df['VAE_Score'] <= max_score) &
        (df['Severity'].isin(severity_filter))
    ]
    
    if label_filter == "Normal (0)":
        filtered_df = filtered_df[filtered_df['GNN_Label'] == 0]
    elif label_filter == "Anomaly (1)":
        filtered_df = filtered_df[filtered_df['GNN_Label'] == 1]
    
    # Dashboard Metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Alerts", len(df))
    with col2:
        st.metric("Filtered Alerts", len(filtered_df))
    with col3:
        avg_score = filtered_df['VAE_Score'].mean() if not filtered_df.empty else 0
        st.metric("Average VAE Score", f"{avg_score:.2f}")
    with col4:
        if not filtered_df.empty:
            latest = filtered_df.iloc[0]
            st.metric("Latest Alert", f"Score: {latest['VAE_Score']:.2f}")
    
    # Visualization Section
    st.markdown("---")
    st.subheader("📊 Anomaly Score Trends")
    
    if not filtered_df.empty:
        # Time series chart
        fig = px.line(
            filtered_df,
            x='Timestamp',
            y='VAE_Score',
            color='Severity',
            title='VAE Scores Over Time',
            hover_data=['Sample_Index', 'GNN_Label', 'Time_Ago'],
            color_discrete_map={
                'Low': 'green',
                'Medium': 'orange',
                'High': 'red',
                'Critical': 'purple'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Score distribution
        col1, col2 = st.columns(2)
        with col1:
            fig = px.histogram(
                filtered_df,
                x='VAE_Score',
                nbins=20,
                title='Score Distribution',
                color='Severity'
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            fig = px.box(
                filtered_df,
                y='VAE_Score',
                title='Score Statistics',
                color='Severity'
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Alert Table
    st.markdown("---")
    st.subheader("🔍 Detailed Alerts")
    
    if not filtered_df.empty:
        # Format display columns
        display_cols = ['Timestamp', 'Time_Ago', 'Sample_Index', 'VAE_Score', 'Severity', 'GNN_Label']
        display_df = filtered_df[display_cols].copy()
        display_df['VAE_Score'] = display_df['VAE_Score'].apply(lambda x: f"{x:.4f}")
        display_df['Timestamp'] = display_df['Timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        
        # Color coding
        def color_alert(row):
            color = '#FFCCCC' if row['GNN_Label'] == 1 else '#CCFFCC'
            return [f'background-color: {color}' for _ in row]
        
        st.dataframe(
            display_df.style.apply(color_alert, axis=1),
            use_container_width=True,
            height=600,
            hide_index=True
        )
    else:
        st.warning("No alerts match your filters")
    
    # Auto-refresh
    st.caption(f"🔄 Auto-refreshing in {REFRESH_INTERVAL} seconds...")
    time.sleep(REFRESH_INTERVAL)
    st.rerun()

if __name__ == "__main__":
    main()