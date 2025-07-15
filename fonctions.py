import os
import pandas as pd
from config import CONFIG

def load_all_gps_files():
    folder = CONFIG["paths"]["gps_data_folder"]
    if not os.path.exists(folder):
        return pd.DataFrame()

    files = [f for f in os.listdir(folder) if f.endswith("_details.csv")]
    all_data = []
    for file in files:
        try:
            date_str = file.split(" - ")[1].split("_details")[0]
            date = pd.to_datetime(date_str, format=CONFIG['date_format'])
            df = pd.read_csv(os.path.join(folder, file))
            df['date'] = date

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

            num_cols = ['Total_Distance', 'Max_Speed', 'Speed_Zone_1', 'Speed_Zone_2',
                        'Speed_Zone_3', 'Speed_Zone_4', 'Speed_Zone_5', 'Speed_Zone_6',
                        'Sprints', 'Accelerations', 'Decelerations']
            for col in num_cols:
                if col in df.columns:
                    df[col] = df[col].astype(str).str.replace(',', '').astype(float)

            all_data.append(df[['date', 'Player'] + num_cols])

        except Exception as e:
            print(f"Error loading {file}: {e}")
    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def filter_gps_data_by_range(data, range_type):
    today = pd.Timestamp.today()
    if range_type == '7 days':
        start = today - pd.Timedelta(days=7)
    elif range_type == '14 days':
        start = today - pd.Timedelta(days=14)
    elif range_type == '30 days':
        start = today - pd.Timedelta(days=30)
    else:
        start = data['date'].min()
    return data[data['date'] >= start]
