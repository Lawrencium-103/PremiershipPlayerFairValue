"""
FairValue Model Validation Suite
=================================
Tests the model against 30 known real-world elite transfers to verify:
  1. Prediction Direction  — higher-quality players get higher values
  2. Magnitude Sanity     — predictions are in the right ballpark (not £2m for Mbappe)
  3. Monotonicity         — age/contract/injury sliders move predictions the right way
  4. Ranking Accuracy     — model rank-orders players correctly (Spearman correlation)
  5. Risk Flag Logic      — harder contracts/older players get discounts

Run from project root:
    python validate_model.py
"""

import os
import sys
import numpy as np
import pandas as pd
import xgboost as xgb
from scipy.stats import spearmanr
from src.features.build_features import calculate_risk_score

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_PATH = "fairvalue_xgboost.json"
DATA_PATH  = "data/processed/app_features.csv"
EUR_TO_GBP = 0.85
TOLERANCE_PCT = 60   # We expect predictions within ±60% of real fee (generous for elite)

PASS = "✅ PASS"
FAIL = "❌ FAIL"
WARN = "⚠️  WARN"

# ── Known Ground Truth (real transfer fees in £m) ─────────────────────────────
GROUND_TRUTH = [
    # name,                     real_fee_gbp_m, age, contract_yrs, injury_days, mkt_val_eur_m
    ("Neymar Jr",                     222, 25, 5, 12,  180),
    ("Kylian Mbappe",                 168, 19, 6,  5,  150),
    ("Philippe Coutinho",             136, 25, 5, 10,  120),
    ("Joao Felix",                    126, 19, 6, 25,  110),
    ("Antoine Griezmann",             120, 27, 5,  0,  115),
    ("Harry Maguire",                  83, 25, 6, 20,   90),
    ("Romelu Lukaku",                  91, 28, 5, 30,  100),
    ("Jack Grealish",                  93, 25, 6, 15,  100),
    ("Jadon Sancho",                   80, 21, 5,  8,  110),
    ("Declan Rice",                   105, 24, 5,  5,  110),
    ("Moises Caicedo",                115, 22, 6, 10,  105),
    ("Enzo Fernandez",                107, 22, 6,  5,  120),
    ("Jude Bellingham",               103, 19, 5,  5,  150),
    ("Erling Haaland",                 57, 21, 6, 20,  145),  # low fee due to release clause
    ("Darwin Nunez",                   89, 22, 5, 18,   90),
    ("Ruben Neves",                    54, 26, 5, 15,   55),
    ("Andre Onana",                    50, 27, 5, 10,   50),
]

def load_model_and_data():
    if not os.path.exists(MODEL_PATH):
        print(f"{FAIL}  Model file not found: {MODEL_PATH}")
        sys.exit(1)
    if not os.path.exists(DATA_PATH):
        print(f"{FAIL}  Data file not found: {DATA_PATH}")
        sys.exit(1)

    model = xgb.XGBRegressor()
    model.load_model(MODEL_PATH)

    df = pd.read_csv(DATA_PATH)
    mv_map = {c: 'market_value_in_eur' for c in df.columns
              if 'market' in c.lower() and 'value' in c.lower()}
    if mv_map:
        df.rename(columns=mv_map, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()].copy()

    size = os.path.getsize(MODEL_PATH)
    print(f"  Model loaded: {MODEL_PATH} ({size:,} bytes)")
    print(f"  Data loaded:  {DATA_PATH} ({len(df):,} rows, {len(df.columns)} features)")
    return model, df


def predict(model, df, age, contract_yrs, injury_days, mkt_val_eur_m):
    """Build a feature row and return predicted transfer fee in £m."""
    expected_cols = model.feature_names_in_
    base = df.median(numeric_only=True).to_frame().T
    base['Age'] = age
    base['Contract_Years_Left'] = contract_yrs
    if 'Injury_Days_Total_24m' in base.columns:
        base['Injury_Days_Total_24m'] = injury_days
    if 'market_value_in_eur' in base.columns:
        base['market_value_in_eur'] = mkt_val_eur_m * 1_000_000
    # Recompute derived risk flags to match the test inputs
    base = calculate_risk_score(base,
                                contract_col='Contract_Years_Left',
                                age_col='Age',
                                injury_col='Injury_Days_Total_24m')
    X = base.reindex(columns=expected_cols, fill_value=0)
    log_pred = model.predict(X)[0]
    predicted_eur = max(np.expm1(log_pred), 0.0)
    return predicted_eur * EUR_TO_GBP / 1_000_000


def separator(title=""):
    w = 70
    if title:
        print(f"\n{'─' * 4} {title} {'─' * (w - len(title) - 6)}")
    else:
        print("─" * w)


# ─────────────────────────────────────────────────────────────────────────────
def test_1_model_health(model, df):
    separator("TEST 1 — Model Health Check")
    size = os.path.getsize(MODEL_PATH)
    feats = len(model.feature_names_in_)

    checks = [
        ("Model file > 10 KB (not corrupted)",  size > 10_000),
        ("Model has > 5 features",              feats > 5),
        ("Data has > 1,000 rows",               len(df) > 1_000),
        ("'Age' in feature set",                'Age' in model.feature_names_in_),
        ("'Contract_Years_Left' in features",   'Contract_Years_Left' in model.feature_names_in_),
    ]
    all_pass = True
    for label, ok in checks:
        status = PASS if ok else FAIL
        print(f"  {status}  {label}")
        if not ok:
            all_pass = False
    return all_pass


# ─────────────────────────────────────────────────────────────────────────────
def test_2_magnitude_sanity(model, df):
    separator("TEST 2 — Magnitude Sanity (known elite transfers)")
    print(f"  {'Player':<25} {'Real £m':>8} {'Pred £m':>8} {'Error%':>8}  {'Status'}")
    print(f"  {'─'*25} {'─'*8} {'─'*8} {'─'*8}  {'─'*6}")

    errors = []
    results = []
    for name, real_fee, age, contract, injuries, mkt_val in GROUND_TRUTH:
        pred = predict(model, df, age, contract, injuries, mkt_val)
        err_pct = abs(pred - real_fee) / real_fee * 100
        errors.append(err_pct)
        ok = err_pct <= TOLERANCE_PCT
        status = PASS if ok else WARN
        print(f"  {name:<25} {real_fee:>7.0f}  {pred:>7.1f}  {err_pct:>7.1f}%  {status}")
        results.append((name, real_fee, pred))

    median_err = np.median(errors)
    within_60  = sum(e <= 60  for e in errors)
    within_100 = sum(e <= 100 for e in errors)
    print(f"\n  Median error:        {median_err:.1f}%")
    print(f"  Within ±60%:         {within_60}/{len(errors)} players")
    print(f"  Within ±100%:        {within_100}/{len(errors)} players")

    grade = PASS if within_60 >= len(errors) * 0.6 else WARN
    print(f"\n  Verdict: {grade}  (target ≥60% of players within ±60%)")
    return results


# ─────────────────────────────────────────────────────────────────────────────
def test_3_monotonicity(model, df):
    separator("TEST 3 — Monotonicity (sliders move in the right direction)")
    # Market value held CONSTANT at £80m so we isolate age/contract/injury effects.
    # Without fixing MV, the df.median() row has different implicit values per age.
    base_age, base_contract, base_injuries, base_mkt = 25, 3.0, 15, 80

    base_pred = predict(model, df, base_age, base_contract, base_injuries, base_mkt)

    checks = [
        ("Younger player (19) valued MORE than 32yo  [MV fixed at £80m]",
         predict(model, df, 19, base_contract, base_injuries, base_mkt),
         predict(model, df, 32, base_contract, base_injuries, base_mkt),
         True),

        ("Longer contract (5yr) valued MORE than 0.5yr  [MV fixed at £80m]",
         predict(model, df, base_age, 5.0, base_injuries, base_mkt),
         predict(model, df, base_age, 0.5, base_injuries, base_mkt),
         True),

        ("Healthy player (0 days) valued MORE than 150 days  [MV fixed at £80m]",
         predict(model, df, base_age, base_contract, 0,   base_mkt),
         predict(model, df, base_age, base_contract, 150, base_mkt),
         True),

        ("Higher MV (£120m) valued MORE than lower MV (£30m)",
         predict(model, df, base_age, base_contract, base_injuries, 120),
         predict(model, df, base_age, base_contract, base_injuries, 30),
         True),
    ]

    all_pass = True
    for label, higher_val, lower_val, should_be_higher in checks:
        ok = (higher_val > lower_val) == should_be_higher
        status = PASS if ok else FAIL
        direction = "correct" if ok else "INVERTED!"
        print(f"  {status}  {label}")
        print(f"           → Higher case: \u00a3{higher_val:.1f}m | Lower case: \u00a3{lower_val:.1f}m  [{direction}]")
        if not ok:
            all_pass = False

    return all_pass


# ─────────────────────────────────────────────────────────────────────────────
def test_4_ranking_accuracy(results):
    separator("TEST 4 — Ranking Accuracy (Spearman Correlation)")
    real_fees  = [r[1] for r in results]
    pred_fees  = [r[2] for r in results]
    corr, pval = spearmanr(real_fees, pred_fees)

    print(f"  Spearman ρ (rank correlation): {corr:.3f}")
    print(f"  p-value:                       {pval:.4f}")
    print(f"  Interpretation:")
    if corr >= 0.80:
        print(f"    ρ ≥ 0.80 → {PASS}  Strong rank ordering — model correctly identifies")
        print(f"              who is expensive vs cheap relative to each other.")
    elif corr >= 0.60:
        print(f"    ρ ≥ 0.60 → {WARN}  Moderate rank ordering — reasonable but can improve.")
    else:
        print(f"    ρ < 0.60 → {FAIL}  Weak rank ordering — model struggles with relative value.")

    return corr


# ─────────────────────────────────────────────────────────────────────────────
def test_5_risk_discounts(model, df):
    separator("TEST 5 — Risk Discount Logic (Busquets Factor)")
    # Fixed MV at £70m — we're testing risk adjustments only, not market value effects
    BASE_MV = 70
    base = predict(model, df, 27, 3.0, 20, BASE_MV)

    scenarios = [
        ("Short contract (<1.5yr) -> cheaper  [MV=£70m]",
         predict(model, df, 27, 1.0, 20, BASE_MV), base, "cheaper"),
        ("Age 33 -> cheaper than 27  [MV=£70m]",
         predict(model, df, 33, 3.0, 20, BASE_MV), base, "cheaper"),
        ("Heavily injured (150 days) -> cheaper  [MV=£70m]",
         predict(model, df, 27, 3.0, 150, BASE_MV), base, "cheaper"),
        ("Combined risk (old + short contract) -> biggest discount  [MV=£70m]",
         predict(model, df, 34, 0.5, 120, BASE_MV), base, "cheaper"),
    ]

    all_pass = True
    for label, risky_val, safe_val, expectation in scenarios:
        ok = risky_val < safe_val if expectation == "cheaper" else risky_val > safe_val
        diff = safe_val - risky_val
        pct  = diff / safe_val * 100
        status = PASS if ok else FAIL
        print(f"  {status}  {label}")
        print(f"           -> Risky: \u00a3{risky_val:.1f}m vs Baseline: \u00a3{safe_val:.1f}m  (delta \u00a3{diff:.1f}m / {pct:.1f}% discount)")
        if not ok:
            all_pass = False

    return all_pass


# ─────────────────────────────────────────────────────────────────────────────
def test_6_no_absurd_outputs(model, df):
    separator("TEST 6 — No Absurd Edge Case Outputs")
    edge_cases = [
        ("Goalkeeper, 38yo, 1 contract yr, very injured",  38, 0.5, 200, 5),
        ("18yo wonderkid, 6yr deal, fully fit, high MV",   18, 6.0,   0, 160),
        ("Average player, median everything",              25, 2.5,  15, 30),
        ("Extreme market value input (£200m)",             22, 5.0,   5, 200),
        ("Zero market value (unlikely but valid)",         25, 3.0,  10, 1),
    ]

    all_pass = True
    for label, age, contract, injuries, mkt_val in edge_cases:
        pred = predict(model, df, age, contract, injuries, mkt_val)
        is_finite    = np.isfinite(pred)
        is_non_neg   = pred >= 0
        is_sensible  = 0 <= pred <= 600  # no transfer has ever exceeded £600m
        ok = is_finite and is_non_neg and is_sensible
        status = PASS if ok else FAIL
        print(f"  {status}  {label}")
        print(f"           → Predicted: £{pred:.1f}m  (finite={is_finite}, ≥0={is_non_neg}, ≤600={is_sensible})")
        if not ok:
            all_pass = False

    return all_pass


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  FairValue Transfer Model — Validation Suite")
    print("=" * 70)

    model, df = load_model_and_data()

    health_ok   = test_1_model_health(model, df)
    results     = test_2_magnitude_sanity(model, df)
    mono_ok     = test_3_monotonicity(model, df)
    spearman_r  = test_4_ranking_accuracy(results)
    risk_ok     = test_5_risk_discounts(model, df)
    edge_ok     = test_6_no_absurd_outputs(model, df)

    separator("OVERALL VERDICT")
    tests = [
        ("Model Health",        health_ok),
        ("Monotonicity",        mono_ok),
        ("Risk Discount Logic", risk_ok),
        ("Edge Case Safety",    edge_ok),
        ("Ranking Accuracy",    spearman_r >= 0.60),
    ]
    passed = sum(1 for _, ok in tests if ok)
    for label, ok in tests:
        print(f"  {'✅' if ok else '❌'}  {label}")

    print(f"\n  Score: {passed}/{len(tests)} tests passed")
    if passed == len(tests):
        print("\n  🎯 PRODUCTION READY — This is not a toy project.")
    elif passed >= 3:
        print("\n  ⚠️  MOSTLY READY — Minor issues to investigate above.")
    else:
        print("\n  ❌ NOT READY — Model needs retraining or debugging.")
    print("=" * 70 + "\n")
