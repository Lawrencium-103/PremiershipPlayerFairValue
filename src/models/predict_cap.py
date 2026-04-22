import numpy as np
import xgboost as xgb

class FairValueCapEstimator:
    def __init__(self, model_path="fairvalue_xgboost.json"):
        self.model = xgb.XGBRegressor()
        try:
            self.model.load_model(model_path)
            # Default validation error margin (Confidence Interval) roughly 15%
            self.model_error_margin = 0.15 
            self.is_loaded = True
        except:
            print("Warning: Model file not found. Estimations will be unavailable.")
            self.model_error_margin = 0.15
            self.is_loaded = False

    def predict_fair_value(self, player_features_df):
        """
        Calculates the Predicted Value (PV) and the computationally strict Hard Cap.
        """
        if not self.is_loaded:
            return {"error": "Model not loaded."}
            
        # 1. Predicted Value (PV) (Reverse the log1p transform)
        log_pv = self.model.predict(player_features_df)
        pv = np.expm1(log_pv)[0]
        
        # 2. Confidence Interval (CI) bounds
        conservative_value = pv * (1 - self.model_error_margin)
        optimistic_value = pv * (1 + self.model_error_margin)
        
        # 3. Calculate Risk Discount (RD)
        risk_discount_percentage = 0.0
        
        # Using feature engineered columns from build_features.py logic
        if 'Risk_Contract' in player_features_df.columns and player_features_df['Risk_Contract'].iloc[0] == 1:
            risk_discount_percentage += 0.20 # 20% discount for expiring contracts
            
        if 'Risk_Age' in player_features_df.columns and player_features_df['Risk_Age'].iloc[0] == 1:
            risk_discount_percentage += 0.15 # 15% discount for age curve decay
            
        if 'Risk_Injury' in player_features_df.columns and player_features_df['Risk_Injury'].iloc[0] == 1:
            risk_discount_percentage += 0.10 # 10% discount for recurring injuries
            
        risk_discount_monetary = conservative_value * risk_discount_percentage
        
        # 4. Hard Cap
        hard_cap = conservative_value - risk_discount_monetary
        
        return {
            'predicted_value': pv,
            'conservative': conservative_value,
            'optimistic': optimistic_value,
            'risk_discount': risk_discount_monetary,
            'risk_percentage': risk_discount_percentage,
            'hard_cap': hard_cap
        }
