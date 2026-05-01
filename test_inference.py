import pandas as pd
import xgboost as xgb
import numpy as np

# Load data and model
df = pd.read_csv("data/processed/app_features.csv")

mv_rename_map = {col: 'market_value_in_eur' for col in df.columns if 'market' in col.lower() and 'value' in col.lower()}
if mv_rename_map:
    df.rename(columns=mv_rename_map, inplace=True)
df = df.loc[:, ~df.columns.duplicated()].copy()

model = xgb.XGBRegressor()
model.load_model("fairvalue_xgboost.json")
expected_cols = model.feature_names_in_

name_col = next((c for c in ['name', 'name_x', 'Player_Name', 'Name'] if c in df.columns), None)

print("Name Col:", name_col)
print("Is Bruno in df?", "Bruno Fernandes" in df[name_col].astype(str).tolist())

player_data = df[df[name_col].astype(str) == "Bruno Fernandes"].iloc[0:1].copy() if name_col else df.median().to_frame().T

print("Pre-update market_value_in_eur:", player_data.get('market_value_in_eur', pd.Series([None])).iloc[0])

player_data['Contract_Years_Left'] = 2.5
player_data['Age'] = 28
player_data['market_value_in_eur'] = (120 * 1_000_000) / 0.85

print("Post-update market_value_in_eur:", player_data['market_value_in_eur'].iloc[0])

X_infer = player_data.reindex(columns=expected_cols, fill_value=0)

print("X_infer expected length:", len(expected_cols))
print("Any missing cols?", [c for c in expected_cols if c not in player_data.columns])

preds = model.predict(X_infer)
print("Raw pred:", preds[0])
print("Exp PV:", np.expm1(preds[0]))

dmatrix = xgb.DMatrix(X_infer)
shap_vals = model.get_booster().predict(dmatrix, pred_contribs=True)[0]
print("SHAP max / min:", shap_vals.max(), shap_vals.min())

