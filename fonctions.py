# --- fonctions.py ---
import os
import pandas as pd
from config import CONFIG

def load_all_gps_files():
    folder = CONFIG["paths"]["gps_data_folder"]
    files = [f for f in os.listdir(folder) if f.endswith("_details.csv")]
    data_frames = []

    for file in files:
        path = os.path.join(folder, file)
        df = pd.read_csv(path)
        df['session_file'] = file
        data_frames.append(df)

    return pd.concat(data_frames, ignore_index=True) if data_frames else pd.DataFrame()
