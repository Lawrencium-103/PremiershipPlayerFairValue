import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import os
import xgboost as xgb
import traceback

try:
    from ddgs import DDGS
except ImportError:
    DDGS = None

try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

st.set_page_config(page_title="Transfer Estimator", layout="wide", page_icon="📊")

st.title("📊 Strategic Transfer Estimator")
st.markdown("Evaluate 'Hard Caps' guided by ML Valuations and Multi-Axis NLP intelligence.")

@st.cache_resource
def load_data_and_model():
    df_path = "data/processed/app_features.csv"
    if not os.path.exists(df_path):
        return None, None
    df = pd.read_csv(df_path)
    
    mv_rename_map = {}
    for col in df.columns:
        if 'market' in col.lower() and 'value' in col.lower():
            mv_rename_map[col] = 'market_value_in_eur'
    if mv_rename_map:
        df.rename(columns=mv_rename_map, inplace=True)
    df = df.loc[:, ~df.columns.duplicated()].copy()
    
    model = xgb.XGBRegressor()
    try:
        path = "fairvalue_xgboost.json"
        if os.path.exists(path):
            size = os.path.getsize(path)
            model.load_model(path)
            return df, (model, size, path)
        else:
            return df, "MODEL_FILE_NOT_FOUND"
    except Exception as e:
        return df, f"LOAD_ERROR: {str(e)}"

# --- NLP RECONNAISSANCE ENGINE ---
@st.cache_data(ttl=3600, show_spinner=False)
def run_strategic_recon(player_name, current_club, interested_club):
    if DDGS is None or TextBlob is None or not player_name.strip():
        return 0.0, 0.0, 0.0, ["Missing DDGS/TextBlob or Player Name"]
    
    ddgs = DDGS()
    
    c_club_str = current_club if current_club.strip() else ""
    i_club_str = interested_club if interested_club.strip() else ""
    
    axes = {
        'durability': f"{player_name} {c_club_str} injury status games missed medical",
        'recency': f"{player_name} {c_club_str} recent form impact stats",
        'agent': f"{player_name} {c_club_str} transfer rumors {i_club_str} fee"
    }
    
    results = {'durability': 0.0, 'recency': 0.0, 'agent': 0.0}
    explanations = []
    
    for axis, query in axes.items():
        try:
            snippets = list(ddgs.text(query.strip(), max_results=3))
            if not snippets:
                continue
            
            sentiments = []
            for r in snippets:
                content = r.get('body', '') + " " + r.get('title', '')
                blob = TextBlob(content)
                sentiments.append(blob.sentiment.polarity)
                
            avg_pol = sum(sentiments) / len(sentiments) if sentiments else 0.0
            results[axis] = avg_pol
            explanations.append(f"Scraped 3 sources for {axis}. Polarity: {avg_pol:.2f}")
        except Exception as e:
            explanations.append(f"Failed {axis}: {str(e)}")
            
    return results['durability'], results['recency'], results['agent'], explanations


df, model_meta = load_data_and_model()

if isinstance(model_meta, str):
    st.error(f"⚠️ {model_meta}")
    st.stop()

if df is None:
    st.error("⚠️ Data file not found. Run pipeline first.")
    st.stop()

model, model_size, model_path = model_meta

st.sidebar.header("Player Transfer Profile")
input_mode = st.sidebar.radio("Input Mode", ["Select Existing Player", "Create Custom Player"])

name_col = next((c for c in ['name', 'name_x', 'Player_Name', 'Name'] if c in df.columns), None)

selected_name = "Custom Player"
current_club = ""
interested_club = ""

if input_mode == "Select Existing Player":
    if name_col:
        player_list = sorted(df[name_col].astype(str).unique().tolist())
        selected_name = st.sidebar.selectbox("Target Database Player", player_list)
        player_data = df[df[name_col].astype(str) == selected_name].iloc[0:1].copy()
    else:
        st.stop()
    contract_years = st.sidebar.slider("Contract Years Remaining", 0.5, 6.0, float(player_data.get('Contract_Years_Left', 2.5).iloc[0] if 'Contract_Years_Left' in player_data else 2.5), 0.5)
    age = st.sidebar.slider("Age", 16, 40, int(player_data.get('Age', 24).iloc[0] if 'Age' in player_data else 24))
    inj_col = next((c for c in ['Injury_Days_Total_24m', 'Injury_Days'] if c in player_data.columns), None)
    injuries = st.sidebar.number_input("Injury missed days (24m)", 0, 500, int(player_data[inj_col].iloc[0]) if inj_col else 10)
    
    st.sidebar.markdown("---")
    st.sidebar.subheader("Market Context (Optional)")
    current_club = st.sidebar.text_input("Current Club", "")
    interested_club = st.sidebar.text_input("Interested Club (Buyer)", "")
else:
    selected_name = st.sidebar.text_input("Custom Player Name", "E.g., Viktor Gyokeres")
    
    st.sidebar.subheader("Market Context")
    current_club = st.sidebar.text_input("Current Club", "Sporting CP")
    interested_club = st.sidebar.text_input("Interested Club (Buyer)", "Arsenal")
    
    player_data = df.median(numeric_only=True).to_frame().T
    contract_years = st.sidebar.slider("Contract Years Remaining", 0.5, 6.0, 2.0, 0.5)
    age = st.sidebar.slider("Age", 16, 40, 24)
    injuries = st.sidebar.number_input("Injury missed days (24m)", 0, 500, 10)
    
    if 'market_value_in_eur' in player_data.columns:
        m_val = st.sidebar.number_input("Current Market Value Estimation (£m)", 1.0, 200.0, 20.0)
        player_data['market_value_in_eur'] = (m_val * 1_000_000) / 0.85

asking_price = st.sidebar.number_input("Selling Club Asking Price (£m)", 1.0, 300.0, 45.0)

expected_cols = model.feature_names_in_
player_data['Contract_Years_Left'] = contract_years
player_data['Age'] = age
if 'Injury_Days_Total_24m' in player_data.columns: 
    player_data['Injury_Days_Total_24m'] = injuries

X_infer = player_data.reindex(columns=expected_cols, fill_value=0)


if st.button("Calculate Prediction (w/ Network Recon)", type="primary"):
    with st.spinner("Executing Strategic Network Reconnaissance & XAI Profiling..."):
        raw_preds = model.predict(X_infer)
        log_pv = raw_preds[0]
        baseline_pv = np.expm1(log_pv)
        if baseline_pv < 0.1: baseline_pv = 0.0
    
        baseline_pv_m = baseline_pv / 1_000_000
        conservative_bound_m = baseline_pv_m * 0.85
        
        # --- NATIVE XGBOOST SHAP ISOLATION ---
        # Instead of the python SHAP library (which has float parsing bugs with XGBoost >2.0 JSON output),
        # we natively execute the C++ Explainer inside XGBoost via pred_contribs!
        dmatrix = xgb.DMatrix(X_infer)
        shap_vals = model.get_booster().predict(dmatrix, pred_contribs=True)[0]
        feature_shaps = shap_vals[:-1] # Last element is the expected value bias
        
        idx_age = expected_cols.tolist().index('Age')
        idx_contract = expected_cols.tolist().index('Contract_Years_Left')
        
        shap_depreciation = feature_shaps[idx_age] + feature_shaps[idx_contract]
        
        # Mathematical Isolation (Log-Space extraction)
        raw_skill_log_pv = log_pv - shap_depreciation
        raw_skill_pv_m = np.expm1(raw_skill_log_pv) / 1_000_000
        depreciation_penalty_m = raw_skill_pv_m - baseline_pv_m
        
        if depreciation_penalty_m < 0:
            depreciation_penalty_m = 0.0 # Prevent strange edge cases where age actually increased value
        
        # 1. Base ML Internal Risk (Data-driven)
        internal_risk_pct = (0.2 if contract_years < 1.5 else 0) + (0.15 if age > 30 else 0) + (0.1 if injuries > 60 else 0)
        
        # 2. External NLP Risk (Hype Factor) via DDGS
        dur, rec, agnt, recon_logs = run_strategic_recon(selected_name, current_club, interested_club)
        
        # --- TIER-CALIBRATED VOLATILITY IMPLEMENTATION ---
        # The impact of "Hype / Form" scales with the intrinsic baseline ML valuation.
        if baseline_pv_m > 40.0:
            rec_ceiling_pct = 0.25 # Global bidding war (Elite Tier)
            tier_name = "Elite Tier (>£40m)"
        elif baseline_pv_m >= 10.0:
            rec_ceiling_pct = 0.10 # Standard inflation (Core Tier)
            tier_name = "Core Tier (£10m-£40m)"
        else:
            rec_ceiling_pct = 0.05 # Tight budget constraint (Base Tier)
            tier_name = "Base Tier (<£10m)"

        # Durability (-15% max): Only subtract if negative sentiment
        dur_adj = min(0.0, dur) * 0.15 
        # Recency (Scaled max): Only add if positive sentiment
        rec_adj = max(0.0, rec) * rec_ceiling_pct
        # Agent (-5% max): Only subtract if negative sentiment
        agt_adj = min(0.0, agnt) * 0.05
        
        external_multiplier = (1.0 + rec_adj + dur_adj + agt_adj)
        
        # Final Hard Cap Math
        hard_cap_m = conservative_bound_m * (1 - internal_risk_pct) * external_multiplier
    
        col1, col2 = st.columns([2, 1])
        with col1:
            fig = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=asking_price,
                delta={'reference': hard_cap_m, 'increasing': {'color': "red"}, 'decreasing': {'color': 'green'}},
                title={'text': "Asking Price vs Hard Cap (£m)"},
                gauge={
                    'axis': {'range': [0, max(asking_price, 100)]}, 
                    'threshold': {'line': {'color': "black", 'width': 4}, 'value': hard_cap_m},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, hard_cap_m], 'color': "lightgray"},
                        {'range': [hard_cap_m, max(asking_price, 100)], 'color': "salmon"}
                    ]
                }
            ))
            st.plotly_chart(fig, use_container_width=True)
    
        with col2:
            st.subheader("XAI Valuation Ledger")
            st.metric("1. Intrinsic Performance Value", f"£{raw_skill_pv_m:.1f}m", f"Category: {tier_name}")
            st.metric("2. Age & Contract Depreciation", f"-£{depreciation_penalty_m:.1f}m", "SHAP Calculated Penalty", delta_color="inverse")
            st.metric("3. Final ML Baseline", f"£{baseline_pv_m:.1f}m")
            
            st.markdown("---")
            if external_multiplier != 1.0:
                st.metric("NLP External Hype Multiplier", f"x {external_multiplier:.2f}", f"{(external_multiplier-1.0)*100.0:+.1f}% External Factor")
            st.metric("Final Hard Cap (Max Bid)", f"£{hard_cap_m:.1f}m")
            
            if asking_price > hard_cap_m:
                st.error(f"Winner's Curse Risk: Overpaying by £{asking_price-hard_cap_m:.1f}m")
            else:
                st.success("Target is currently under Hard Cap valuation!")
                
        st.markdown("---")
        
        # Consultant Summary Block
        st.subheader("🎩 Strategic Consultant Summary")
        net_nlp_adj_pct = (external_multiplier - 1.0) * 100
        
        summary_text = f"**Executive Diagnosis:** Using Native XGBoost SHAP isolation, the model acknowledges {selected_name}'s pure on-pitch performance statistics translate to **£{raw_skill_pv_m:.1f}m** of raw intrinsic value. However, the model strictly penalises his valuation by **-£{depreciation_penalty_m:.1f}m** purely due to depreciation risks concerning his Age ({age}) and Contract ({contract_years:.1f}yr). This establishes his true machine value at **£{baseline_pv_m:.1f}m**. "
        
        summary_text += "\n\n**Market Reconnaissance:**"
        
        if rec_adj > 0:
            summary_text += f"\n- **Tier-Calibrated Form Premium:** Positive recent form (Polarity {rec:.2f}) triggers a {rec_adj*100:.1f}% inflation premium based on the {tier_name} leverage rules. "
        if dur_adj < 0:
            summary_text += f"\n- **Durability Discount:** Live medical scans indicate recurring or sustained injury narratives (Polarity {dur:.2f}). To protect investment, a strictly enforced {-dur_adj*100:.1f}% discount is applied. "
        if agt_adj < 0:
            summary_text += f"\n- **Agent/Noise Discount:** Market rumors indicate potential friction or excessive demands (Polarity {agnt:.2f}), penalising the cap by {-agt_adj*100:.1f}%. "
            
        if net_nlp_adj_pct != 0:
            summary_text += f"\n\n**Outcome:** Combining ML Baseline with the NLP Adjuster ({net_nlp_adj_pct:+.1f}%), the absolute PSR Hard Cap is set to **£{hard_cap_m:.1f}m**."
        else:
            summary_text += "\n\n**Outcome:** External reconnaissance flagged no significant financial volatility. The ML 15% safety threshold applies entirely, setting the cap to **£{hard_cap_m:.1f}m**."
            
        st.info(summary_text)
        
        with st.expander("Show Reconnaissance Log"):
            for log in recon_logs:
                st.write(log)
                
        # --- NEW SHAP VISUALIZATION CHART ---
        st.markdown("---")
        st.subheader("🔬 SHAP Deep Dive: Top 10 Valuation Drivers")
        st.markdown(f"Mapping the exact algorithmic variables that pushed {selected_name}'s valuation up (green) or down (red).")
        
        shap_df = pd.DataFrame({
            'Feature': [feat.replace('_', ' ').title() for feat in expected_cols],
            'SHAP Value': feature_shaps
        })
        
        # Sort by absolute magnitude to find the 10 most impactful features
        shap_df['Abs_Impact'] = shap_df['SHAP Value'].abs()
        top_10 = shap_df.sort_values(by='Abs_Impact', ascending=False).head(10)
        
        # Reverse sort so the largest impact is on top in the horizontal bar chart
        top_10 = top_10.sort_values(by='Abs_Impact', ascending=True)
        
        bar_colors = ['salmon' if val < 0 else 'mediumseagreen' for val in top_10['SHAP Value']]
        
        fig2 = go.Figure(go.Bar(
            x=top_10['SHAP Value'],
            y=top_10['Feature'],
            orientation='h',
            marker_color=bar_colors,
            text=[f"{v:+.3f}" for v in top_10['SHAP Value']],
            textposition='auto',
            hoverinfo='text',
            hovertemplate='%{y}: %{x:+.4f}<extra></extra>' # <extra></extra> hides trace name
        ))
        
        fig2.update_layout(
            title="Top 10 Feature Contributions (Log Price Space)",
            xaxis_title="SHAP Value (Impact on Log Valuation)",
            yaxis_title="",
            height=400,
            margin=dict(l=0, r=0, t=45, b=0),
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        st.plotly_chart(fig2, use_container_width=True)
