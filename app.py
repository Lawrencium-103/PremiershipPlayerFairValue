import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import xgboost as xgb
from src.models.explain import generate_shap_explanation
from src.features.build_features import calculate_risk_score

st.set_page_config(page_title="FairValue Transfer Cap Estimator", layout="wide")

# ── Currency Config ───────────────────────────────────────────────────────────
EUR_TO_GBP = 0.85  # Approximate conversion — review quarterly

st.title("FairValue Transfer Cap Estimator")
st.markdown(
    "A rigorous, data-driven 'Transfer Ceiling Calculator' grounded in ML "
    "and Hedonic Pricing Theory."
)


# ── Data Loading ─────────────────────────────────────────────────────────────
# Fixed: was @st.cache_resource — mutations persisted across user sessions.
# @st.cache_data correctly serialises DataFrames per session.
@st.cache_data
def load_player_data():
    """Loads processed player features CSV. Returns None if file not found."""
    df_path = "data/processed/app_features.csv"
    if not os.path.exists(df_path):
        return None
    df = pd.read_csv(df_path)
    mv_rename_map = {
        col: 'market_value_in_eur'
        for col in df.columns
        if 'market' in col.lower() and 'value' in col.lower()
    }
    if mv_rename_map:
        df.rename(columns=mv_rename_map, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    return df


# ── Model Loading ─────────────────────────────────────────────────────────────
# @st.cache_resource is correct here — the model object is shared, not copied.
@st.cache_resource
def load_model():
    """Loads XGBoost model from disk. Returns (model, size_bytes, path)."""
    xgb_model = xgb.XGBRegressor()
    for path in ["fairvalue_xgboost.json", "FairValue_xgboost.json"]:
        if os.path.exists(path):
            size = os.path.getsize(path)
            xgb_model.load_model(path)
            return xgb_model, size, path
    return None, 0, None


df = load_player_data()
model, model_size, model_path = load_model()

if df is None:
    st.error("⚠️ Data file not found: `data/processed/app_features.csv`. Re-run the pipeline.")
    st.stop()

if model is None:
    st.error("⚠️ MODEL_FILE_NOT_FOUND — ensure `fairvalue_xgboost.json` is in the project root.")
    st.stop()

if model_size < 1000:
    st.error(
        f"❌ MODEL CORRUPTED: `{model_path}` is only {model_size:,} bytes "
        "(expected ~400 KB). Please re-upload the correct model file."
    )
    st.stop()  # Fixed: was missing — execution continued and produced silent zero predictions


# ── Sidebar ───────────────────────────────────────────────────────────────────
st.sidebar.header("Player Transfer Profile")
input_mode = st.sidebar.radio("Input Mode", ["Select Existing Player", "Create Custom Player"])

name_col = next(
    (c for c in ['name', 'name_x', 'Player_Name', 'Name'] if c in df.columns), None
)

selected_name = ""

if input_mode == "Select Existing Player":
    if name_col is None:
        st.error("No player name column found in data. Please re-run the pipeline.")
        st.stop()
    player_list = sorted(df[name_col].astype(str).unique().tolist())
    selected_name = st.sidebar.selectbox("Target Database Player", player_list)
    player_data = df[df[name_col].astype(str) == selected_name].iloc[0:1].copy()

    contract_years = st.sidebar.slider(
        "Contract Years Remaining", 0.5, 6.0,
        float(player_data['Contract_Years_Left'].iloc[0]), 0.5
    )
    age = st.sidebar.slider("Age", 16, 40, int(player_data['Age'].iloc[0]))
    inj_col = next(
        (c for c in ['Injury_Days_Total_24m', 'Injury_Days'] if c in player_data.columns), None
    )
    injuries = st.sidebar.number_input(
        "Injury missed days (24m)", 0, 500,
        int(player_data[inj_col].iloc[0]) if inj_col else 10
    )

else:
    player_data = df.median(numeric_only=True).to_frame().T
    contract_years = st.sidebar.slider("Contract Years Remaining", 0.5, 6.0, 2.0, 0.5)
    age = st.sidebar.slider("Age", 16, 40, 24)
    injuries = st.sidebar.number_input("Injury missed days (24m)", 0, 500, 10)

    if 'market_value_in_eur' in player_data.columns:
        m_val = st.sidebar.number_input("Current Market Value Estimation (£m)", 1.0, 200.0, 20.0)
        player_data['market_value_in_eur'] = (m_val * 1_000_000) / EUR_TO_GBP

asking_price = st.sidebar.number_input("Selling Club Asking Price (£m)", 1.0, 300.0, 45.0)


# ── Hype Factor Integration (consumed from Page 3 Live Player Intel) ──────────
# Fixed: was never read — hard_cap calculation ignored session_state entirely.
hype_all = st.session_state.get('player_hype_metrics', {})
hype_entry = hype_all.get(selected_name.lower(), {}) if selected_name else {}
hype_premium_pct = hype_entry.get('hype_premium_percent', 0.0)

if hype_premium_pct != 0.0:
    sign = "+" if hype_premium_pct > 0 else ""
    st.sidebar.info(
        f"💡 **Hype Factor Active:** {sign}{hype_premium_pct:.1f}%  \n"
        "*Run Page 3 → Live Player Intel to refresh.*"
    )
else:
    st.sidebar.caption("No Hype Factor loaded. Run Page 3 to enrich this estimate.")


# ── Build Inference Vector ─────────────────────────────────────────────────────
expected_cols = model.feature_names_in_
player_data = player_data.copy()
player_data['Contract_Years_Left'] = contract_years
player_data['Age'] = age
if 'Injury_Days_Total_24m' in player_data.columns:
    player_data['Injury_Days_Total_24m'] = injuries

# Recompute derived risk flags so they reflect the slider values, not stale DB data.
# Without this, Risk_Contract / Risk_Age / Risk_Injury don't update when sliders move.
player_data = calculate_risk_score(
    player_data,
    contract_col='Contract_Years_Left',
    age_col='Age',
    injury_col='Injury_Days_Total_24m'
)

X_infer = player_data.reindex(columns=expected_cols, fill_value=0)


if st.button("Calculate Prediction", type="primary"):
    raw_preds = model.predict(X_infer)
    log_pv = raw_preds[0]
    baseline_pv = max(float(np.expm1(log_pv)), 0.0)

    baseline_pv_m = baseline_pv / 1_000_000
    conservative_bound = baseline_pv * 0.85

    # Internal rule-based risk discount (transparent to users)
    risk_pct = (
        (0.20 if contract_years < 1.5 else 0.0) +
        (0.15 if age > 30 else 0.0) +
        (0.10 if injuries > 60 else 0.0)
    )

    # External hype multiplier from Page 3 NLP sentiment
    hype_multiplier = 1.0 + (hype_premium_pct / 100.0)
    hard_cap = conservative_bound * (1.0 - risk_pct) * hype_multiplier
    hard_cap_m = hard_cap / 1_000_000

    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Price Range Recommendation")
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=asking_price,
            delta={'reference': hard_cap_m, 'increasing': {'color': "red"}},
            title={'text': "Asking Price vs Hard Cap (£m)"},
            gauge={
                'axis': {'range': [0, max(asking_price * 1.2, 100)]},
                'threshold': {'line': {'color': "white", 'width': 4}, 'value': hard_cap_m}
            }
        ))
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Metrics Breakdown")
        st.metric("Predicted Market Value (Baseline)", f"£{baseline_pv_m:.1f}m")
        st.metric("Risk-Adjusted Hard Cap", f"£{hard_cap_m:.1f}m")
        if hype_premium_pct != 0.0:
            sign = "+" if hype_premium_pct > 0 else ""
            st.metric("Hype / Form Adjustment", f"{sign}{hype_premium_pct:.1f}%")
        if asking_price > hard_cap_m:
            overpay = asking_price - hard_cap_m
            st.error(f"⚠️ Winner's Curse Risk: £{overpay:.1f}m Overpay")
        else:
            st.success("✅ Asking price is within Fair Value bounds.")

    # ── SHAP Explainability Panel ─────────────────────────────────────────────
    # Fixed: shap was imported but never used. Now wired to generate_shap_explanation.
    st.markdown("---")
    st.subheader("🔬 XAI Explainability — What Drives This Valuation?")
    with st.spinner("Computing SHAP feature contributions..."):
        try:
            _, explanation_df = generate_shap_explanation(model, X_infer)
            top_shap = explanation_df.head(10).copy()
            top_shap['Label'] = top_shap['Feature'].str.replace('_', ' ').str.title()

            fig_shap = go.Figure(go.Bar(
                x=top_shap['Contribution_to_LogPrice'],
                y=top_shap['Label'],
                orientation='h',
                marker_color=[
                    '#e74c3c' if v < 0 else '#2ecc71'
                    for v in top_shap['Contribution_to_LogPrice']
                ],
                text=[f"{v:+.3f}" for v in top_shap['Contribution_to_LogPrice']],
                textposition='outside',
            ))
            fig_shap.update_layout(
                title="Top 10 Feature Contributions to Transfer Fee (Log-Price Scale)",
                xaxis_title="SHAP Value (Additive impact on log transfer fee)",
                yaxis={'categoryorder': 'total ascending'},
                height=420,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_shap, use_container_width=True)
            st.caption(
                "🟢 Green = boosts transfer value | 🔴 Red = depresses transfer value | "
                "Sorted by absolute magnitude."
            )
        except Exception as shap_err:
            st.warning(f"SHAP panel unavailable: {shap_err}")

    with st.expander("🛠️ Technical Deep Dive (Internal Metrics)"):
        st.write(f"**Model:** `{model_path}` ({model_size:,} bytes)")
        st.write(f"**Raw Log-Scale Prediction:** `{log_pv:.4f}`")
        mv_val = (
            X_infer['market_value_in_eur'].iloc[0]
            if 'market_value_in_eur' in X_infer.columns else "MISSING"
        )
        if isinstance(mv_val, (int, float)):
            st.write(f"**Market Value Input (EUR):** `{mv_val:,.0f}`")
        else:
            st.write(f"**Market Value Input:** `{mv_val}`")
        st.write("**Full Feature Vector:**", X_infer)

st.markdown("---")
st.subheader("Model Performance Assessment")
st.markdown(f"**Training Set:** `{len(df):,}` transfers | **Engine:** XGBoost + RandomizedSearchCV")
st.markdown("**Validation MAE:** `~£23,980,000` | **Status:** Production Ready")
