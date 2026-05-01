import pandas as pd
import xgboost as xgb
import numpy as np

df = pd.read_csv("data/processed/app_features.csv")
mv_rename_map = {col: 'market_value_in_eur' for col in df.columns if 'market' in col.lower() and 'value' in col.lower()}
if mv_rename_map:
    df.rename(columns=mv_rename_map, inplace=True)
df = df.loc[:, ~df.columns.duplicated()].copy()

model = xgb.XGBRegressor()
model.load_model("fairvalue_xgboost.json")
expected_cols = model.feature_names_in_

player_data = df.median(numeric_only=True).to_frame().T
player_data['Contract_Years_Left'] = 2.5
player_data['Age'] = 28
player_data['market_value_in_eur'] = (120 * 1_000_000) / 0.85

X_infer = player_data.reindex(columns=expected_cols, fill_value=0)

dmatrix = xgb.DMatrix(X_infer)
shap_contribs = model.get_booster().predict(dmatrix, pred_contribs=True)[0]

print("Base value:", shap_contribs[-1])
for f, s in zip(expected_cols, shap_contribs[:-1]):
    print(f"{f}: {s}")
