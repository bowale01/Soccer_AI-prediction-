# GamePredict AI Agent

An autonomous AI-powered football prediction agent that intelligently analyzes Live Score API data using machine learning to deliver quality-first predictions. The agent autonomously filters matches based on head-to-head data sufficiency and only makes predictions when confident.

## 🤖 AI Agent Capabilities

- **Autonomous Decision Making**: Intelligently filters matches without human intervention
- **Quality-First Intelligence**: Only predicts matches with sufficient head-to-head data (≥3 matches)
- **Live Data Processing**: Real-time fixture and historical data collection from Live Score API
- **Machine Learning Pipeline**: RandomForest with engineered features from H2H statistics
- **Multi-Type Predictions**: Home Win, Away Win, Draw, Over/Under Goals, Both Teams to Score
- **Confidence-Based Output**: Returns ALL confident predictions (no artificial quantity limits)
- **API Interface**: Professional REST API for serving intelligent predictions
- **Secure Operations**: Environment variable-based credential management

##  Project Structure

```
gamepredict_ai_agent/
 .env                    # API credentials (not committed)
 .env.example           # Environment variables template
 API_SETUP.md          # API configuration guide
 PROJECT_ROADMAP.md    # Development roadmap
 data/
    matches.csv       # Training data (auto-populated from API)
 src/
     data_collector.py      # Live Score API integration
     predictor.py           # ML training & prediction system
     train_ml_model.py      # Dedicated model training script
     agent.py               # FastAPI service
     test_predictor_simulation.py  # Testing with mock data
```

##  Quick Start

### 1. Environment Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/AI-Agents.git
cd AI-Agents/gamepredict_ai_agent

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. API Configuration
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your Live Score API credentials
```

### 3. Data Collection & Training
```bash
# Collect training data from Live Score API
python src/data_collector.py

# Train the ML model
python src/train_ml_model.py
```

### 4. Get Daily Predictions
```bash
# Run quality-first daily predictions
python src/predictor.py
```

### 5. Start API Service
```bash
# Launch FastAPI server
uvicorn src.agent:app --reload

# Access API documentation at http://127.0.0.1:8000/docs
```

##  Prediction System Logic

### Quality Filters Applied:
1. **H2H Requirement**: Minimum 3 head-to-head matches between teams
2. **Confidence Threshold**: Only predictions with 75% confidence
3. **Data Validation**: Skip matches with insufficient historical context

### Sample Output:
```
📊 Analyzing 50 total fixtures for H2H data quality...
✅ Arsenal vs Chelsea - 12 valid H2H matches
⏭️  NewTeam vs Another - Only 1 H2H matches (need ≥3)

🎯 Found 5 confident predictions (>75% confidence):
  ✅ 15:00 | Arsenal vs Chelsea: Over 2.5 Goals (87.3%)
  ✅ 17:30 | Liverpool vs Man City: Away Win (81.2%)
  ✅ 20:00 | Barcelona vs Real Madrid: Both Teams to Score (79.1%)
```

##  API Usage

### Get Predictions
```bash
POST /predict
{
  "home_team": "Arsenal",
  "away_team": "Chelsea"
}
```

##  Security

- API credentials stored in `.env` file (git-ignored)
- No hardcoded secrets in source code
- Environment variable validation on startup

## 🎯 AI Agent Philosophy

**Intelligent Quality over Quantity**: The AI agent autonomously decides to predict only 2 matches accurately rather than 20 poorly. It automatically filters out matches without sufficient historical data, ensuring only high-confidence predictions are delivered without human oversight.

## 🚀 Future AI Enhancements

1. **Team News/Injuries Integration** → Autonomous player news analysis if API provides data
2. **Advanced ML Ensemble** → Self-improving models combining H2H + recent form + betting odds
3. **Prediction Visualization** → Intelligent charts and trend analysis using matplotlib/Plotly
4. **Autonomous Scheduling** → Automatic daily prediction runs with cron jobs
5. **Full Web Dashboard** → Real-time updates with authentication and intelligent filtering

## 🛠️ Technology Stack

- **Core Language**: Python 3.8+
- **API Integration**: requests, Live Score API
- **Data Processing**: pandas, numpy
- **Machine Learning**: scikit-learn (RandomForest), xgboost
- **Web API**: FastAPI, uvicorn
- **Security**: python-dotenv, environment variables
- **Future ML**: TensorFlow/PyTorch for advanced models
