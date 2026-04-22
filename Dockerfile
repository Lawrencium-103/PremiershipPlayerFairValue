FROM python:3.11-slim

WORKDIR /app

# Install OS dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first (Docker cache layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy only what the API needs at runtime
# (raw CSVs are gitignored and NOT copied — only the processed outputs)
COPY api/         ./api/
COPY src/         ./src/
COPY fairvalue_xgboost.json .
COPY data/processed/app_features.csv ./data/processed/app_features.csv

# Hugging Face Spaces requires port 7860
EXPOSE 7860

# Uvicorn with 2 workers for concurrent requests
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "7860", "--workers", "2"]
