import shap
import pandas as pd
import numpy as np

def generate_shap_explanation(model, user_input_df):
    """
    Generates SHAP values for a specific player prediction.
    """
    # Create the tree explainer for XGBoost
    explainer = shap.TreeExplainer(model)
    
    # Calculate shap values for the specific prediction
    shap_values = explainer(user_input_df)
    
    # Extract structural contributions
    feature_names = user_input_df.columns
    contributions = shap_values.values[0]
    
    explanation_df = pd.DataFrame({
        'Feature': feature_names,
        'Value': user_input_df.iloc[0].values,
        'Contribution_to_LogPrice': contributions
    })
    
    # Identify top drivers
    explanation_df['Absolute_Impact'] = np.abs(explanation_df['Contribution_to_LogPrice'])
    explanation_df = explanation_df.sort_values(by='Absolute_Impact', ascending=False)
    
    return shap_values, explanation_df

def make_justification_string(prediction_dict):
    """
    Formats the FairValue logic human-readably for the pitch/app logic.
    """
    pv = prediction_dict['predicted_value']
    cap = prediction_dict['hard_cap']
    risk_pct = prediction_dict['risk_percentage'] * 100
    
    msg = (f"Our model predicts a baseline market value of £{pv/1e6:.1f}m. "
           f"However, after factoring a {risk_pct:.0f}% risk discount based on "
           f"the player's profile (contract/age/injury), the Risk-Adjusted "
           f"Fair Value drops. We recommend a maximal Hard Cap of £{cap/1e6:.1f}m.")
    return msg
