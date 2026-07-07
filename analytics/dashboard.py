import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Configure absolute storage resolution points matching backend setups
DATA_PATH = "../storage/data/analytics.csv"

# Establish professional application dashboard styling defaults
st.set_page_config(
    page_title="FreeSongs Platform Metrics Engine",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Header Section
st.title("📊 FreeSongs Platform Telemetry Indicators")
st.markdown("---")

# Verify raw analytics time-series files exist before compiling layout charts
if os.path.exists(DATA_PATH):
    try:
        # Load telemetry framework variables
        df = pd.read_csv(DATA_PATH)
        
        # Guard against zero interaction edge cases
        if df.empty:
            st.info("📊 Ingestion logs are currently blank. Stream or download music tracks on your platform to populate metrics.")
        else:
            # Clean data mappings safely
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # --- SIDEBAR INTERACTIVE TIMELINE SELECTOR CONTROLS ---
            st.sidebar.header("⏱️ Analytics Control Filter")
            time_filter = st.sidebar.selectbox(
                "Select Aggregation Window Profile:",
                options=["All-Time Data", "Last 24 Hours", "Last 7 Days", "Last 30 Days"]
            )
            
            # Compute timeline delta mappings matching Day 9 backend requirements
            now = pd.Timestamp.now()
            if time_filter == "Last 24 Hours":
                df = df[df['timestamp'] >= (now - pd.Timedelta(days=1))]
            elif time_filter == "Last 7 Days":
                df = df[df['timestamp'] >= (now - pd.Timedelta(days=7))]
            elif time_filter == "Last 30 Days":
                df = df[df['timestamp'] >= (now - pd.Timedelta(days=30))]

            # --- TOP LEVEL TOTAL METRIC SCORE CARDS ---
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(label="Total Platform Engagements", value=len(df))
            with col2:
                streams_count = len(df[df['action'] == 'stream'])
                st.metric(label="Total Async Streams played", value=streams_count)
            with col3:
                downloads_count = len(df[df['action'] == 'download'])
                st.metric(label="Total Binary File Downloads", value=downloads_count)
                
            st.markdown("### 📈 Trajectory and Asset Distribution Metrics")
            chart_col1, chart_col2 = st.columns(2)
            
            # --- CHART 1: TOP TRACKS BAR CHART ---
            with chart_col1:
                st.subheader("🎵 Top 5 Most Popular Audio Assets")
                top_tracks = df['song_name'].value_counts().head(5)
                if not top_tracks.empty:
                    st.bar_chart(top_tracks, color="#1DB954") # Premium Spotify Green shade hex accent
                else:
                    st.write("No asset distribution logs in this target window profile.")
                    
            # --- CHART 2: INTERACTION TIME-SERIES TIMELINE LINE CHART ---
            with chart_col2:
                st.subheader("🕒 Platform Activity Trajectory over Time")
                # Extract chronological hours to monitor heavy streaming peaks
                df['Hour'] = df['timestamp'].dt.to_period('H').astype(str)
                time_trend = df.groupby('Hour').size()
                if not time_trend.empty:
                    st.line_chart(time_trend, color="#FF4B4B")
                else:
                    st.write("No timeline tracking signatures in this target window profile.")

            # --- AUDITABLE INTERACTIVE LOG AGGREGATION VIEW ---
            st.markdown("---")
            st.subheader("📋 Raw Transaction Monitoring Audit Logs")
            st.dataframe(
                df.sort_values(by="timestamp", ascending=False), 
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"Failed to mount interactive visualization layer dashboard parameters: {str(e)}")
else:
    # Handle zero transaction logging cold-start edge cases gracefully
    st.warning("⚠️ Telemetry pipeline data source missing. Run server interactions to generate '../storage/data/analytics.csv' data structures.")