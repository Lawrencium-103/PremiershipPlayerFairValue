# FairValue Transfer Cap Estimator: Technical Stack Specification

| Component | Technology | Justification |
| :--- | :--- | :--- |
| **Language** | Python 3.9+ | Industry standard for Data Science and Machine Learning. |
| **Data Scraping** | Requests, BeautifulSoup4, Selenium | Free, effective for scraping unstructured data from sources like Transfermarkt and FBref. |
| **Data Manipulation** | Pandas, NumPy | Best in class for handling tabular time-series data and vectorized operations. |
| **Machine Learning** | XGBoost, Scikit-Learn | Gradient boosting is state-of-the-art for tabular data; inherently handles non-linear relationships and missing data robustly. |
| **Visualization** | Plotly, Streamlit | Enables interactive, web-ready charts (gauges, waterfall plots) without JS overhead. |
| **Explainability** | SHAP | Gold standard for model interpretation, allows breakdown of exact features influencing the price cap. |
| **Hosting** | Hugging Face Spaces (CPU Basic) | Free, permanent public URL, supports Streamlit natively and enables rapid MVP deployment. |
| **Version Control** | Git / GitHub (Free) | Essential for code collaboration and proving project credibility. |
