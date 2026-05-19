import streamlit as st
import pandas as pd
import os
from datetime import datetime, time

# Configuration
BASE_DATA_DIR = r'C:\Users\faizz\OneDrive - MARA Japan Industrial Institute\Desktop\FYP\File for Coding\Pothole project\data'
CSV_PATH = os.path.join(BASE_DATA_DIR, 'datapotholes.csv')
IMAGE_FOLDER = os.path.join(BASE_DATA_DIR, 'images')

st.set_page_config(page_title="Pothole Telemetry System", layout="wide")
st.title("🚧 Multi-Day Road Maintenance Log")

def load_data():
    if os.path.exists(CSV_PATH):
        df = pd.read_csv(CSV_PATH)
        df['timestamp'] = pd.to_datetime(df['timestamp']) #
        # Create separate date and time columns for easier filtering
        df['date'] = df['timestamp'].dt.date
        df['time_only'] = df['timestamp'].dt.time
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # --- SIDEBAR FILTERS ---
    st.sidebar.header("Filter Logs")
    
    # 1. Date Selection
    available_dates = df['date'].unique()
    selected_date = st.sidebar.selectbox("Select Date", options=sorted(available_dates, reverse=True))
    
    # 2. Time Range Selection
    time_range = st.sidebar.slider(
        "Select Time Range",
        value=(time(0, 0), time(23, 59))
    )

    # Filter the dataframe based on user input
    filtered_df = df[
        (df['date'] == selected_date) & 
        (df['time_only'] >= time_range[0]) & 
        (df['time_only'] <= time_range[1])
    ]

    if not filtered_df.empty:
        # Timeline Slider for the filtered results
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
            img_name = event['timestamp'].strftime("%H%M%S") + ".jpg" 
            img_path = os.path.join(IMAGE_FOLDER, img_name) 
            
            if os.path.exists(img_path):
                st.image(img_path, caption=f"Detection at {event['timestamp']}", width='stretch')
            else:
                st.warning(f"File {img_name} not found.")

        with col2:
            st.subheader("Sensor Data")
            st.metric("G-Force", f"{event['z_axis_g']:.2f}g")
            st.write(f"**GPS:** {event['latitude']}, {event['longitude']}")
            st.map(pd.DataFrame({'lat': [event['latitude']], 'lon': [event['longitude']]}))
    else:
        st.warning("No detections found for the selected time range.")
else:
    st.error("Missing data/potholes.csv. Run your tracker or fake data script.")
