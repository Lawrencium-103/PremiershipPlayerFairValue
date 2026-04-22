import pandas as pd
import numpy as np

# A basic historical inflation index for football transfers 
# Base Year: 2024 (Index = 1.00)
# (e.g., fees in 2017 are multiplied by 1.50 to equal 2024 purchasing power)
INFLATION_RATES = {
    2015: 2.10,
    2016: 1.85,
    2017: 1.50, # Pre-Neymar era adjustment
    2018: 1.40,
    2019: 1.35,
    2020: 1.25, # COVID market impact
    2021: 1.20,
    2022: 1.10,
    2023: 1.05,
    2024: 1.00
}

def adjust_for_inflation(df, fee_col='market_value_in_eur', year_col='date'):
    """
    Adjusts past transfer fees or market values to 2024 equivalent.
    Converts EUR to GBP using an approximated flat rate for the MVP.
    """
    df = df.copy()
    
    # Process dates to extract the year
    if df[year_col].dtype == 'object':
        df['Transfer_Year'] = pd.to_datetime(df[year_col]).dt.year
    else:
        df['Transfer_Year'] = df[year_col]
        
    df['Inflation_Multiplier'] = df['Transfer_Year'].map(INFLATION_RATES).fillna(1.0)
    
    # Adjust to 2024 values
    df['Adjusted_Fee_EUR'] = df[fee_col] * df['Inflation_Multiplier']
    
    # Convert EUR to GBP (approx. 0.85 rate)
    df['Transfer_Fee_2024_GBP'] = df['Adjusted_Fee_EUR'] * 0.85
    
    return df

def clean_data(df):
    """
    Handles missing values and basic cleanup.
    """
    # Future specific cleaning logic goes here
    # Example: Impute missing minutes played with 0
    if 'minutes_played' in df.columns:
        df['minutes_played'] = df['minutes_played'].fillna(0)
    return df
