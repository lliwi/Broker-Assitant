"""
Technical Analysis Service with pattern recognition and indicators.
Implements automated technical analysis with 80%+ accuracy target.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import talib
from flask import current_app

from app.utils.cache import cache_get, cache_set, get_analysis_cache_key


class TechnicalAnalysisService:
    """
    Service for automated technical analysis including:
    - Chart pattern recognition (head & shoulders, double bottom, etc.)
    - Technical indicators (Bollinger Bands, RSI, Stochastic)
    """

    def __init__(self):
        self.confidence_threshold = current_app.config['PATTERN_CONFIDENCE_THRESHOLD']

    def analyze_asset(self, symbol: str, price_data: pd.DataFrame) -> Dict:
        """
        Perform complete technical analysis on an asset.

        Args:
            symbol: Asset symbol
            price_data: DataFrame with OHLCV data (open, high, low, close, volume)

        Returns:
            Dictionary with analysis results and signals
        """
        # Check cache first
        cache_key = get_analysis_cache_key(symbol, 'technical')
        cached = cache_get(cache_key)
        if cached:
            return cached

        results = {
            'symbol': symbol,
            'indicators': self._calculate_indicators(price_data),
            'patterns': self._detect_patterns(price_data),
            'signals': []
        }

        # Generate trading signals based on indicators and patterns
        results['signals'] = self._generate_signals(results['indicators'], results['patterns'])

        # Cache results
        cache_set(cache_key, results, ttl=300)  # 5 minutes

        return results

    def _calculate_indicators(self, df: pd.DataFrame) -> Dict:
        """
        Calculate technical indicators.

        Args:
            df: OHLCV DataFrame

        Returns:
            Dictionary with indicator values
        """
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values

        indicators = {}

        # Bollinger Bands
        try:
            period = current_app.config.get('BOLLINGER_PERIOD', 20)
            upper, middle, lower = talib.BBANDS(
                close,
                timeperiod=period,
                nbdevup=2,
                nbdevdn=2,
                matype=0
            )
            indicators['bollinger_bands'] = {
                'upper': float(upper[-1]) if not np.isnan(upper[-1]) else None,
                'middle': float(middle[-1]) if not np.isnan(middle[-1]) else None,
                'lower': float(lower[-1]) if not np.isnan(lower[-1]) else None,
                'current_price': float(close[-1]),
                'signal': self._interpret_bollinger(close[-1], upper[-1], lower[-1])
            }
        except Exception as e:
            current_app.logger.error(f"Bollinger Bands calculation error: {str(e)}")
            indicators['bollinger_bands'] = None

        # RSI (Relative Strength Index)
        try:
            rsi_period = current_app.config.get('RSI_PERIOD', 14)
            rsi = talib.RSI(close, timeperiod=rsi_period)
            indicators['rsi'] = {
                'value': float(rsi[-1]) if not np.isnan(rsi[-1]) else None,
                'signal': self._interpret_rsi(rsi[-1])
            }
        except Exception as e:
            current_app.logger.error(f"RSI calculation error: {str(e)}")
            indicators['rsi'] = None

        # Stochastic Oscillator
        try:
            stoch_period = current_app.config.get('STOCHASTIC_PERIOD', 14)
            slowk, slowd = talib.STOCH(
                high, low, close,
                fastk_period=stoch_period,
                slowk_period=3,
                slowk_matype=0,
                slowd_period=3,
                slowd_matype=0
            )
            indicators['stochastic'] = {
                'k': float(slowk[-1]) if not np.isnan(slowk[-1]) else None,
                'd': float(slowd[-1]) if not np.isnan(slowd[-1]) else None,
                'signal': self._interpret_stochastic(slowk[-1], slowd[-1])
            }
        except Exception as e:
            current_app.logger.error(f"Stochastic calculation error: {str(e)}")
            indicators['stochastic'] = None

        # MACD
        try:
            macd, signal, hist = talib.MACD(close, fastperiod=12, slowperiod=26, signalperiod=9)
            indicators['macd'] = {
                'macd': float(macd[-1]) if not np.isnan(macd[-1]) else None,
                'signal': float(signal[-1]) if not np.isnan(signal[-1]) else None,
                'histogram': float(hist[-1]) if not np.isnan(hist[-1]) else None,
                'trend': self._interpret_macd(macd[-1], signal[-1])
            }
        except Exception as e:
            current_app.logger.error(f"MACD calculation error: {str(e)}")
            indicators['macd'] = None

        return indicators

    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect chart patterns using TA-Lib pattern recognition.

        Args:
            df: OHLCV DataFrame

        Returns:
            List of detected patterns with confidence scores
        """
        patterns = []
        open_prices = df['open'].values
        high = df['high'].values
        low = df['low'].values
        close = df['close'].values

        # Pattern recognition functions from TA-Lib
        pattern_functions = {
            'CDLENGULFING': 'Engulfing Pattern',
            'CDLHAMMER': 'Hammer',
            'CDLSHOOTINGSTAR': 'Shooting Star',
            'CDLDOJI': 'Doji',
            'CDLMORNINGSTAR': 'Morning Star',
            'CDLEVENINGSTAR': 'Evening Star',
            'CDL3WHITESOLDIERS': 'Three White Soldiers',
            'CDL3BLACKCROWS': 'Three Black Crows',
            'CDLHARAMI': 'Harami Pattern',
            'CDLPIERCING': 'Piercing Pattern',
            'CDLDRAGONFLYDOJI': 'Dragonfly Doji'
        }

        for func_name, pattern_name in pattern_functions.items():
            try:
                func = getattr(talib, func_name)
                result = func(open_prices, high, low, close)

                if result[-1] != 0:  # Pattern detected
                    patterns.append({
                        'name': pattern_name,
                        'type': 'bullish' if result[-1] > 0 else 'bearish',
                        'confidence': abs(result[-1]) / 100.0,  # Normalize to 0-1
                        'indicator': func_name
                    })
            except Exception as e:
                current_app.logger.error(f"Pattern detection error for {func_name}: {str(e)}")

        return patterns

    def _interpret_bollinger(self, price: float, upper: float, lower: float) -> str:
        """Interpret Bollinger Bands signal."""
        if np.isnan(upper) or np.isnan(lower):
            return 'neutral'

        if price <= lower:
            return 'oversold'  # Potential buy signal
        elif price >= upper:
            return 'overbought'  # Potential sell signal
        else:
            return 'neutral'

    def _interpret_rsi(self, rsi: float) -> str:
        """Interpret RSI signal."""
        if np.isnan(rsi):
            return 'neutral'

        if rsi < 30:
            return 'oversold'  # Buy signal
        elif rsi > 70:
            return 'overbought'  # Sell signal
        else:
            return 'neutral'

    def _interpret_stochastic(self, k: float, d: float) -> str:
        """Interpret Stochastic Oscillator signal."""
        if np.isnan(k) or np.isnan(d):
            return 'neutral'

        if k < 20 and d < 20:
            return 'oversold'  # Buy signal
        elif k > 80 and d > 80:
            return 'overbought'  # Sell signal
        elif k > d:
            return 'bullish_crossover'
        elif k < d:
            return 'bearish_crossover'
        else:
            return 'neutral'

    def _interpret_macd(self, macd: float, signal: float) -> str:
        """Interpret MACD signal."""
        if np.isnan(macd) or np.isnan(signal):
            return 'neutral'

        if macd > signal:
            return 'bullish'
        elif macd < signal:
            return 'bearish'
        else:
            return 'neutral'

    def _generate_signals(self, indicators: Dict, patterns: List[Dict]) -> List[Dict]:
        """
        Generate trading signals based on indicators and patterns.

        Args:
            indicators: Calculated indicators
            patterns: Detected patterns

        Returns:
            List of trading signals
        """
        signals = []

        # Strong buy signals
        buy_score = 0
        sell_score = 0

        # Indicator signals
        if indicators.get('rsi') and indicators['rsi']['signal'] == 'oversold':
            buy_score += 1
        if indicators.get('rsi') and indicators['rsi']['signal'] == 'overbought':
            sell_score += 1

        if indicators.get('bollinger_bands') and indicators['bollinger_bands']['signal'] == 'oversold':
            buy_score += 1
        if indicators.get('bollinger_bands') and indicators['bollinger_bands']['signal'] == 'overbought':
            sell_score += 1

        if indicators.get('stochastic'):
            stoch_signal = indicators['stochastic']['signal']
            if stoch_signal in ['oversold', 'bullish_crossover']:
                buy_score += 1
            elif stoch_signal in ['overbought', 'bearish_crossover']:
                sell_score += 1

        if indicators.get('macd') and indicators['macd']['trend'] == 'bullish':
            buy_score += 1
        if indicators.get('macd') and indicators['macd']['trend'] == 'bearish':
            sell_score += 1

        # Pattern signals
        for pattern in patterns:
            if pattern['confidence'] >= self.confidence_threshold:
                if pattern['type'] == 'bullish':
                    buy_score += 2  # Patterns have higher weight
                elif pattern['type'] == 'bearish':
                    sell_score += 2

        # Generate signals based on scores
        total_indicators = 4  # RSI, Bollinger, Stochastic, MACD
        max_score = total_indicators + (len(patterns) * 2)

        if buy_score >= 3:
            confidence = min(buy_score / max_score, 1.0)
            signals.append({
                'type': 'BUY',
                'confidence': confidence,
                'strength': 'strong' if buy_score >= 5 else 'moderate',
                'supporting_factors': buy_score
            })

        if sell_score >= 3:
            confidence = min(sell_score / max_score, 1.0)
            signals.append({
                'type': 'SELL',
                'confidence': confidence,
                'strength': 'strong' if sell_score >= 5 else 'moderate',
                'supporting_factors': sell_score
            })

        return signals

    def scan_multiple_assets(self, symbols: List[str], price_data_dict: Dict[str, pd.DataFrame]) -> List[Dict]:
        """
        Scan multiple assets for trading opportunities.

        Args:
            symbols: List of asset symbols
            price_data_dict: Dictionary mapping symbols to OHLCV DataFrames

        Returns:
            List of opportunities sorted by confidence
        """
        opportunities = []

        for symbol in symbols[:current_app.config['MAX_ASSETS_SCAN']]:
            if symbol not in price_data_dict:
                continue

            try:
                analysis = self.analyze_asset(symbol, price_data_dict[symbol])

                if analysis['signals']:
                    for signal in analysis['signals']:
                        opportunities.append({
                            'symbol': symbol,
                            'signal_type': signal['type'],
                            'confidence': signal['confidence'],
                            'strength': signal['strength'],
                            'patterns': analysis['patterns'],
                            'indicators': analysis['indicators']
                        })
            except Exception as e:
                current_app.logger.error(f"Error analyzing {symbol}: {str(e)}")

        # Sort by confidence
        opportunities.sort(key=lambda x: x['confidence'], reverse=True)

        return opportunities
