# GamePredict AI Agent

A minimal, local-first AI agent that predicts football match outcomes using historical data.

## Features (MVP)
- Train a baseline model (XGBoost) from a CSV (`data/matches.csv`).
- Serve predictions via FastAPI `/predict`.
- Simple team encoding and probability outputs (home/draw/away).

## Project Structure
```
gamepredict_ai_agent/
  data/
    matches.csv            # your dataset (you provide)
  src/
    train.py               # trains model -> sports_model.pkl
    agent.py               # FastAPI API service
  requirements.txt
  README.md
```

## Dataset Format
Provide `data/matches.csv` with columns:
- home_team
- away_team
- home_score
- away_score

## Quickstart
1. Create/activate your virtual environment.
2. Install deps.
3. Add your dataset.
4. Train the model.
5. Run the API.

### Commands
Install dependencies (inside your venv):
```
# Windows PowerShell
pip install -r .\gamepredict_ai_agent\requirements.txt
```

Train the model:
```
python .\gamepredict_ai_agent\src\train.py
```

Run the API:
```
uvicorn gamepredict_ai_agent.src.agent:app --reload
```

Open docs at:
- http://127.0.0.1:8000/docs

### Predict body
POST /predict
```
{
  "home_team": "Chelsea",
  "away_team": "Arsenal"
}
```

## Notes
- If `/predict` says model not loaded, ensure `sports_model.pkl` exists at project root or set `MODEL_PATH` env var to its location.
- Improve features later: head-to-head aggregates, recent form, home/away, player availability.
