---
title: FairValue Transfer Cap Estimator
emoji: ⚽
colorFrom: green
colorTo: gray
sdk: streamlit
sdk_version: 1.32.0
app_file: app.py
pinned: true
license: mit
---

# FairValue Transfer Cap Estimator
A rigorous, data-driven 'Transfer Ceiling Calculator' grounded in ML and Hedonic Pricing Theory.


# FairValue Transfer Cap Estimator

**A rigorous, data-driven 'Transfer Ceiling Calculator' grounded in ML and Hedonic Pricing Theory.**

This application uses a trained XGBoost regressor to calculate the fair market valuation and risk-adjusted "Hard Cap" for football player transfers.

### Key Features:
- **ML Baseline Prediction:** Log-transformed XGBoost regressor trained on 12,500+ transfer records.
- **The Busquets Factor:** Dynamic risk scoring for age, contract length, and injury history.
- **Winner's Curse Prevention:** Calculates a "Hard Cap" ceiling to prevent statistical overpayment.
- **Live Search & Custom Player Mode:** Test real players from our database or simulate new signings from scratch.

### How to use:
1. Select a player from the dropdown or toggle to **Custom Player Mode**.
2. Adjust simulation parameters (Contract, Age, Injuries).
3. Input the **Selling Club Asking Price**.
4. Click **Calculate Prediction** to see the Hard Cap analysis!

### Local Development:
```bash
pip install -r requirements.txt
streamlit run app.py
```

---
*Built as a professional proof-of-concept for data-driven football recruitment.*
