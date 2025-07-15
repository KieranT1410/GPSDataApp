# --- streamlit_app.py ---
import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
from io import BytesIO
from config import CONFIG
from fonctions import load_all_gps_files
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
from zipfile import ZipFile
import datetime

st.set_page_config(page_title="Annan Athletic FC GPS Dashboard ⚽", layout="wide")
st.title("Annan Athletic FC | GPS Dashboard")

# Load available GPS session files
session_files = sorted([f for f in os.listdir(CONFIG["paths"]["gps_data_folder"]) if f.endswith("_details.csv")], reverse=True)
selected_session = st.sidebar.selectbox("Select a Session", session_files)

# Load session data
file_path = os.path.join(CONFIG["paths"]["gps_data_folder"], selected_session)
df = pd.read_csv(file_path)
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

# Clean numeric values
for col in df.columns:
    if df[col].dtype == 'object' and df[col].str.replace('.', '', 1).str.replace(',', '').str.isnumeric().any():
        df[col] = df[col].astype(str).str.replace(',', '').astype(float)

players = df['Player'].unique().tolist()
selected_player = st.sidebar.selectbox("Select Player", ['All'] + players)

# Filter player data
data = df if selected_player == 'All' else df[df['Player'] == selected_player]

# Metrics Display
st.subheader("📊 Key Session Metrics")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Distance (km)", round(data['Total_Distance'].sum() / 1000, 2))
col2.metric("Max Speed (km/h)", round(data['Max_Speed'].max(), 1))
col3.metric("Sprints", int(data['Sprints'].sum()))
col4.metric("Accel / Decel", f"{int(data['Accelerations'].sum())} / {int(data['Decelerations'].sum())}")

# Speed Zones
st.subheader("🏃‍♂️ Speed Zone Distances")
sz_cols = [f'Speed_Zone_{i}' for i in range(1, 7)]
st.bar_chart(data[sz_cols].sum(), use_container_width=True)

# Charts - Small size to fit grid layout
st.subheader("📈 Player Comparison Charts")
chart_col1, chart_col2 = st.columns(2)
with chart_col1:
    fig = px.bar(data, x='Player', y='Total_Distance', title='Total Distance by Player', labels={'Total_Distance': 'Distance (m)'})
    fig.update_layout(height=300, margin=dict(t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    fig2 = px.bar(data, x='Player', y='Max_Speed', title='Max Speed by Player', labels={'Max_Speed': 'Speed (km/h)'})
    fig2.update_layout(height=300, margin=dict(t=30, b=10))
    st.plotly_chart(fig2, use_container_width=True)

# PDF Export
st.subheader("📄 Export Reports")

def generate_pdf(player_df, player_name):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph(f"GPS Report - {player_name}", styles['Title'])]

    for col in ['Total_Distance', 'Max_Speed', 'Sprints', 'Accelerations', 'Decelerations']:
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"{col.replace('_', ' ')}: {round(player_df[col].values[0], 2)}", styles['Normal']))

    doc.build(story)
    buffer.seek(0)
    return buffer

if selected_player != 'All':
    pdf = generate_pdf(data, selected_player)
    st.download_button("📅 Download Player Report", data=pdf, file_name=f"{selected_player}_Report.pdf")
else:
    if st.button("📦 Download All Reports as ZIP"):
        zip_buffer = BytesIO()
        with ZipFile(zip_buffer, "a") as zipf:
            for player in df['Player'].unique():
                player_df = df[df['Player'] == player]
                pdf = generate_pdf(player_df, player)
                zipf.writestr(f"{player}_Report.pdf", pdf.read())
        zip_buffer.seek(0)
        st.download_button("📅 Download ZIP of All Reports", data=zip_buffer, file_name="All_Player_Reports.zip")
