"""
Tests for technical analysis service.
"""
import pytest
import pandas as pd
import numpy as np
from app.services.technical_analysis import TechnicalAnalysisService


@pytest.fixture
def sample_price_data():
    """Generate sample OHLCV data for testing."""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)

    data = {
        'open': 100 + np.random.randn(100).cumsum(),
        'high': 102 + np.random.randn(100).cumsum(),
        'low': 98 + np.random.randn(100).cumsum(),
        'close': 100 + np.random.randn(100).cumsum(),
        'volume': np.random.randint(1000000, 5000000, 100)
    }

    return pd.DataFrame(data, index=dates)


def test_technical_analysis_service_initialization(app):
    """Test service initialization."""
    with app.app_context():
        service = TechnicalAnalysisService()
        assert service.confidence_threshold > 0


def test_calculate_indicators(app, sample_price_data):
    """Test indicator calculations."""
    with app.app_context():
        service = TechnicalAnalysisService()
        indicators = service._calculate_indicators(sample_price_data)

        # Check that all indicators are present
        assert 'bollinger_bands' in indicators
        assert 'rsi' in indicators
        assert 'stochastic' in indicators
        assert 'macd' in indicators


def test_detect_patterns(app, sample_price_data):
    """Test pattern detection."""
    with app.app_context():
        service = TechnicalAnalysisService()
        patterns = service._detect_patterns(sample_price_data)

        # Patterns should be a list (may be empty)
        assert isinstance(patterns, list)


def test_analyze_asset(app, sample_price_data):
    """Test complete asset analysis."""
    with app.app_context():
        service = TechnicalAnalysisService()
        result = service.analyze_asset('AAPL', sample_price_data)

        assert 'symbol' in result
        assert 'indicators' in result
        assert 'patterns' in result
        assert 'signals' in result
        assert result['symbol'] == 'AAPL'


def test_bollinger_interpretation(app):
    """Test Bollinger Bands interpretation."""
    with app.app_context():
        service = TechnicalAnalysisService()

        # Price at lower band - oversold
        assert service._interpret_bollinger(95, 110, 90) == 'oversold'

        # Price at upper band - overbought
        assert service._interpret_bollinger(110, 110, 90) == 'overbought'

        # Price in middle - neutral
        assert service._interpret_bollinger(100, 110, 90) == 'neutral'


def test_rsi_interpretation(app):
    """Test RSI interpretation."""
    with app.app_context():
        service = TechnicalAnalysisService()

        assert service._interpret_rsi(25) == 'oversold'
        assert service._interpret_rsi(75) == 'overbought'
        assert service._interpret_rsi(50) == 'neutral'


def test_stochastic_interpretation(app):
    """Test Stochastic Oscillator interpretation."""
    with app.app_context():
        service = TechnicalAnalysisService()

        assert service._interpret_stochastic(15, 18) == 'oversold'
        assert service._interpret_stochastic(85, 82) == 'overbought'
        assert service._interpret_stochastic(60, 55) == 'bullish_crossover'
        assert service._interpret_stochastic(40, 45) == 'bearish_crossover'
