# Quick Start Guide - InsightFlow

Get InsightFlow up and running in 5 minutes!

## Prerequisites

- Docker and Docker Compose installed
- API keys for AI and financial data services

## Installation Steps

### 1. Clone and Setup

```bash
cd BrokerAssistant
cp .env.example .env
```

### 2. Configure API Keys

Edit `.env` and add your API keys:

```bash
# Required for AI analysis
ANTHROPIC_API_KEY=sk-ant-...

# Required for financial data
ALPHA_VANTAGE_API_KEY=your-key
FINNHUB_API_KEY=your-key
NEWS_API_KEY=your-key

# Generate encryption key
DB_ENCRYPTION_KEY=$(python scripts/generate_encryption_key.py)
```

### 3. Start Application

```bash
# Using Makefile (recommended)
make init

# Or manually
docker-compose up --build
```

Wait for all services to start (~30 seconds).

## Verify Installation

### Check Services

```bash
# Check if all containers are running
docker-compose ps

# Expected output:
# insightflow-app      running
# insightflow-db       running
# insightflow-redis    running
# insightflow-kafka    running
# insightflow-zookeeper running
```

### Test API

```bash
curl http://localhost:5000/api/portfolio/positions?user_id=1
```

Expected: `{"positions": [], "count": 0}`

## Try the Examples

Run the example script to see all features:

```bash
docker-compose exec app python scripts/example_usage.py
```

This demonstrates:
- Technical analysis with indicators and patterns
- News sentiment analysis
- AI prediction generation with explainability
- Portfolio management (positions and favorites)
- Multi-asset scanning
- Accuracy statistics

## Common Tasks

### View Logs

```bash
make logs

# Or for specific service
docker-compose logs -f app
```

### Run Tests

```bash
make test
```

### Access Database

```bash
make db-shell
```

### Access Redis

```bash
make redis-cli
```

### Stop Services

```bash
make down
```

## Next Steps

1. **Read the API documentation** in [README.md](README.md)
2. **Explore the codebase** structure in [CLAUDE.md](CLAUDE.md)
3. **Review the architecture** in [BrokerAssistant.md](BrokerAssistant.md)

## API Endpoints Overview

### Portfolio Management
```
GET  /api/portfolio/positions       # List positions
POST /api/portfolio/positions       # Create position
GET  /api/portfolio/favorites       # List favorites
GET  /api/portfolio/summary         # Portfolio summary
```

### Analysis & Predictions
```
POST /api/analysis/technical/:symbol   # Technical analysis
GET  /api/analysis/news/:symbol        # News sentiment
POST /api/analysis/predict/:symbol     # Generate prediction
POST /api/analysis/scan                # Scan multiple assets
GET  /api/analysis/accuracy            # Get accuracy stats
```

### WebSocket (Real-time)
```javascript
// Connect to WebSocket
const socket = io('http://localhost:5000');

// Subscribe to price updates
socket.emit('subscribe_symbol', {symbol: 'AAPL'});

// Receive updates
socket.on('price_update', (data) => {
  console.log('Price update:', data);
});
```

## Troubleshooting

### Port Already in Use

If port 5000 is in use:
```bash
# Edit docker-compose.yml
ports:
  - "5001:5000"  # Change external port
```

### Kafka Connection Issues

Wait for Kafka to fully initialize (~20 seconds):
```bash
docker-compose logs -f kafka
```

Look for: "INFO [KafkaServer id=1] started"

### Database Connection Error

Reset database:
```bash
make clean
make init
```

### Missing API Keys

Some features require API keys:
- **Technical Analysis**: Works without keys (uses TA-Lib)
- **News Analysis**: Requires NEWS_API_KEY and FINNHUB_API_KEY
- **AI Predictions**: Requires ANTHROPIC_API_KEY

## Development Mode

Run with auto-reload for development:

```bash
make dev
```

This starts all services in foreground with live logs.

## Performance Tips

1. **Redis Caching**: Automatically reduces API calls
2. **Cache TTL**: Adjust `CACHE_TTL_SECONDS` in `.env` (default: 300s)
3. **Max Assets**: Limit concurrent scans with `MAX_ASSETS_SCAN` (default: 500)

## Getting Help

- Review [README.md](README.md) for detailed documentation
- Check [CLAUDE.md](CLAUDE.md) for development guidelines
- See [BrokerAssistant.md](BrokerAssistant.md) for architecture details

---

**Ready to go!** Your InsightFlow instance is now running at `http://localhost:5000`
