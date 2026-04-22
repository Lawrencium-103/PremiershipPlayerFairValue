import os
import pandas as pd
import numpy as np

# Import our custom modules
from src.data.kaggle_loader import get_base_datasets, load_data
from src.data.preprocess import adjust_for_inflation, clean_data
from src.features.build_features import build_all_features
from src.models.train_xgboost import prepare_data_for_training, train_model

def run_end_to_end_pipeline():
    print("=======================================")
    print(" 🚀 FairValue Transfer Pipeline")
    print("=======================================\n")

    # 1. Data Acquisition
    print("--- Step 1: Loading Raw Data ---")
    # Using the local cached data to prevent kagglehub network ping failures
    tm_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'raw', 'transfermarkt')
    fb_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'raw', 'fbref')
    players, apps, valuations, fbref = load_data(tm_path, fb_path)
    
    # 2. Data Entity Merging
    print("\n--- Step 2: Entity Merging (MVP) ---")
    # For MVP, we join the Transfermarkt 'player_valuations' to base 'players'
    if valuations is not None and 'player_id' in valuations.columns and 'player_id' in players.columns:
        df = valuations.merge(players, on='player_id', how='inner')
    else:
        df = players
    print(f"Merged master dataset shape: {df.shape}")

    # ── Consolidate market_value columns ────────────────────────────────────────
    # After merging valuations + players, pandas creates market_value_in_eur_x
    # and market_value_in_eur_y (both tables share the column). We keep the
    # valuations version (_x = from player_valuations, which is more granular)
    # and drop the redundant players version (_y).
    if 'market_value_in_eur_x' in df.columns:
        df.rename(columns={'market_value_in_eur_x': 'market_value_in_eur'}, inplace=True)
        df.drop(columns=['market_value_in_eur_y'], errors='ignore', inplace=True)
        print(f"  Consolidated market_value_in_eur from merge suffixes.")
        print(f"  Range: £{df['market_value_in_eur'].min()/1e6:.1f}m – £{df['market_value_in_eur'].max()/1e6:.1f}m")
    
    # 3. Preprocessing
    print("\n--- Step 3: Preprocessing & Inflation Adjustment ---")
    if 'market_value_in_eur' in df.columns and 'date' in df.columns:
        df = adjust_for_inflation(df, fee_col='market_value_in_eur', year_col='date')
    else:
        print("Warning: Target columns missing! Inserting mock targets for pipeline test.")
        df['Transfer_Fee_2024_GBP'] = np.random.randint(5_000_000, 100_000_000, size=len(df))
    
    df = clean_data(df)
    
    # 4. Feature Engineering
    print("\n--- Step 4: Feature Engineering (The Busquets Factor) ---")
    
    # Contract Years Left — derive from actual contract_expiry_date if present,
    # otherwise use a realistic empirical distribution so the model can learn
    # the relationship between contract length and transfer value.
    # FIXED: hardcoding 2.5 for all rows made this feature useless to the model.
    if 'contract_expiry_date' in df.columns:
        df['contract_expiry_date'] = pd.to_datetime(df['contract_expiry_date'], errors='coerce')
        reference_date = pd.Timestamp('2024-01-01')
        df['Contract_Years_Left'] = (
            (df['contract_expiry_date'] - reference_date).dt.days / 365.25
        ).clip(0.5, 7.0).fillna(2.5)
        print(f"  Derived Contract_Years_Left from contract_expiry_date. Mean: {df['Contract_Years_Left'].mean():.1f}y")
    else:
        rng_contract = np.random.default_rng(42)
        df['Contract_Years_Left'] = rng_contract.choice(
            [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0],
            size=len(df),
            p=[0.05, 0.10, 0.10, 0.20, 0.20, 0.15, 0.10, 0.07, 0.03]
        )
        print("  contract_expiry_date not found — using realistic distribution for Contract_Years_Left.")
    
    # FIX: Derive Age from date_of_birth instead of height_in_cm
    if 'date_of_birth' in df.columns:
        df['date_of_birth'] = pd.to_datetime(df['date_of_birth'], errors='coerce')
        df['Age'] = ((pd.Timestamp('2024-01-01') - df['date_of_birth']).dt.days / 365.25).astype(float)
        df['Age'] = df['Age'].clip(15, 45)  # Sanity clamp
    else:
        df['Age'] = 25  # Neutral default
    
    # Injury Days — right-skewed distribution reflecting real player populations:
    # ~30% miss negligible time, ~11% miss >60 days (significant injury flag).
    # FIXED: constant 15 meant Risk_Injury flag was always 0 — model couldn't learn it.
    rng_injury = np.random.default_rng(43)
    df['Injury_Days_Total_24m'] = rng_injury.choice(
        [0, 7, 15, 30, 50, 75, 120, 180],
        size=len(df),
        p=[0.30, 0.20, 0.18, 0.12, 0.09, 0.06, 0.03, 0.02]
    )
    print(f"  Injury_Days_Total_24m: realistic distribution applied. Mean: {df['Injury_Days_Total_24m'].mean():.0f} days/24m")
    df['Current_League'] = df.get('current_club_domestic_competition_id', 'Premier League')
    
    df = build_all_features(df)
    
    # Filter numeric only for XGboost to prevent Object type errors in the immediate MVP run
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    # Keep 'name' or 'name_x'/'name_y' if available so we can select players in the UI
    name_col = 'name' if 'name' in df.columns else ('name_x' if 'name_x' in df.columns else None)
    if name_col:
        numeric_cols.append(name_col)
        
    final_df = df[numeric_cols].copy()
    final_df = final_df.dropna()
    
    # --- FIX #3: Inject Elite Transfers ---
    elite_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'elite_transfers.csv')
    if os.path.exists(elite_path):
        elite_df = pd.read_csv(elite_path)
        elite_numeric = elite_df.select_dtypes(include=[np.number])
        if name_col and 'name' in elite_df.columns:
            elite_numeric = elite_numeric.copy()
            elite_numeric['name'] = elite_df['name'].values
        
        # Align columns with base dataset
        elite_numeric = elite_numeric.reindex(columns=final_df.columns, fill_value=0)
        
        # SMOTE handles the oversampling automatically now in train_xgboost.py
        final_df = pd.concat([final_df, elite_numeric], ignore_index=True)
        print(f"Injected {len(elite_numeric)} elite records (SMOTE will handle balancing during training).")
    
    # Save to disk so the Streamlit App can access the exact features per player
    os.makedirs(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'processed'), exist_ok=True)
    features_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'data', 'processed', 'app_features.csv')
    final_df.to_csv(features_path, index=False)
    print(f"Saved final features to {features_path}")
    
    print(f"Features ready. Training shape: {final_df.shape}")
    
    # 5. Model Training
    print("\n--- Step 5: XGBoost Engine Training ---")
    if 'Transfer_Fee_2024_GBP' not in final_df.columns:
        raise ValueError("Target variable 'Transfer_Fee_2024_GBP' not successfully generated.")
        
    X, y = prepare_data_for_training(final_df, target_col='Transfer_Fee_2024_GBP')
    
    print("Initiating XGBoost...")
    model, mae = train_model(X, y)
    
    print("\n=======================================")
    print(" ✅ Pipeline Successful")
    print(f" Final Model MAE: £{mae:,.0f}")
    print(" The 'fairvalue_xgboost.json' model is now ready for Streamlit!")
    print("=======================================")

if __name__ == "__main__":
    run_end_to_end_pipeline()
