# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Broker Assistant** - A Flask-based web application for stock investment assistance powered by AI. The platform provides buy/sell suggestions based on two pillars:

1. **Automated Technical Analysis**: Pattern recognition in candlestick charts using ML models
2. **Quantitative Fundamental Analysis**: News sentiment analysis and fundamental data screening

## Architecture Stack (Planned)

### Backend
- **Framework**: Flask (Python)
- **AI/ML Models**: Claude, OpenAI, or Deepseek for NLP and market analysis
- **Pattern Recognition**: ML models for detecting chart patterns (head & shoulders, double bottom, bullish flags, etc.)
- **Time Series Forecasting**: Hybrid ARIMA-LSTM models for learning from historical predictions
- **Real-time Data Streaming**: Apache Kafka for low-latency price data distribution
- **Database**: PostgreSQL or MySQL for transactional data (user positions, favorites)
- **Caching**: Redis for high-performance data retrieval
- **WebSockets**: Real-time price updates to browser clients

### Frontend
- **Visualization**: Interactive candlestick charts using Highcharts or Chart.js
- **Communication**: WebSocket connections for real-time data

### Security
- **Data at Rest**: AES-256 encryption for database storage
- **Data in Transit**: TLS/SSL/HTTPS for all network communications

## Core Functional Modules

### 1. AI Investment Suggestions Engine

**Technical Analysis Module**:
- Pattern detection with 80%+ accuracy target
- Technical indicators integration:
  - Bollinger Bands (volatility and reversions)
  - RSI (overbought/oversold conditions)
  - Stochastic Oscillator (market extremes)
- Real-time scanning of hundreds of assets

**News Analysis Module**:
- News ingestion via specialized APIs
- Algorithmic filtering based on:
  - Low P/E ratios
  - Price below book value
  - Above-average dividend yields

### 2. Portfolio Management
- Open positions tracking (buy/sell operations)
- Favorite assets management (generates labeled data for ML personalization)

### 3. Continuous Learning & Backtesting
- Historical logging of all entry/exit suggestions (regardless of user execution)
- Suggestions must include explainability (XAI) linking predictions to technical/fundamental factors
- ARIMA-LSTM hybrid models learn from prediction performance

## Development Guidelines

### Data Flow Architecture
- Kafka streams → WebSocket distribution → Browser client
- Redis caching layer between APIs and chart rendering
- Sub-millisecond read performance for historical data

### ML Model Integration
- All suggestions must be explainable (link to triggering factors)
- Store predictions independently of user actions for training dataset
- Implement feedback loop from prediction outcomes to model refinement

### Database Design
- Separate transactional DB (positions, favorites) from time-series data
- Design for low-latency queries on portfolio operations
- Historical predictions table must capture: timestamp, asset, signal type, confidence, triggering factors

## Key Technical Considerations

1. **Low Latency**: Critical for real-time chart rendering and price updates
2. **Scalability**: Architecture must handle hundreds of simultaneous asset scans
3. **Data Integrity**: Kafka ensures durability and reliability of price streams
4. **Cost Optimization**: Redis caching reduces paid API calls
5. **User Trust**: XAI (Explainable AI) is mandatory for all suggestions

## Development Commands

### Quick Start
```bash
# First time setup
make init

# Start development server
make up

# View logs
make logs

# Stop services
make down
```

### Common Commands
```bash
# Run tests
make test

# Open shell in app container
make shell

# Database migrations
make migrate msg="Add new field"
make upgrade

# Code formatting and linting
make format
make lint

# View container stats
make stats
```

### Docker Compose Commands
```bash
# Build and start
docker-compose up --build

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f app

# Execute command in container
docker-compose exec app flask db upgrade
docker-compose exec app pytest
```

### Manual Setup
```bash
# Generate encryption key
python scripts/generate_encryption_key.py

# Run example usage
docker-compose exec app python scripts/example_usage.py
```

## Project Structure

```
app/
├── models/              # SQLAlchemy models (User, Position, FavoriteAsset, Prediction)
├── routes/              # API endpoints (portfolio, analysis, websocket)
├── services/            # Business logic (technical_analysis, news_analysis, prediction_service, kafka_service)
└── utils/               # Utilities (cache, encryption)

config/                  # Configuration classes
scripts/                 # Utility scripts (example_usage, generate_encryption_key)
tests/                   # Test suite
```

## Important Implementation Details

### Models
- **Position**: Encrypted notes field, automatic P&L calculation
- **Prediction**: All predictions stored for backtesting, includes XAI factors
- **PredictionFactor**: Explainability factors linking predictions to technical/fundamental triggers

### Services
- **TechnicalAnalysisService**: TA-Lib integration for indicators and pattern detection
- **NewsAnalysisService**: Claude AI integration for sentiment analysis
- **PredictionService**: Combines technical + fundamental analysis with XAI
- **KafkaService**: Real-time price streaming with producer/consumer pattern

### API Endpoints
- Portfolio: `/api/portfolio/positions`, `/api/portfolio/favorites`, `/api/portfolio/summary`
- Analysis: `/api/analysis/technical/:symbol`, `/api/analysis/news/:symbol`, `/api/analysis/predict/:symbol`
- Predictions: `/api/analysis/predictions`, `/api/analysis/accuracy`
- WebSocket: Subscribe to price updates via `subscribe_symbol` event

## Language Note

The original specification document (BrokerAssistant.md) is written in Spanish. When collaborating with stakeholders, confirm language preference for code comments, documentation, and variable naming conventions.
