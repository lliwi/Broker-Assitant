"""
Example usage of Broker Assistant API.
Demonstrates how to interact with the platform programmatically.
"""
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Base URL for API
BASE_URL = "http://localhost:5000/api"

# Example user ID (you would get this from authentication)
USER_ID = 1


def generate_sample_price_data(symbol: str, days: int = 100) -> list:
    """Generate sample OHLCV data for demonstration."""
    dates = pd.date_range(end=datetime.now(), periods=days, freq='D')
    np.random.seed(hash(symbol) % 1000)

    base_price = 100
    prices = base_price + np.random.randn(days).cumsum()

    data = []
    for i, date in enumerate(dates):
        price = prices[i]
        data.append({
            'timestamp': date.isoformat(),
            'open': float(price * (1 + np.random.uniform(-0.02, 0.02))),
            'high': float(price * (1 + np.random.uniform(0, 0.03))),
            'low': float(price * (1 - np.random.uniform(0, 0.03))),
            'close': float(price),
            'volume': int(np.random.uniform(1000000, 5000000))
        })

    return data


def example_technical_analysis():
    """Example: Perform technical analysis on an asset."""
    print("\n=== Technical Analysis Example ===")

    symbol = "AAPL"
    price_data = generate_sample_price_data(symbol, 60)

    response = requests.post(
        f"{BASE_URL}/analysis/technical/{symbol}",
        json={'price_data': price_data}
    )

    if response.status_code == 200:
        result = response.json()
        analysis = result['analysis']

        print(f"\nSymbol: {symbol}")
        print(f"\nIndicators:")
        print(f"  RSI: {analysis['indicators']['rsi']}")
        print(f"  Bollinger Bands: {analysis['indicators']['bollinger_bands']}")

        print(f"\nPatterns detected: {len(analysis['patterns'])}")
        for pattern in analysis['patterns']:
            print(f"  - {pattern['name']} ({pattern['type']}) - Confidence: {pattern['confidence']:.2%}")

        print(f"\nSignals: {len(analysis['signals'])}")
        for signal in analysis['signals']:
            print(f"  - {signal['type']}: {signal['strength']} (confidence: {signal['confidence']:.2%})")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def example_news_analysis():
    """Example: Analyze news sentiment for an asset."""
    print("\n=== News Analysis Example ===")

    symbol = "GOOGL"

    response = requests.get(
        f"{BASE_URL}/analysis/news/{symbol}",
        params={'limit': 5}
    )

    if response.status_code == 200:
        result = response.json()
        analysis = result['analysis']

        print(f"\nSymbol: {symbol}")
        print(f"Sentiment: {analysis['sentiment']}")
        print(f"Score: {analysis['score']:.2f}")
        print(f"Articles analyzed: {analysis['articles_analyzed']}")
        print(f"\nSummary: {analysis.get('summary', 'N/A')}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def example_generate_prediction():
    """Example: Generate AI prediction for an asset."""
    print("\n=== Generate Prediction Example ===")

    symbol = "MSFT"
    price_data = generate_sample_price_data(symbol, 90)

    response = requests.post(
        f"{BASE_URL}/analysis/predict/{symbol}",
        json={
            'price_data': price_data,
            'analysis_type': 'hybrid',
            'user_id': USER_ID
        }
    )

    if response.status_code == 201:
        result = response.json()
        prediction = result['prediction']

        print(f"\nSymbol: {symbol}")
        print(f"Prediction: {prediction['prediction_type']}")
        print(f"Confidence: {prediction['confidence_score']:.2%}")
        print(f"Target Price: ${prediction['target_price']:.2f}")
        print(f"Stop Loss: ${prediction['stop_loss']:.2f}")
        print(f"Time Horizon: {prediction['time_horizon']}")

        print(f"\nExplainability Factors:")
        for factor in prediction['factors']:
            print(f"  - {factor['factor_name']} ({factor['factor_type']}): {factor['description']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")


def example_portfolio_management():
    """Example: Manage portfolio positions."""
    print("\n=== Portfolio Management Example ===")

    # Create a position
    print("\nCreating new position...")
    response = requests.post(
        f"{BASE_URL}/portfolio/positions",
        json={
            'user_id': USER_ID,
            'symbol': 'TSLA',
            'asset_name': 'Tesla Inc.',
            'position_type': 'BUY',
            'quantity': 10,
            'entry_price': 250.50,
            'notes': 'Strong technical signals'
        }
    )

    if response.status_code == 201:
        position = response.json()['position']
        position_id = position['id']
        print(f"Position created: {position['symbol']} - {position['quantity']} shares @ ${position['entry_price']}")

        # Update position with current price
        print("\nUpdating position with current price...")
        requests.put(
            f"{BASE_URL}/portfolio/positions/{position_id}",
            json={'current_price': 265.75}
        )

        # Get portfolio summary
        print("\nFetching portfolio summary...")
        response = requests.get(
            f"{BASE_URL}/portfolio/summary",
            params={'user_id': USER_ID}
        )

        if response.status_code == 200:
            summary = response.json()['summary']
            print(f"\nPortfolio Summary:")
            print(f"  Total Positions: {summary['total_positions']}")
            print(f"  Open Positions: {summary['open_positions']}")
            print(f"  Total Unrealized P&L: ${summary['total_unrealized_pnl']:.2f}")


def example_add_favorites():
    """Example: Manage favorite assets."""
    print("\n=== Favorites Management Example ===")

    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'NVDA']

    for symbol in symbols:
        response = requests.post(
            f"{BASE_URL}/portfolio/favorites",
            json={
                'user_id': USER_ID,
                'symbol': symbol,
                'asset_name': f'{symbol} Corporation',
                'asset_type': 'stock',
                'risk_tolerance': 'medium',
                'investment_horizon': 'long'
            }
        )

        if response.status_code == 201:
            print(f"Added {symbol} to favorites")
        elif response.status_code == 409:
            print(f"{symbol} already in favorites")

    # Get all favorites
    response = requests.get(
        f"{BASE_URL}/portfolio/favorites",
        params={'user_id': USER_ID}
    )

    if response.status_code == 200:
        favorites = response.json()['favorites']
        print(f"\nTotal favorites: {len(favorites)}")


def example_scan_multiple_assets():
    """Example: Scan multiple assets for opportunities."""
    print("\n=== Multi-Asset Scan Example ===")

    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA']

    # Generate price data for all symbols
    price_data_dict = {}
    for symbol in symbols:
        price_data_dict[symbol] = generate_sample_price_data(symbol, 60)

    response = requests.post(
        f"{BASE_URL}/analysis/scan",
        json={
            'symbols': symbols,
            'price_data': price_data_dict
        }
    )

    if response.status_code == 200:
        result = response.json()
        opportunities = result['opportunities']

        print(f"\nFound {len(opportunities)} trading opportunities:")
        for opp in opportunities[:5]:  # Show top 5
            print(f"\n  {opp['symbol']} - {opp['signal_type']}")
            print(f"    Confidence: {opp['confidence']:.2%}")
            print(f"    Strength: {opp['strength']}")
            if opp['patterns']:
                print(f"    Patterns: {', '.join([p['name'] for p in opp['patterns']])}")


def example_get_accuracy_stats():
    """Example: Get prediction accuracy statistics."""
    print("\n=== Accuracy Statistics Example ===")

    response = requests.get(f"{BASE_URL}/analysis/accuracy")

    if response.status_code == 200:
        stats = response.json()
        print(f"\nOverall Accuracy:")
        print(f"  Total Predictions: {stats['total_predictions']}")
        print(f"  Correct Predictions: {stats['correct_predictions']}")
        print(f"  Accuracy: {stats['accuracy_percentage']:.2f}%")


if __name__ == '__main__':
    print("=" * 60)
    print("Broker Assistant API Usage Examples")
    print("=" * 60)

    try:
        # Run examples
        example_technical_analysis()
        example_news_analysis()
        example_generate_prediction()
        example_portfolio_management()
        example_add_favorites()
        example_scan_multiple_assets()
        example_get_accuracy_stats()

        print("\n" + "=" * 60)
        print("Examples completed successfully!")
        print("=" * 60)

    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to API. Make sure the server is running:")
        print("  docker-compose up")
    except Exception as e:
        print(f"\nError: {e}")
