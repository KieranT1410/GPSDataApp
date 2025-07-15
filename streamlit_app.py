import streamlit as st
import pandas as pd
import os
from fonctions import load_all_gps_files, filter_gps_data_by_range
from config import CONFIG
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Annan Athletic FC GPS Dashboard ⚽", layout="wide")
st.title("Annan Athletic FC | GPS Dashboard")

# Load Data
data = load_all_gps_files()

# Sidebar Filters
players = ['All'] + sorted(data['Player'].unique())
selected_player = st.sidebar.selectbox("Select Player", players)
date_range = st.sidebar.radio("Date Range", ['7 days', '14 days', '30 days', 'All'])

# Filtered Data
filtered_data = filter_gps_data_by_range(data, date_range)
if selected_player != 'All':
    filtered_data = filtered_data[filtered_data['Player'] == selected_player]

# Metrics
st.subheader("Key Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Distance (km)", round(filtered_data['Total_Distance'].sum() / 1000, 2))
col2.metric("Max Speed (km/h)", round(filtered_data['Max_Speed'].max(), 1))
col3.metric("No. of Sprints", int(filtered_data['Sprints'].sum()))
col4.metric("Accelerations / Decelerations", f"{int(filtered_data['Accelerations'].sum())} / {int(filtered_data['Decelerations'].sum())}")

# Charts
st.subheader("Metrics Over Time")
fig, ax = plt.subplots()
for name, group in filtered_data.groupby('Player'):
    ax.plot(group['date'], group['Total_Distance'], label=name)
ax.set_title("Total Distance Over Time")
ax.set_ylabel("Distance (m)")
ax.set_xlabel("Date")
ax.legend()
st.pyplot(fig)

fig2, ax2 = plt.subplots()
for name, group in filtered_data.groupby('Player'):
    ax2.plot(group['date'], group['Max_Speed'], label=name)
ax2.set_title("Max Speed Over Time")
ax2.set_ylabel("Speed (km/h)")
ax2.set_xlabel("Date")
ax2.legend()
st.pyplot(fig2)

# Speed Zones Summary
st.subheader("Speed Zone Totals")
sz_cols = [f'Speed_Zone_{i}' for i in range(1, 7)]
st.bar_chart(filtered_data[sz_cols].sum())

# Download
st.subheader("Export Data")
buffer = BytesIO()
filtered_data.to_excel(buffer, index=False)
buffer.seek(0)
st.download_button("Download Excel Report", buffer, file_name="gps_report.xlsx")
