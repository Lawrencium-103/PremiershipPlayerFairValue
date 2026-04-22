import kagglehub
import pandas as pd
import os
import shutil

def download_datasets():
    """
    Downloads the Transfermarkt dataset and an FBref dataset.
    """
    print("Downloading Transfermarkt dataset...")
    tm_path = kagglehub.dataset_download("davidcariboo/player-scores")
    print(f"Transfermarkt dataset downloaded locally to {tm_path}")
    
    print("Downloading FBref dataset...")
    try:
        # Using a popular FBref Kaggle dataset for advanced metrics
        fb_path = kagglehub.dataset_download("vivovinco/20222023-football-player-stats")
        print(f"FBref dataset downloaded locally to {fb_path}")
    except Exception as e:
        print(f"Warning: Could not download FBref dataset: {e}")
        fb_path = None
        
    return tm_path, fb_path

def load_data(tm_path, fb_path):
    """
    Loads necessary csv files into pandas DataFrames.
    """
    # Transfermarkt data
    players_path = os.path.join(tm_path, "players.csv")
    appearances_path = os.path.join(tm_path, "appearances.csv")
    player_valuations_path = os.path.join(tm_path, "player_valuations.csv")

    players_df = pd.read_csv(players_path)
    appearances_df = pd.read_csv(appearances_path)
    
    valuations_df = None
    if os.path.exists(player_valuations_path):
        valuations_df = pd.read_csv(player_valuations_path)
    
    # FBref data
    fbref_df = None
    if fb_path and os.path.exists(fb_path):
        for file in os.listdir(fb_path):
            if file.endswith('.csv'):
                # Many FBref datasets use latin1 encoding
                fbref_df = pd.read_csv(os.path.join(fb_path, file), encoding='latin1', low_memory=False)
                break
                
    return players_df, appearances_df, valuations_df, fbref_df

def get_base_datasets(stage_locally=True):
    """Downloads and returns all dataframes, optionally staging them locally."""
    tm_path, fb_path = download_datasets()
    
    if stage_locally:
        print("Staging datasets into local data/raw directory...")
        # Get absolute path relative to project root
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        tm_raw_dir = os.path.join(project_root, "data", "raw", "transfermarkt")
        fb_raw_dir = os.path.join(project_root, "data", "raw", "fbref")
        
        os.makedirs(tm_raw_dir, exist_ok=True)
        os.makedirs(fb_raw_dir, exist_ok=True)
        
        for f in os.listdir(tm_path):
            if f.endswith('.csv'):
                shutil.copy(os.path.join(tm_path, f), tm_raw_dir)
                
        if fb_path and os.path.exists(fb_path):
            for f in os.listdir(fb_path):
                if f.endswith('.csv'):
                    shutil.copy(os.path.join(fb_path, f), fb_raw_dir)
                    
        print(f"Data staged successfully into {os.path.join(project_root, 'data', 'raw')}.")
        
    return load_data(tm_path, fb_path)

if __name__ == "__main__":
    players, apps, valuations, fbref = get_base_datasets()
    
    print("\n--- Data Loading Summary ---")
    print(f"Loaded {len(players)} Transfermarkt players.")
    print(f"Loaded {len(apps)} match appearances.")
    if valuations is not None:
        print(f"Loaded {len(valuations)} transfer valuations.")
    if fbref is not None:
        print(f"Loaded {len(fbref)} FBref player records with advanced metrics like xG and xA.")
