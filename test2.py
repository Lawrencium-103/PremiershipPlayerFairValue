import pandas as pd
import xgboost as xgb

df = pd.read_csv("data/processed/app_features.csv")
model = xgb.XGBRegressor()
model.load_model("fairvalue_xgboost.json")
expected_cols = model.feature_names_in_

print("Expected cols:")
print(expected_cols[:5])

# Find name column
name_col = next((c for c in ['name', 'name_x', 'Player_Name', 'Name'] if c in df.columns), None)
print("Name col:", name_col)
if name_col:
    print("Bruno matches:", df[df[name_col].astype(str).str.contains("bruno fern", case=False, na=False)][name_col].tolist())

med = df.median(numeric_only=True).to_frame().T
missing = [c for c in expected_cols if c not in med.columns]
print(f"Missing from median: {len(missing)} out of {len(expected_cols)}")
if len(missing) > 0:
    print("First 5 missing:", missing[:5])
