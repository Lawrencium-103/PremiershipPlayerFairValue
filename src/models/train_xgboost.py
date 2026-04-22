import xgboost as xgb
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.metrics import mean_absolute_error, mean_squared_error


def prepare_data_for_training(df, target_col='Transfer_Fee_2024_GBP'):
    """
    Separates features from target and applies log1p to the target.

    Design decision — market_value_in_eur:
    ────────────────────────────────────────
    Previous code dropped this as "leaky". That was wrong for our use case:

    TRUE leakage = using the SAME transfer's fee data during training
    (e.g. Adjusted_Fee_EUR, Transfer_Fee_EUR from the same record).

    market_value_in_eur is NOT leaky because:
      1. It is a published, pre-transfer datapoint every club already knows.
      2. In the app, users explicitly enter their market value estimate.
      3. Without it, the model cannot distinguish Mbappe from a League Two
         player — all predictions collapse to the population median (~£40m).
      4. The model should learn the RELATIONSHIP between market value and
         actual transfer fee (premiums/discounts), not pretend MV doesn't exist.

    ACTUALLY leaky columns are only those derived from the same transfer record:
      - Transfer_Fee_EUR, Adjusted_Fee_EUR, Inflation_Multiplier, Transfer_Year
    """
    X = df.drop(
        columns=[
            target_col, 'Player_ID', 'Name', 'name', 'name_x', 'name_y',
            'Transfer_Date', 'Adjusted_Fee_EUR', 'Inflation_Multiplier',
            'Transfer_Year', 'player_id'
        ],
        errors='ignore'
    )

    # Drop only same-transaction fee history — NOT market_value_in_eur
    truly_leaky = [
        c for c in X.columns
        if ('fee' in c.lower() and 'transfer' in c.lower())   # e.g. Transfer_Fee_EUR
        or ('adjusted' in c.lower() and 'fee' in c.lower())   # e.g. Adjusted_Fee_EUR
    ]
    X = X.drop(columns=truly_leaky, errors='ignore')

    print(f"  Training features ({len(X.columns)}): {sorted(X.columns.tolist())}")
    if 'market_value_in_eur' in X.columns:
        print("  ✅ market_value_in_eur INCLUDED — elite player differentiation enabled.")
    else:
        print("  ⚠️  market_value_in_eur NOT FOUND in dataset — check pipeline renaming.")

    y = np.log1p(df[target_col])
    return X, y


def compute_sample_weights(y_log):
    """
    Industry-standard approach to handle transfer fee class imbalance.

    Replaces SMOTE-for-regression, which introduced synthetic noise:
      - SMOTE was designed for classification, not regression
      - Discretising log-price into bins and re-interpolating targets
        introduces distributional artifacts that hurt generalisation
      - XGBoost's native sample_weight is cleaner, faster, and more principled

    sample_weight tells XGBoost "getting this prediction right matters more".
    It does NOT create fake data — it simply re-weights gradient updates.

    Tier thresholds (2024 GBP equivalent):
      Elite:     > £60m    → weight 5.0   (Bellingham, Haaland tier)
      High:      £25–60m   → weight 2.5   (Premier League regulars)
      Mid:       £5–25m    → weight 1.5   (Championship / squad depth)
      Standard:  < £5m     → weight 1.0   (lower leagues)
    """
    y_real = np.expm1(y_log)
    weights = np.where(y_real > 60_000_000, 5.0,
              np.where(y_real > 25_000_000, 2.5,
              np.where(y_real >  5_000_000, 1.5,
              1.0)))

    total_weighted = (weights * np.ones_like(y_real)).sum()
    print(f"\n  Sample weight breakdown:")
    print(f"    Elite  (>£60m):    {(weights == 5.0).sum():>5,} records × 5.0 "
          f"= {(weights == 5.0).sum() * 5:.0f} effective samples")
    print(f"    High   (£25-60m):  {(weights == 2.5).sum():>5,} records × 2.5 "
          f"= {(weights == 2.5).sum() * 2.5:.0f} effective samples")
    print(f"    Mid    (£5-25m):   {(weights == 1.5).sum():>5,} records × 1.5 "
          f"= {(weights == 1.5).sum() * 1.5:.0f} effective samples")
    print(f"    Standard (<£5m):   {(weights == 1.0).sum():>5,} records × 1.0 "
          f"= {(weights == 1.0).sum() * 1.0:.0f} effective samples")
    print(f"    Total effective:   {total_weighted:>7,.0f}")
    return weights


def train_model(X, y):
    """
    Trains the XGBoost regressor using RandomizedSearchCV + sample weights.

    Key improvements over previous version:
      - sample_weight replaces SMOTE: native, noise-free, principled
      - Added reg_alpha (L1) to complement reg_lambda (L2) regularisation
      - Elite-specific MAE reported alongside global MAE for transparency
      - Weights are computed on train split only (clean test evaluation)
    """
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Compute weights on training set ONLY — test set uses uniform weighting
    sample_weights_train = compute_sample_weights(y_train)

    xgb_reg = xgb.XGBRegressor(
        objective='reg:squarederror',
        random_state=42,
        tree_method='hist'  # Fastest for large datasets
    )

    param_dist = {
        'n_estimators':     [200, 400, 600, 800],
        'learning_rate':    [0.01, 0.03, 0.05, 0.08],
        'max_depth':        [4, 5, 6, 7],
        'min_child_weight': [1, 2, 3, 5],    # Protects against overfitting on rare elites
        'subsample':        [0.7, 0.8, 0.9, 1.0],
        'colsample_bytree': [0.7, 0.8, 0.9, 1.0],
        'gamma':            [0, 0.05, 0.1, 0.2],
        'reg_lambda':       [0.5, 1.0, 1.5, 2.0],  # L2 regularisation
        'reg_alpha':        [0, 0.05, 0.1, 0.2],    # L1 regularisation (new)
    }

    print("\nBeginning Hyperparameter Search (50 iterations, 5-fold CV)...")
    search = RandomizedSearchCV(
        xgb_reg,
        param_distributions=param_dist,
        n_iter=50,
        cv=5,
        scoring='neg_mean_absolute_error',
        n_jobs=-1,
        random_state=42,
        verbose=1
    )

    # This is the key line — XGBoost re-weights gradient updates per sample
    search.fit(X_train, y_train, sample_weight=sample_weights_train)

    best_model = search.best_estimator_
    print(f"\nBest hyperparameters: {search.best_params_}")

    # ── Evaluate on clean hold-out (no sample weights at test time) ───────────
    predictions_log  = best_model.predict(X_test)
    predictions_real = np.expm1(predictions_log)
    y_test_real      = np.expm1(y_test)

    mae  = mean_absolute_error(y_test_real, predictions_real)
    rmse = np.sqrt(mean_squared_error(y_test_real, predictions_real))

    print(f"\n{'='*55}")
    print(f"  Model Evaluation (held-out test set)")
    print(f"{'='*55}")
    print(f"  Global MAE:  £{mae:>12,.0f}")
    print(f"  Global RMSE: £{rmse:>12,.0f}")

    # Elite-specific performance (the critical metric for our use case)
    for threshold, label in [(60_000_000, ">£60m"), (25_000_000, ">£25m")]:
        mask = y_test_real > threshold
        if mask.sum() > 0:
            tier_mae = mean_absolute_error(
                y_test_real[mask], predictions_real[mask]
            )
            print(f"  Elite MAE ({label}): £{tier_mae:>12,.0f}  [{mask.sum()} players]")

    print(f"{'='*55}")

    best_model.save_model("fairvalue_xgboost.json")
    print("  Model saved: fairvalue_xgboost.json")

    return best_model, mae
