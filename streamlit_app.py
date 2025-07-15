import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
from io import BytesIO
from fonctions import filter_gps_data_by_range  # load_all_gps_files no longer used here
from config import CONFIG

st.set_page_config(page_title="Annan Athletic FC GPS Dashboard ⚽", layout="wide")
st.title("Annan Athletic FC | GPS Dashboard")

# Session file selector
session_files = sorted([f for f in os.listdir(CONFIG["paths"]["gps_data_folder"]) if f.endswith("_details.csv")], reverse=True)
selected_session = st.sidebar.selectbox("Select a Session", session_files)

# Load and clean the selected session file
df = pd.read_csv(os.path.join(CONFIG["paths"]["gps_data_folder"], selected_session))

# Rename and normalize columns
df = df.rename(columns={
    'Player Name': 'Player',
    'Total Distance (m)': 'Total_Distance',
    'Max Speed (km/h)': 'Max_Speed',
    'Speed Zone 1 Distance (m)': 'Speed_Zone_1',
    'Speed Zone 2 Distance (m)': 'Speed_Zone_2',
    'Speed Zone 3 Distance (m)': 'Speed_Zone_3',
    'Speed Zone 4 Distance (m)': 'Speed_Zone_4',
    'Speed Zone 5 Distance (m)': 'Speed_Zone_5',
    'Speed Zone 6 Distance (m)': 'Speed_Zone_6',
    'No. of Sprint (times)': 'Sprints',
    'No. of Exp. Acc. (times)': 'Accelerations',
    'No. of Exp. Dec. (times)': 'Decelerations'
})

# Clean numeric columns
num_cols = ['Total_Distance', 'Max_Speed', 'Speed_Zone_1', 'Speed_Zone_2',
            'Speed_Zone_3', 'Speed_Zone_4', 'Speed_Zone_5', 'Speed_Zone_6',
            'Sprints', 'Accelerations', 'Decelerations']
for col in num_cols:
    if col in df.columns:
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)

# Add date column
df['date'] = pd.to_datetime(selected_session.split(" - ")[1].split("_details")[0], format=CONFIG['date_format'])

data = df

# Sidebar Filters
players = ['All'] + sorted(data['Player'].unique())
selected_player = st.sidebar.selectbox("Select Player", players)

if selected_player != 'All':
    data = data[data['Player'] == selected_player]

# Metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Distance (km)", round(data['Total_Distance'].sum() / 1000, 2))
col2.metric("Max Speed (km/h)", round(data['Max_Speed'].max(), 1))
col3.metric("No. of Sprints", int(data['Sprints'].sum()))
col4.metric("Accelerations / Decelerations", f"{int(data['Accelerations'].sum())} / {int(data['Decelerations'].sum())}")

# Charts
st.subheader("Metrics Over Time")
fig, ax = plt.subplots()
for name, group in data.groupby('Player'):
    ax.plot(group['date'], group['Total_Distance'], label=name)
ax.set_title("Total Distance Over Time")
ax.set_ylabel("Distance (m)")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

fig2, ax2 = plt.subplots()
for name, group in data.groupby('Player'):
    ax2.plot(group['date'], group['Max_Speed'], label=name)
ax2.set_title("Max Speed Over Time")
ax2.set_ylabel("Speed (km/h)")
ax2.set_xlabel("Date")
ax2.legend()
st.pyplot(fig2)

# Speed Zones Summary
st.subheader("Speed Zone Totals")
sz_cols = [f'Speed_Zone_{i}' for i in range(1, 7) if f'Speed_Zone_{i}' in data.columns]
if sz_cols:
    st.bar_chart(data[sz_cols].sum())

# Placeholder for PDF Export
st.subheader("Export Data")
st.info("📄 PDF export coming soon – individual and squad reports will be available.")
