import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

st.set_page_config(page_title="FFP / PSR Advisor", layout="wide", page_icon="💼")

st.title("💼 Financial Fair Play (PSR) Advisor")
st.markdown("Calculate the exact impact of a transfer on the club's 3-year Profitability & Sustainability Rules (PSR) allowance.")

import os

@st.cache_data
def load_data():
    df_path = "data/processed/app_features.csv"
    if not os.path.exists(df_path):
        return None
    return pd.read_csv(df_path)

df = load_data()

st.sidebar.header("Transfer Financials")

default_fee = 50.0
default_years = 5
default_wage = 100.0

if df is not None:
    name_col = next((c for c in ['name', 'name_x', 'Player_Name', 'Name'] if c in df.columns), None)
    if name_col:
        player_list = ["-- Custom Scenario --"] + sorted(df[name_col].astype(str).unique().tolist())
        target_player = st.sidebar.selectbox("Pre-fill from Database Player", player_list)
        if target_player != "-- Custom Scenario --":
            player_data = df[df[name_col].astype(str) == target_player].iloc[0]
            if 'market_value_in_eur' in player_data:
                raw_fee = float(player_data['market_value_in_eur'] / 1_000_000 * 0.85)
            elif 'market_value_in_eur_x' in player_data:
                raw_fee = float(player_data['market_value_in_eur_x'] / 1_000_000 * 0.85)
            else:
                raw_fee = 0.0
            # Clamp to [1.0, 300.0] — players with £0 market value (retained/loaned)
            # would crash the number_input widget whose min_value is 1.0
            default_fee = max(1.0, min(300.0, raw_fee))
            if 'Contract_Years_Left' in player_data:
                default_years = max(1, min(7, int(player_data['Contract_Years_Left'])))

transfer_fee_m = st.sidebar.number_input("Transfer Fee (£m)", 1.0, 300.0, float(default_fee), 1.0)
contract_years = st.sidebar.slider("Contract Length (Years)", 1, 7, int(default_years))
weekly_wage_k = st.sidebar.number_input("Weekly Wage (£k)", 5.0, 1000.0, float(default_wage), 5.0)
agent_fee_m = st.sidebar.number_input("Agent/Sign-on Fees (£m)", 0.0, 50.0, float(max(1.0, transfer_fee_m * 0.1)), 0.5)

st.sidebar.markdown("---")
st.sidebar.header("Club Economics")
current_psr_loss = st.sidebar.number_input("Current 3-Yr PSR Loss (£m)", -200.0, 150.0, 50.0, 5.0)
max_allowed_loss = st.sidebar.number_input("Max Allowed Loss (£m)", 0.0, 200.0, 105.0)

# Calculations
annual_amortisation = transfer_fee_m / contract_years
annual_wage_m = (weekly_wage_k * 52) / 1000.0
annual_agent_m = agent_fee_m / contract_years

total_annual_cost_m = annual_amortisation + annual_wage_m + annual_agent_m
total_contract_cost_m = transfer_fee_m + (annual_wage_m * contract_years) + agent_fee_m

psr_remaining = max_allowed_loss - current_psr_loss
new_psr_loss = current_psr_loss + total_annual_cost_m

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Financial Impact Summary")
    st.metric("Total Package Cost (Over Contract)", f"£{total_contract_cost_m:.1f}m")
    
    st.markdown("#### Annual Profit & Loss Hit")
    st.write(f"- Amortisation: **£{annual_amortisation:.1f}m/yr**")
    st.write(f"- Wages: **£{annual_wage_m:.1f}m/yr**")
    st.write(f"- Accrued Fees: **£{annual_agent_m:.1f}m/yr**")
    st.info(f"**Total Annual Accounting Cost: £{total_annual_cost_m:.1f}m**")

with col2:
    st.subheader("PSR Compliance Overview")
    labels = ['Current Loss', 'This Transfer (Yr 1)', 'Remaining Allowance']
    
    if new_psr_loss > max_allowed_loss:
        st.error(f"⚠️ BREACH RISK: This transfer pushes the club £{new_psr_loss - max_allowed_loss:.1f}m over the PSR limit of £{max_allowed_loss}m.")
        values = [current_psr_loss, total_annual_cost_m, 0]
        colors = ['gray', 'red', 'lightgray']
    else:
        st.success(f"✅ COMPLIANT: The club remains £{max_allowed_loss - new_psr_loss:.1f}m under the limit.")
        values = [current_psr_loss, total_annual_cost_m, max_allowed_loss - new_psr_loss]
        colors = ['gray', 'blue', 'lightgreen']
        
    fig = go.Figure(data=[go.Pie(labels=labels, values=values, hole=.5, marker_colors=colors)])
    fig.update_layout(title_text=f"£{max_allowed_loss}m 3-Yr Loss Limit")
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.subheader("Contract Horizon Prediction")

years = [f"Year {i}" for i in range(1, contract_years + 1)]
fig_bar = go.Figure(data=[
    go.Bar(name='Amortisation', x=years, y=[annual_amortisation]*contract_years),
    go.Bar(name='Wages', x=years, y=[annual_wage_m]*contract_years),
    go.Bar(name='Agent/Additional', x=years, y=[annual_agent_m]*contract_years)
])
fig_bar.update_layout(barmode='stack', title="Year-on-Year Accounting Impact (£m)")
st.plotly_chart(fig_bar, use_container_width=True)
