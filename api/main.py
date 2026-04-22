from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import os
import time
import xgboost as xgb
from ddgs import DDGS
from textblob import TextBlob

app = FastAPI(
    title="FairValue Strategic AI API",
    description="Investor-ready Player Valuation Engine"
)

# Fixed: allow_credentials=True is a CORS spec violation when allow_origins=["*"].
# Browsers silently reject credentialed requests to wildcard origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # Tighten to Vercel domain after first deploy
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def health_check():
    """Required by Render to confirm the service is alive."""
    return {
        "status": "healthy",
        "model_loaded": model_global is not None,
        "data_loaded": df_global is not None,
    }


@app.get("/api/players")
def get_players(q: str = ""):
    """
    Returns unique player names from the training database.
    Accepts an optional ?q= filter for autocomplete.
    The React frontend uses this to power the player search input.
    """
    if df_global is None:
        return {"players": []}
    name_col = next(
        (c for c in ["name", "name_x", "Player_Name", "Name"] if c in df_global.columns),
        None,
    )
    if not name_col:
        return {"players": []}
    all_names = df_global[name_col].astype(str).dropna().unique()
    if q:
        all_names = [n for n in all_names if q.lower() in n.lower()]
    return {"players": sorted(all_names)[:100]}


@app.get("/api/scout")
async def scout_player(player: str, club: str = "", interested_club: str = ""):
    """
    Standalone NLP-only intelligence endpoint — used by the Live Intel page.
    Does NOT run the ML model, just returns 3-axis DDGS sentiment scores.
    Shares the same 1-hour TTL cache as the full /api/evaluate endpoint.
    """
    if not player.strip():
        raise HTTPException(status_code=422, detail="player query param is required")
    nlp = _fetch_nlp_intelligence(player.strip(), club.strip(), interested_club.strip())
    return {
        "player": player,
        "durability": nlp["durability"],
        "recency": nlp["recency"],
        "agent": nlp["agent"],
        "logs": nlp.get("_logs", []),
        "from_cache": nlp.get("_from_cache", False),
    }



# ── Currency Config ────────────────────────────────────────────────────────────
EUR_TO_GBP = 0.85  # Approximate — review quarterly

# ── Path resolution: works locally AND inside the Docker container ─────────────
# Using __file__ means paths are always relative to api/main.py, not cwd.
import pathlib
_ROOT      = pathlib.Path(__file__).parent.parent.resolve()
DATA_PATH  = str(_ROOT / "data" / "processed" / "app_features.csv")
MODEL_PATH = str(_ROOT / "fairvalue_xgboost.json")

# ── Data / Model Globals ───────────────────────────────────────────────────────
df_global = None
model_global = None
expected_cols_global = None


@app.on_event("startup")
def startup_event():
    global df_global, model_global, expected_cols_global

    if os.path.exists(DATA_PATH):
        df_global = pd.read_csv(DATA_PATH)
        mv_rename_map = {
            col: 'market_value_in_eur'
            for col in df_global.columns
            if 'market' in col.lower() and 'value' in col.lower()
        }
        if mv_rename_map:
            df_global.rename(columns=mv_rename_map, inplace=True)
        df_global = df_global.loc[:, ~df_global.columns.duplicated()].copy()

    if os.path.exists(MODEL_PATH):
        model_global = xgb.XGBRegressor()
        model_global.load_model(MODEL_PATH)
        expected_cols_global = model_global.feature_names_in_


# ── NLP Intelligence Cache (TTL = 1 hour) ────────────────────────────────────
# Fixed: previously ran 3 live DDGS searches on every API call — caused
# rate-limiting errors and high latency. Now cached per player+club for 1 hour.
_nlp_cache: dict = {}
_NLP_CACHE_TTL = 3600  # seconds


def _fetch_nlp_intelligence(
    player_name: str, current_club: str, interested_club: str
) -> dict:
    """
    Returns DDGS sentiment scores for durability, recency, and agent axes.
    Results are cached per player+club combination for 1 hour to prevent
    rate-limiting and reduce API latency.
    """
    cache_key = f"{player_name.lower()}|{current_club.lower()}"
    cached = _nlp_cache.get(cache_key)
    if cached and (time.time() - cached.get('_ts', 0)) < _NLP_CACHE_TTL:
        return {**cached, '_from_cache': True}

    ddgs = DDGS()
    axes = {
        'durability': f"{player_name} {current_club} injury status games missed medical",
        'recency':    f"{player_name} {current_club} recent form impact stats",
        'agent':      f"{player_name} {current_club} transfer rumors {interested_club} fee",
    }
    scores = {'durability': 0.0, 'recency': 0.0, 'agent': 0.0}
    logs = []

    for axis, query in axes.items():
        try:
            snippets = list(ddgs.text(query.strip(), max_results=3))
            sentiments = [
                TextBlob(r.get('body', '') + ' ' + r.get('title', '')).sentiment.polarity
                for r in snippets
            ]
            avg_pol = sum(sentiments) / len(sentiments) if sentiments else 0.0
            scores[axis] = float(avg_pol)
            logs.append(f"Scraped {axis}: Polarity {avg_pol:.2f}")
        except Exception as e:
            logs.append(f"Failed {axis}: {str(e)}")

    result = {**scores, '_ts': time.time(), '_logs': logs, '_from_cache': False}
    _nlp_cache[cache_key] = result
    return result


# ── Request Schema ────────────────────────────────────────────────────────────
class PlayerEvaluateRequest(BaseModel):
    selected_name: str
    current_club: str = ""
    interested_club: str = ""
    contract_years: float = 2.0
    age: int = 24
    injuries_24m: int = 10
    asking_price: float = 45.0
    market_value_estimation: float = 20.0


@app.post("/api/evaluate")
async def evaluate_player(req: PlayerEvaluateRequest):
    if df_global is None or model_global is None:
        raise HTTPException(
            status_code=500,
            detail="Model or data not loaded on startup. Check server logs."
        )

    name_col = next(
        (c for c in ['name', 'name_x', 'Player_Name', 'Name'] if c in df_global.columns),
        None
    )

    player_data = df_global.median(numeric_only=True).to_frame().T
    if name_col and req.selected_name in df_global[name_col].astype(str).tolist():
        player_data = df_global[
            df_global[name_col].astype(str) == req.selected_name
        ].iloc[0:1].copy()

    player_data['Contract_Years_Left'] = req.contract_years
    player_data['Age'] = req.age
    if 'Injury_Days_Total_24m' in player_data.columns:
        player_data['Injury_Days_Total_24m'] = req.injuries_24m
    if 'market_value_in_eur' in player_data.columns:
        player_data['market_value_in_eur'] = (
            req.market_value_estimation * 1_000_000
        ) / EUR_TO_GBP

    X_infer = player_data.reindex(columns=expected_cols_global, fill_value=0)

    raw_preds = model_global.predict(X_infer)
    log_pv = float(raw_preds[0])
    baseline_pv = max(float(np.expm1(log_pv)), 0.0)
    baseline_pv_m = baseline_pv / 1_000_000
    conservative_bound_m = baseline_pv_m * 0.85

    # ── SHAP: Talent vs Depreciation Decomposition ────────────────────────────
    # Fixed: previous logic used max(0, ...) which silently dropped the
    # youth/long-contract premium (negative depreciation) case.
    # depreciation_penalty_m is now signed: positive = age/contract drag,
    # negative = youth premium (long contract, prime age).
    dmatrix = xgb.DMatrix(X_infer)
    shap_contribs = model_global.get_booster().predict(dmatrix, pred_contribs=True)[0]
    feature_shaps = shap_contribs[:-1]  # Last element is the SHAP base value

    try:
        idx_age = expected_cols_global.tolist().index('Age')
        idx_contract = expected_cols_global.tolist().index('Contract_Years_Left')
        # Combined log-space drag from age and contract length
        age_contract_shap = float(feature_shaps[idx_age] + feature_shaps[idx_contract])
        # Talent value = what this player would command without age/contract factors
        talent_log_pv = log_pv - age_contract_shap
        talent_pv_m = float(np.expm1(talent_log_pv)) / 1_000_000
        # Positive = depreciation penalty | Negative = youth/contract premium
        depreciation_penalty_m = talent_pv_m - baseline_pv_m
    except (ValueError, IndexError):
        # Age or Contract_Years_Left not in model features — decomposition unavailable
        talent_pv_m = baseline_pv_m
        depreciation_penalty_m = 0.0

    # ── Internal Risk Factors ─────────────────────────────────────────────────
    internal_risk_pct = (
        (0.20 if req.contract_years < 1.5 else 0.0) +
        (0.15 if req.age > 30 else 0.0) +
        (0.10 if req.injuries_24m > 60 else 0.0)
    )

    # ── External NLP Intelligence (1-hour TTL cache) ──────────────────────────
    nlp = _fetch_nlp_intelligence(req.selected_name, req.current_club, req.interested_club)
    dur = nlp['durability']
    rec = nlp['recency']
    agnt = nlp['agent']
    logs = nlp.get('_logs', [])

    # Tier-aware hype ceiling prevents NLP from distorting low-value players
    if baseline_pv_m > 40.0:
        rec_ceiling_pct = 0.25
        tier_name = "Elite Tier (>£40m)"
    elif baseline_pv_m >= 10.0:
        rec_ceiling_pct = 0.10
        tier_name = "Core Tier (£10m–£40m)"
    else:
        rec_ceiling_pct = 0.05
        tier_name = "Base Tier (<£10m)"

    dur_adj = min(0.0, dur) * 0.15    # Injury news can only discount
    rec_adj = max(0.0, rec) * rec_ceiling_pct  # Form can only add premium
    agt_adj = min(0.0, agnt) * 0.05   # Agent leverage only discounts

    external_multiplier = 1.0 + rec_adj + dur_adj + agt_adj
    hard_cap_m = conservative_bound_m * (1.0 - internal_risk_pct) * external_multiplier

    # ── SHAP Feature Contribution Table ──────────────────────────────────────
    shap_data = sorted(
        [
            {"feature": f.replace('_', ' ').title(), "impact": float(s)}
            for f, s in zip(expected_cols_global, feature_shaps)
        ],
        key=lambda x: abs(x['impact']),
        reverse=True,
    )[:10]

    return {
        "ledger": {
            "intrinsic_performance_value": talent_pv_m,
            "category": tier_name,
            "depreciation": depreciation_penalty_m,
            "baseline_value": baseline_pv_m,
            "external_multiplier": external_multiplier,
            "hard_cap": hard_cap_m,
        },
        "nlp_results": {"durability": dur, "recency": rec, "agent": agnt},
        "nlp_cached": nlp.get('_from_cache', False),
        "logs": logs,
        "shap_data": shap_data,
    }
