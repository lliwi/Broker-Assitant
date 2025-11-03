"""
Seed database with sample data for development and testing.
Creates sample users, positions, favorites, and predictions.
"""
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.models.user import User
from app.models.portfolio import Position, FavoriteAsset
from app.models.prediction import Prediction, PredictionFactor
from datetime import datetime, timedelta
import random


def create_sample_users():
    """Create sample users."""
    print("Creating sample users...")

    users = [
        User(username='demo', email='demo@insightflow.com', password_hash='hashed_password_1'),
        User(username='trader1', email='trader1@insightflow.com', password_hash='hashed_password_2'),
        User(username='investor', email='investor@insightflow.com', password_hash='hashed_password_3'),
    ]

    for user in users:
        db.session.add(user)

    db.session.commit()
    print(f"Created {len(users)} users")
    return users


def create_sample_positions(users):
    """Create sample positions."""
    print("Creating sample positions...")

    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX']
    positions = []

    for user in users[:2]:  # First 2 users have positions
        # Create 3-5 positions per user
        num_positions = random.randint(3, 5)

        for _ in range(num_positions):
            symbol = random.choice(symbols)
            position_type = random.choice(['BUY', 'SELL'])
            entry_price = random.uniform(50, 500)
            quantity = random.randint(1, 100)
            is_open = random.choice([True, True, False])  # 2/3 open

            position = Position(
                user_id=user.id,
                symbol=symbol,
                asset_name=f'{symbol} Corporation',
                position_type=position_type,
                quantity=quantity,
                entry_price=entry_price,
                current_price=entry_price * random.uniform(0.85, 1.15),  # ±15%
                opened_at=datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                is_open=is_open
            )

            if not is_open:
                position.closed_at = datetime.utcnow() - timedelta(days=random.randint(1, 30))

            position.calculate_pnl()
            positions.append(position)
            db.session.add(position)

    db.session.commit()
    print(f"Created {len(positions)} positions")
    return positions


def create_sample_favorites(users):
    """Create sample favorite assets."""
    print("Creating sample favorite assets...")

    symbols = {
        'AAPL': 'Apple Inc.',
        'GOOGL': 'Alphabet Inc.',
        'MSFT': 'Microsoft Corporation',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'NVDA': 'NVIDIA Corporation',
        'META': 'Meta Platforms Inc.',
        'JPM': 'JPMorgan Chase & Co.',
        'V': 'Visa Inc.',
        'WMT': 'Walmart Inc.'
    }

    favorites = []

    for user in users:
        # Each user has 5-8 favorites
        num_favorites = random.randint(5, 8)
        user_symbols = random.sample(list(symbols.keys()), num_favorites)

        for symbol in user_symbols:
            favorite = FavoriteAsset(
                user_id=user.id,
                symbol=symbol,
                asset_name=symbols[symbol],
                asset_type='stock',
                interest_reason=random.choice([
                    'Strong growth potential',
                    'Solid fundamentals',
                    'Technical breakout pattern',
                    'Dividend yield',
                    'Market leader'
                ]),
                risk_tolerance=random.choice(['low', 'medium', 'high']),
                investment_horizon=random.choice(['short', 'medium', 'long']),
                added_at=datetime.utcnow() - timedelta(days=random.randint(1, 180)),
                view_count=random.randint(0, 50)
            )

            favorites.append(favorite)
            db.session.add(favorite)

    db.session.commit()
    print(f"Created {len(favorites)} favorite assets")
    return favorites


def create_sample_predictions():
    """Create sample predictions with factors."""
    print("Creating sample predictions...")

    symbols = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'NVDA', 'META', 'NFLX', 'JPM', 'V']
    predictions = []

    for _ in range(20):  # 20 sample predictions
        symbol = random.choice(symbols)
        prediction_type = random.choice(['BUY', 'SELL', 'HOLD'])
        confidence = random.uniform(0.6, 0.95)
        price = random.uniform(50, 500)

        prediction = Prediction(
            symbol=symbol,
            asset_name=f'{symbol} Corporation',
            prediction_type=prediction_type,
            confidence_score=confidence,
            target_price=price * (1.1 if prediction_type == 'BUY' else 0.9),
            stop_loss=price * (0.95 if prediction_type == 'BUY' else 1.05),
            time_horizon=random.choice(['short', 'medium', 'long']),
            analysis_type=random.choice(['technical', 'fundamental', 'hybrid']),
            model_version='v1.0',
            price_at_prediction=price,
            market_condition=random.choice(['bullish', 'bearish', 'sideways']),
            created_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
            expires_at=datetime.utcnow() + timedelta(days=random.randint(7, 90)),
            actual_outcome=random.choice(['pending', 'correct', 'incorrect']),
            user_executed=random.choice([True, False])
        )

        # Set accuracy for non-pending outcomes
        if prediction.actual_outcome != 'pending':
            prediction.accuracy_score = random.uniform(0.6, 0.95) if prediction.actual_outcome == 'correct' else random.uniform(0.3, 0.6)
            prediction.outcome_verified_at = datetime.utcnow() - timedelta(days=random.randint(0, 15))

        predictions.append(prediction)
        db.session.add(prediction)
        db.session.flush()  # Get prediction ID

        # Add factors
        factors_data = [
            {
                'factor_type': 'indicator',
                'factor_name': 'RSI',
                'factor_value': str(random.uniform(30, 70)),
                'weight': 0.2,
                'description': f"RSI indicates {'oversold' if prediction_type == 'BUY' else 'overbought'} conditions"
            },
            {
                'factor_type': 'indicator',
                'factor_name': 'MACD',
                'factor_value': 'bullish' if prediction_type == 'BUY' else 'bearish',
                'weight': 0.25,
                'description': f"MACD showing {'bullish' if prediction_type == 'BUY' else 'bearish'} crossover"
            },
            {
                'factor_type': 'pattern',
                'factor_name': random.choice(['Head and Shoulders', 'Double Bottom', 'Triangle']),
                'factor_value': prediction_type.lower(),
                'weight': 0.3,
                'description': f"Chart pattern suggests {prediction_type.lower()} signal"
            },
            {
                'factor_type': 'news',
                'factor_name': 'News Sentiment',
                'factor_value': 'positive' if prediction_type == 'BUY' else 'negative',
                'weight': 0.25,
                'description': f"Recent news sentiment is {'positive' if prediction_type == 'BUY' else 'negative'}"
            }
        ]

        for factor_data in factors_data:
            factor = PredictionFactor(
                prediction_id=prediction.id,
                **factor_data
            )
            db.session.add(factor)

    db.session.commit()
    print(f"Created {len(predictions)} predictions with factors")
    return predictions


def seed_database():
    """Main function to seed database with sample data."""
    print("=" * 60)
    print("Seeding InsightFlow Database with Sample Data")
    print("=" * 60)

    app = create_app('development')

    with app.app_context():
        # Check if data already exists
        if User.query.first():
            print("\nDatabase already contains data!")
            response = input("Do you want to clear and re-seed? (yes/no): ")
            if response.lower() != 'yes':
                print("Aborted.")
                return

            print("\nClearing existing data...")
            db.drop_all()
            db.create_all()
            print("Database cleared.")

        print("\nCreating sample data...\n")

        users = create_sample_users()
        positions = create_sample_positions(users)
        favorites = create_sample_favorites(users)
        predictions = create_sample_predictions()

        print("\n" + "=" * 60)
        print("Database Seeding Complete!")
        print("=" * 60)
        print(f"\nCreated:")
        print(f"  - {len(users)} users")
        print(f"  - {len(positions)} positions")
        print(f"  - {len(favorites)} favorite assets")
        print(f"  - {len(predictions)} predictions")
        print("\nSample credentials:")
        print("  Username: demo")
        print("  Username: trader1")
        print("  Username: investor")
        print("\n(Note: Authentication not implemented yet)")


if __name__ == '__main__':
    seed_database()
