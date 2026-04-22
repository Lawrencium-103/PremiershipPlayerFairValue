# FairValue Transfer Cap Estimator: Data Schema

This document outlines the CSV structure required for training the XGBoost regression model.

## Target Variable
- **`Transfer_Fee_2024_GBP`**: The inflation-adjusted transfer fee in GBP (Target variable to predict).

## Master Dataset (`train.csv` / `test.csv`)

| Column Name | Data Type | Description |
| :--- | :--- | :--- |
| `Player_ID` | Integer | Unique identifier for the player. |
| `Name` | String | Player's full name. |
| `Position` | Categorical | Primary position (e.g., CB, CM, CF). Will be One-Hot Encoded. |
| `Age` | Integer | Player's age at the time of the transfer. |
| `Nationality_Tier` | Integer | Grouped tier (Tier 1 = EU5/SA, Tier 2 = Rest of World) influencing commercial value. |
| `Current_League` | Categorical | The league the player is transferring from, mapped to a League Strength Index via UEFA coefficients. |
| **`Contract_Years_Left`** | Float | **Critical risk factor.** Years remaining on current contract (1 to 5). Heavily influences the Option Value. |
| `Minutes_2023` | Integer | Minutes played in the immediate prior season. |
| `Minutes_2022` | Integer | Minutes played in the season before the immediate prior season. |
| **`xG_90_2023`** | Float | **Key performance metric.** Expected goals per 90 minutes. |
| `xG_90_2022` | Float | Expected goals per 90 minutes in the previous season. |
| `xA_90_2023` | Float | Expected assists per 90 minutes. |
| `xA_90_2022` | Float | Expected assists per 90 minutes in the previous season. |
| `Progressive_Carries_90` | Float | Progressive carries per 90 minutes, capturing ball-progression skill. |
| **`Injury_Days_Total_24m`** | Integer | **Critical risk factor.** Total days injured in the 24 months preceding the transfer. Impacts the "Risk Score" and final Hard Cap. |
| `Transfer_Date` | Date | Date of the transfer, used to determine inflation adjustment multiplier. |

### Example Row
```csv
Player_ID,Name,Position,Age,Nationality_Tier,Current_League,Contract_Years_Left,Minutes_2023,Minutes_2022,xG_90_2023,xG_90_2022,xA_90_2023,xA_90_2022,Progressive_Carries_90,Injury_Days_Total_24m,Transfer_Fee_2024_GBP,Transfer_Date
1001,Jude Bellingham,CM,19,1,La_Liga,4,2500,3000,0.45,0.38,0.22,4.2,5,103000000,2023-06-15
1002,Kai Havertz,CF,24,1,Premier_League,3,2000,2200,0.28,0.25,0.15,3.1,10,65000000,2023-07-01
```
