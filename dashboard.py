import streamlit as st
import pandas as pd
import os
from datetime import datetime, time

# --- AUTO-CORRECTING PATH CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 1. List of possible places the CSV could be sitting
possible_csv_paths = [
    os.path.join(BASE_DIR, 'data', 'potholes.csv'),   # Inside data folder
    os.path.join(BASE_DIR, 'potholes.csv'),          # In the main root folder
]

# 2. Automatically find which path actually exists
CSV_PATH = None
for path in possible_csv_paths:
    if os.path.exists(path):
        CSV_PATH = path
        break

# 3. Handle images folder location dynamically
if os.path.exists(os.path.join(BASE_DIR, 'data', 'images')):
    IMAGE_FOLDER = os.path.join(BASE_DIR, 'data', 'images')
else:
    IMAGE_FOLDER = os.path.join(BASE_DIR, 'images')

st.set_page_config(page_title="Pothole Telemetry System", layout="wide")
st.title("🚧 Multi-Day Road Maintenance Log")

# --- DEBUG DISPLAY (Tells us exactly what the AI system found) ---
with st.expander("🔍 Smart Path Finder Details", expanded=False):
    if CSV_PATH:
        st.success(f"✅ Successfully located your file at: `{CSV_PATH}`")
    else:
        st.error("❌ Could not find 'datapothole.csv' anywhere in the workspace.")

def load_data():
    if CSV_PATH and os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp']) 
        df['date'] = df['timestamp'].dt.date
        df['time_only'] = df['timestamp'].dt.time
        return df
    return pd.DataFrame()

df = load_data()

# --- THE MAIN INTERFACE ---
if not df.empty:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Logs")
    
    available_dates = df['date'].unique()
    selected_date = st.sidebar.selectbox("Select Date", options=sorted(available_dates, reverse=True))
    
    time_range = st.sidebar.slider(
        "Select Time Range",
        value=(time(0, 0), time(23, 59))
    )

    filtered_df = df[
        (df['date'] == selected_date) & 
        (df['time_only'] >= time_range[0]) & 
        (df['time_only'] <= time_range[1])
    ]

    if not filtered_df.empty:
        idx = st.select_slider(
            "Navigate Detections (Sorted by Time)",
            options=range(len(filtered_df)),
            format_func=lambda i: filtered_df.iloc[i]['timestamp'].strftime("%H:%M:%S")
        )
        
        event = filtered_df.iloc[idx]
        
        # --- DISPLAY ---
        col1, col2 = st.columns([1.5, 1])
        with col1:
            st.subheader("Visual Evidence")
            # Try matching both time string formats
            img_name = event['timestamp'].strftime("%H%M%S") + ".jpg" 
            img_path = os.path.join(IMAGE_FOLDER, img_name) 
            
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Detection at {event['timestamp']}", width='stretch')
            else:
                st.warning(f"File {img_name} not found in `{IMAGE_FOLDER}`. Make sure your image name matches the time in your CSV.")

        with col2:
            st.subheader("Sensor Data")
            st.metric("G-Force", f"{event['z_axis_g']:.2f}g")
            st.write(f"**GPS:** {event['latitude']}, {event['longitude']}")
            st.map(pd.DataFrame({'lat': [event['latitude']], 'lon': [event['longitude']]}))
    else:
        st.warning("No detections found for the selected time range.")
else:
    st.error("Data file is empty or missing. Please ensure your file contains columns: timestamp, latitude, longitude, z_axis_g.")