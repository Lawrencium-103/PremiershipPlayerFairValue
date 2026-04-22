import pandas as pd
import numpy as np

# Mock UEFA Coefficients for League Strength Indexing
# In a full production environment, this would be dynamically loaded
LEAGUE_COEFFICIENTS = {
    'Premier League': 1.0,
    'LaLiga': 0.90,
    'Serie A': 0.85,
    'Bundesliga': 0.82,
    'Ligue 1': 0.75,
    'Eredivisie': 0.60,
    'Liga Portugal': 0.55
}

def calculate_risk_score(df, contract_col='Contract_Years_Left', age_col='Age', injury_col='Injury_Days_Total_24m'):
    """
    Computes binary risk flags based on the project blueprint for "The Busquets Factor".
    """
    df = df.copy()
    
    # 1. Contract Risk: Entering final 12-18 months
    if contract_col in df.columns:
        df['Risk_Contract'] = np.where(df[contract_col] < 1.5, 1, 0)
    else:
        df['Risk_Contract'] = 0
        
    # 2. Age Risk: Over 30 years old
    if age_col in df.columns:
        df['Risk_Age'] = np.where(df[age_col] > 30, 1, 0)
    else:
        df['Risk_Age'] = 0
        
    # 3. Injury Risk: Missed significant time (e.g., > 60 days)
    if injury_col in df.columns:
        df['Risk_Injury'] = np.where(df[injury_col] > 60, 1, 0)
    else:
        df['Risk_Injury'] = 0
        
    # Aggregate Score [0 to 3]
    df['Total_Risk_Score'] = df['Risk_Contract'] + df['Risk_Age'] + df['Risk_Injury']
    
    return df

def calculate_league_index(df, league_col='Current_League'):
    """
    Applies the League Strength multiplier based on UEFA coefficients.
    """
    df = df.copy()
    if league_col in df.columns:
        df['League_Index'] = df[league_col].map(LEAGUE_COEFFICIENTS).fillna(0.4) # Default tier 3
    return df

def encode_categorical_features(df, position_col='Position', nationality_tier_col='Nationality_Tier'):
    """
    Performs One-Hot Encoding for positions and handles Nationality Tiers.
    """
    df = df.copy()
    if position_col in df.columns:
        # Prevent completely exploding dimensions if many obscure positions exist
        df = pd.get_dummies(df, columns=[position_col], prefix='Pos')
        
    if nationality_tier_col in df.columns:
        # e.g., Tier 1 = EU5/SA, Tier 2 = Rest of World
        df[nationality_tier_col] = df[nationality_tier_col].astype(int)
        
    return df

def build_all_features(df):
    """
    Orchestrates the feature engineering pipeline.
    """
    df = calculate_risk_score(df)
    df = calculate_league_index(df)
    df = encode_categorical_features(df)
    return df
