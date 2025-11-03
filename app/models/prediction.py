"""
Prediction models for AI suggestions and continuous learning.
Stores all predictions for backtesting and model improvement.
"""
from datetime import datetime
from app import db


class Prediction(db.Model):
    """
    Historical record of all AI predictions for backtesting.
    Critical for continuous learning and model improvement.
    """

    __tablename__ = 'predictions'

    id = db.Column(db.Integer, primary_key=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    asset_name = db.Column(db.String(200))

    # Prediction details
    prediction_type = db.Column(db.String(20), nullable=False, index=True)  # 'BUY', 'SELL', 'HOLD'
    confidence_score = db.Column(db.Numeric(5, 4), nullable=False)  # 0.0000 to 1.0000
    target_price = db.Column(db.Numeric(15, 4))
    stop_loss = db.Column(db.Numeric(15, 4))
    time_horizon = db.Column(db.String(20))  # short, medium, long

    # Analysis source
    analysis_type = db.Column(db.String(50), nullable=False)  # 'technical', 'fundamental', 'hybrid'
    model_version = db.Column(db.String(50))  # Track which model version made the prediction

    # Market context at prediction time
    price_at_prediction = db.Column(db.Numeric(15, 4), nullable=False)
    market_condition = db.Column(db.String(50))  # bullish, bearish, sideways
    volatility_index = db.Column(db.Numeric(10, 4))

    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime)

    # Outcome tracking (for backtesting)
    actual_outcome = db.Column(db.String(20))  # 'correct', 'incorrect', 'pending'
    outcome_verified_at = db.Column(db.DateTime)
    price_at_verification = db.Column(db.Numeric(15, 4))
    accuracy_score = db.Column(db.Numeric(5, 4))  # How accurate was the prediction

    # User interaction
    user_executed = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), index=True)

    # Relationships
    factors = db.relationship('PredictionFactor', backref='prediction', lazy='dynamic', cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Prediction {self.symbol} - {self.prediction_type} ({self.confidence_score})>'

    def to_dict(self, include_factors=True):
        """Convert prediction to dictionary."""
        result = {
            'id': self.id,
            'symbol': self.symbol,
            'asset_name': self.asset_name,
            'prediction_type': self.prediction_type,
            'confidence_score': float(self.confidence_score),
            'target_price': float(self.target_price) if self.target_price else None,
            'stop_loss': float(self.stop_loss) if self.stop_loss else None,
            'time_horizon': self.time_horizon,
            'analysis_type': self.analysis_type,
            'model_version': self.model_version,
            'price_at_prediction': float(self.price_at_prediction),
            'market_condition': self.market_condition,
            'created_at': self.created_at.isoformat(),
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'actual_outcome': self.actual_outcome,
            'accuracy_score': float(self.accuracy_score) if self.accuracy_score else None,
            'user_executed': self.user_executed
        }

        if include_factors:
            result['factors'] = [f.to_dict() for f in self.factors]

        return result


class PredictionFactor(db.Model):
    """
    Explainability factors for predictions (XAI - Explainable AI).
    Links predictions to specific technical or fundamental factors.
    """

    __tablename__ = 'prediction_factors'

    id = db.Column(db.Integer, primary_key=True)
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False, index=True)

    # Factor details
    factor_type = db.Column(db.String(50), nullable=False)  # 'pattern', 'indicator', 'news', 'fundamental'
    factor_name = db.Column(db.String(100), nullable=False)  # e.g., 'RSI', 'Head and Shoulders', 'P/E Ratio'
    factor_value = db.Column(db.String(200))  # The actual value that triggered the factor
    weight = db.Column(db.Numeric(5, 4))  # How much this factor influenced the prediction (0-1)
    description = db.Column(db.Text)  # Human-readable explanation

    # Technical indicator specifics
    indicator_period = db.Column(db.Integer)
    indicator_threshold = db.Column(db.Numeric(10, 4))

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f'<PredictionFactor {self.factor_name}>'

    def to_dict(self):
        """Convert factor to dictionary."""
        return {
            'id': self.id,
            'factor_type': self.factor_type,
            'factor_name': self.factor_name,
            'factor_value': self.factor_value,
            'weight': float(self.weight) if self.weight else None,
            'description': self.description,
            'indicator_period': self.indicator_period,
            'indicator_threshold': float(self.indicator_threshold) if self.indicator_threshold else None
        }
