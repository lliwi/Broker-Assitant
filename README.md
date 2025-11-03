# InsightFlow

AI-powered stock investment assistant platform built with Flask. Provides intelligent buy/sell suggestions based on automated technical analysis and quantitative fundamental analysis.

## Features

### 🤖 AI Investment Engine
- **Automated Technical Analysis**: Pattern recognition (head & shoulders, double bottom, etc.) with 80%+ accuracy target
- **Technical Indicators**: Bollinger Bands, RSI, Stochastic Oscillator, MACD
- **News Sentiment Analysis**: NLP-based fundamental analysis using Claude AI
- **Explainable AI (XAI)**: All predictions include justification and triggering factors

### 📊 Portfolio Management
- Track open/closed positions with real-time P&L calculations
- Favorite assets watchlist (generates labeled data for ML personalization)
- AES-256 encryption for sensitive portfolio data

### 📈 Real-Time Data
- Kafka-based streaming architecture for low-latency price updates
- WebSocket distribution to browser clients
- Redis caching for sub-millisecond performance

### 🔄 Continuous Learning
- Historical logging of all predictions (independent of user execution)
- Backtesting and accuracy tracking
- ARIMA-LSTM hybrid models for time series forecasting (planned)

## Architecture

- **Backend**: Flask (Python 3.11+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Cache**: Redis
- **Streaming**: Apache Kafka
- **Real-time**: Flask-SocketIO (WebSocket)
- **AI/ML**: Claude (Anthropic), TA-Lib, scikit-learn, TensorFlow
- **Deployment**: Docker Compose

## Quick Start

### Prerequisites
- Docker and Docker Compose
- API keys for:
  - Anthropic (Claude AI)
  - Financial data provider (Alpha Vantage, Finnhub, etc.)
  - News API

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd BrokerAssistant
```

2. Create environment file:
```bash
cp .env.example .env
```

3. Edit `.env` and add your API keys:
```bash
ANTHROPIC_API_KEY=your-anthropic-key
ALPHA_VANTAGE_API_KEY=your-alpha-vantage-key
FINNHUB_API_KEY=your-finnhub-key
NEWS_API_KEY=your-news-api-key

# Generate encryption key for database
DB_ENCRYPTION_KEY=$(python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")
```

4. Start the application:
```bash
docker-compose up --build
```

The application will be available at `http://localhost:5000`

### Services
- Flask API: `http://localhost:5000`
- PostgreSQL: `localhost:5432`
- Redis: `localhost:6379`
- Kafka: `localhost:9092`

## API Endpoints

### Portfolio Management
```
GET    /api/portfolio/positions          - Get user positions
POST   /api/portfolio/positions          - Create new position
PUT    /api/portfolio/positions/:id      - Update position
DELETE /api/portfolio/positions/:id      - Delete position

GET    /api/portfolio/favorites          - Get favorite assets
POST   /api/portfolio/favorites          - Add favorite
PUT    /api/portfolio/favorites/:id      - Update favorite
DELETE /api/portfolio/favorites/:id      - Remove favorite

GET    /api/portfolio/summary            - Get portfolio summary with P&L
```

### Analysis & Predictions
```
POST   /api/analysis/technical/:symbol   - Technical analysis
GET    /api/analysis/news/:symbol        - News sentiment analysis
POST   /api/analysis/predict/:symbol     - Generate AI prediction
POST   /api/analysis/scan                - Scan multiple assets

GET    /api/analysis/predictions         - Get prediction history
GET    /api/analysis/predictions/:id     - Get specific prediction
POST   /api/analysis/predictions/:id/execute - Mark prediction as executed
POST   /api/analysis/predictions/verify  - Verify past predictions
GET    /api/analysis/accuracy            - Get accuracy statistics

POST   /api/analysis/fundamental/screen  - Screen by fundamentals
```

### WebSocket Events
```
connect                    - Client connection
subscribe_symbol          - Subscribe to symbol updates
unsubscribe_symbol        - Unsubscribe from symbol
subscribe_portfolio       - Subscribe to multiple symbols
price_update              - Real-time price update (broadcast)
```

## Development

### Running Tests
```bash
docker-compose exec app pytest
```

### Database Migrations
```bash
# Create migration
docker-compose exec app flask db migrate -m "Description"

# Apply migration
docker-compose exec app flask db upgrade
```

### Code Formatting
```bash
docker-compose exec app black .
docker-compose exec app flake8
```

## Configuration

Key configuration options in `config/config.py`:

- `MAX_ASSETS_SCAN`: Maximum assets to scan simultaneously (default: 500)
- `PATTERN_CONFIDENCE_THRESHOLD`: Minimum confidence for pattern signals (default: 0.8)
- `CACHE_TTL_SECONDS`: Redis cache TTL (default: 300)
- `RSI_PERIOD`: RSI calculation period (default: 14)
- `BOLLINGER_PERIOD`: Bollinger Bands period (default: 20)
- `STOCHASTIC_PERIOD`: Stochastic oscillator period (default: 14)

## Security

- **Data at Rest**: AES-256 encryption for sensitive portfolio data
- **Data in Transit**: TLS/SSL for all API communications
- **Secrets Management**: Environment variables (never commit `.env`)

## Project Structure

```
BrokerAssistant/
├── app/
│   ├── __init__.py           # Flask app factory
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py
│   │   ├── portfolio.py
│   │   └── prediction.py
│   ├── routes/               # API endpoints
│   │   ├── portfolio.py
│   │   ├── analysis.py
│   │   └── websocket.py
│   ├── services/             # Business logic
│   │   ├── technical_analysis.py
│   │   ├── news_analysis.py
│   │   ├── prediction_service.py
│   │   └── kafka_service.py
│   └── utils/                # Utilities
│       ├── cache.py
│       └── encryption.py
├── config/
│   └── config.py             # Configuration
├── tests/                    # Test suite
├── docker-compose.yml        # Docker orchestration
├── Dockerfile                # Container definition
├── requirements.txt          # Python dependencies
└── run.py                    # Application entry point
```

## Documentation

For detailed architecture and functional specifications, see [BrokerAssistant.md](BrokerAssistant.md).

## License

[Your License Here]

## Contributing

[Contributing Guidelines]
