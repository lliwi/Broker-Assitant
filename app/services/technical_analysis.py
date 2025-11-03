"""
Technical Analysis Service with pattern recognition and indicators.
Implements automated technical analysis with 80%+ accuracy target.
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from ta import momentum, volatility, trend
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
        Calculate technical indicators using pandas-ta and ta libraries.

        Args:
            df: OHLCV DataFrame

        Returns:
            Dictionary with indicator values
        """
        indicators = {}

        # Bollinger Bands
        try:
            period = current_app.config.get('BOLLINGER_PERIOD', 20)
            bb = volatility.BollingerBands(close=df['close'], window=period, window_dev=2)

            upper = bb.bollinger_hband().iloc[-1]
            middle = bb.bollinger_mavg().iloc[-1]
            lower = bb.bollinger_lband().iloc[-1]
            current_price = df['close'].iloc[-1]

            indicators['bollinger_bands'] = {
                'upper': float(upper) if not np.isnan(upper) else None,
                'middle': float(middle) if not np.isnan(middle) else None,
                'lower': float(lower) if not np.isnan(lower) else None,
                'current_price': float(current_price),
                'signal': self._interpret_bollinger(current_price, upper, lower)
            }
        except Exception as e:
            current_app.logger.error(f"Bollinger Bands calculation error: {str(e)}")
            indicators['bollinger_bands'] = None

        # RSI (Relative Strength Index)
        try:
            rsi_period = current_app.config.get('RSI_PERIOD', 14)
            rsi_indicator = momentum.RSIIndicator(close=df['close'], window=rsi_period)
            rsi_value = rsi_indicator.rsi().iloc[-1]

            indicators['rsi'] = {
                'value': float(rsi_value) if not np.isnan(rsi_value) else None,
                'signal': self._interpret_rsi(rsi_value)
            }
        except Exception as e:
            current_app.logger.error(f"RSI calculation error: {str(e)}")
            indicators['rsi'] = None

        # Stochastic Oscillator
        try:
            stoch_period = current_app.config.get('STOCHASTIC_PERIOD', 14)
            stoch = momentum.StochasticOscillator(
                high=df['high'],
                low=df['low'],
                close=df['close'],
                window=stoch_period,
                smooth_window=3
            )
            slowk = stoch.stoch().iloc[-1]
            slowd = stoch.stoch_signal().iloc[-1]

            indicators['stochastic'] = {
                'k': float(slowk) if not np.isnan(slowk) else None,
                'd': float(slowd) if not np.isnan(slowd) else None,
                'signal': self._interpret_stochastic(slowk, slowd)
            }
        except Exception as e:
            current_app.logger.error(f"Stochastic calculation error: {str(e)}")
            indicators['stochastic'] = None

        # MACD
        try:
            macd_indicator = trend.MACD(close=df['close'], window_slow=26, window_fast=12, window_sign=9)
            macd_value = macd_indicator.macd().iloc[-1]
            signal_value = macd_indicator.macd_signal().iloc[-1]
            hist_value = macd_indicator.macd_diff().iloc[-1]

            indicators['macd'] = {
                'macd': float(macd_value) if not np.isnan(macd_value) else None,
                'signal': float(signal_value) if not np.isnan(signal_value) else None,
                'histogram': float(hist_value) if not np.isnan(hist_value) else None,
                'trend': self._interpret_macd(macd_value, signal_value)
            }
        except Exception as e:
            current_app.logger.error(f"MACD calculation error: {str(e)}")
            indicators['macd'] = None

        return indicators

    def _detect_patterns(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect chart patterns using simple price action analysis.

        Args:
            df: OHLCV DataFrame

        Returns:
            List of detected patterns with confidence scores
        """
        # Use simple pattern detection based on price action
        patterns = self._simple_pattern_detection(df)
        return patterns

    def _simple_pattern_detection(self, df: pd.DataFrame) -> List[Dict]:
        """
        Simple pattern detection fallback based on price action.

        Args:
            df: OHLCV DataFrame

        Returns:
            List of simple patterns
        """
        patterns = []

        try:
            # Check for Doji (open ~= close)
            last_candle = df.iloc[-1]
            body_size = abs(last_candle['close'] - last_candle['open'])
            candle_range = last_candle['high'] - last_candle['low']

            if candle_range > 0 and body_size / candle_range < 0.1:
                patterns.append({
                    'name': 'Doji',
                    'type': 'neutral',
                    'confidence': 0.7,
                    'indicator': 'simple_doji'
                })

            # Check for Hammer (long lower shadow, small body at top)
            lower_shadow = last_candle['open'] - last_candle['low'] if last_candle['close'] > last_candle['open'] else last_candle['close'] - last_candle['low']
            if candle_range > 0 and lower_shadow / candle_range > 0.6:
                patterns.append({
                    'name': 'Hammer',
                    'type': 'bullish',
                    'confidence': 0.65,
                    'indicator': 'simple_hammer'
                })

            # Check for Shooting Star (long upper shadow, small body at bottom)
            upper_shadow = last_candle['high'] - last_candle['close'] if last_candle['close'] > last_candle['open'] else last_candle['high'] - last_candle['open']
            if candle_range > 0 and upper_shadow / candle_range > 0.6:
                patterns.append({
                    'name': 'Shooting Star',
                    'type': 'bearish',
                    'confidence': 0.65,
                    'indicator': 'simple_shooting_star'
                })

        except Exception as e:
            current_app.logger.error(f"Simple pattern detection error: {str(e)}")

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
