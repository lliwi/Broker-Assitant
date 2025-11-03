"""
Prediction Service for generating and storing AI predictions.
Implements continuous learning through prediction history tracking.
"""
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import pandas as pd
from flask import current_app

from app import db
from app.models.prediction import Prediction, PredictionFactor
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.news_analysis import NewsAnalysisService


class PredictionService:
    """
    Service for generating predictions and managing prediction history.
    All predictions are stored for backtesting and continuous learning.
    """

    def __init__(self):
        self.technical_service = TechnicalAnalysisService()
        self.news_service = NewsAnalysisService()

    def generate_prediction(
        self,
        symbol: str,
        price_data: pd.DataFrame,
        analysis_type: str = 'hybrid',
        user_id: Optional[int] = None
    ) -> Prediction:
        """
        Generate a new prediction with explainability (XAI).

        Args:
            symbol: Asset symbol
            price_data: Historical price data
            analysis_type: 'technical', 'fundamental', or 'hybrid'
            user_id: Optional user ID if prediction is for specific user

        Returns:
            Prediction object (already saved to database)
        """
        current_price = float(price_data['close'].iloc[-1])

        # Perform analysis based on type
        if analysis_type in ['technical', 'hybrid']:
            tech_analysis = self.technical_service.analyze_asset(symbol, price_data)
        else:
            tech_analysis = None

        if analysis_type in ['fundamental', 'hybrid']:
            news_analysis = self.news_service.analyze_news_for_asset(symbol)
        else:
            news_analysis = None

        # Generate prediction
        prediction_result = self._combine_analyses(
            symbol,
            current_price,
            tech_analysis,
            news_analysis,
            analysis_type
        )

        # Create prediction record
        prediction = Prediction(
            symbol=symbol,
            prediction_type=prediction_result['type'],
            confidence_score=prediction_result['confidence'],
            target_price=prediction_result.get('target_price'),
            stop_loss=prediction_result.get('stop_loss'),
            time_horizon=prediction_result.get('time_horizon', 'medium'),
            analysis_type=analysis_type,
            model_version='v1.0',
            price_at_prediction=current_price,
            market_condition=prediction_result.get('market_condition', 'neutral'),
            user_id=user_id,
            actual_outcome='pending'
        )

        # Set expiration based on time horizon
        if prediction.time_horizon == 'short':
            prediction.expires_at = datetime.utcnow() + timedelta(days=7)
        elif prediction.time_horizon == 'long':
            prediction.expires_at = datetime.utcnow() + timedelta(days=90)
        else:  # medium
            prediction.expires_at = datetime.utcnow() + timedelta(days=30)

        db.session.add(prediction)
        db.session.flush()  # Get prediction ID

        # Add explainability factors (XAI)
        factors = self._extract_factors(tech_analysis, news_analysis, prediction_result)
        for factor_data in factors:
            factor = PredictionFactor(
                prediction_id=prediction.id,
                **factor_data
            )
            db.session.add(factor)

        db.session.commit()

        current_app.logger.info(
            f"Generated {prediction.prediction_type} prediction for {symbol} "
            f"with confidence {prediction.confidence_score}"
        )

        return prediction

    def _combine_analyses(
        self,
        symbol: str,
        current_price: float,
        tech_analysis: Optional[Dict],
        news_analysis: Optional[Dict],
        analysis_type: str
    ) -> Dict:
        """
        Combine technical and fundamental analyses into a single prediction.

        Args:
            symbol: Asset symbol
            current_price: Current market price
            tech_analysis: Technical analysis results
            news_analysis: News sentiment analysis results
            analysis_type: Type of analysis

        Returns:
            Combined prediction dictionary
        """
        buy_score = 0
        sell_score = 0
        total_weight = 0

        # Technical signals
        if tech_analysis and tech_analysis.get('signals'):
            for signal in tech_analysis['signals']:
                weight = signal['confidence']
                total_weight += weight

                if signal['type'] == 'BUY':
                    buy_score += weight
                elif signal['type'] == 'SELL':
                    sell_score += weight

        # Fundamental signals (news sentiment)
        if news_analysis:
            sentiment_score = news_analysis.get('score', 0.5)
            weight = 0.3  # News has moderate weight

            if sentiment_score > 0.6:
                buy_score += weight
            elif sentiment_score < 0.4:
                sell_score += weight

            total_weight += weight

        # Determine prediction
        if total_weight == 0:
            return {
                'type': 'HOLD',
                'confidence': 0.5,
                'market_condition': 'uncertain'
            }

        buy_confidence = buy_score / total_weight if total_weight > 0 else 0
        sell_confidence = sell_score / total_weight if total_weight > 0 else 0

        threshold = current_app.config.get('PATTERN_CONFIDENCE_THRESHOLD', 0.8)

        if buy_confidence >= threshold:
            prediction_type = 'BUY'
            confidence = buy_confidence
            # Calculate target (5-10% above current)
            target_price = current_price * 1.08
            stop_loss = current_price * 0.95
        elif sell_confidence >= threshold:
            prediction_type = 'SELL'
            confidence = sell_confidence
            target_price = current_price * 0.92
            stop_loss = current_price * 1.05
        elif buy_confidence > sell_confidence and buy_confidence >= 0.6:
            prediction_type = 'BUY'
            confidence = buy_confidence
            target_price = current_price * 1.05
            stop_loss = current_price * 0.97
        elif sell_confidence > buy_confidence and sell_confidence >= 0.6:
            prediction_type = 'SELL'
            confidence = sell_confidence
            target_price = current_price * 0.95
            stop_loss = current_price * 1.03
        else:
            prediction_type = 'HOLD'
            confidence = 0.5
            target_price = None
            stop_loss = None

        return {
            'type': prediction_type,
            'confidence': confidence,
            'target_price': target_price,
            'stop_loss': stop_loss,
            'time_horizon': 'medium',
            'market_condition': self._determine_market_condition(tech_analysis)
        }

    def _determine_market_condition(self, tech_analysis: Optional[Dict]) -> str:
        """Determine overall market condition from technical analysis."""
        if not tech_analysis or not tech_analysis.get('indicators'):
            return 'neutral'

        indicators = tech_analysis['indicators']
        bullish_count = 0
        bearish_count = 0

        if indicators.get('macd') and indicators['macd']['trend'] == 'bullish':
            bullish_count += 1
        elif indicators.get('macd') and indicators['macd']['trend'] == 'bearish':
            bearish_count += 1

        if indicators.get('rsi'):
            rsi_value = indicators['rsi'].get('value')
            if rsi_value and rsi_value > 50:
                bullish_count += 1
            elif rsi_value and rsi_value < 50:
                bearish_count += 1

        if bullish_count > bearish_count:
            return 'bullish'
        elif bearish_count > bullish_count:
            return 'bearish'
        else:
            return 'sideways'

    def _extract_factors(
        self,
        tech_analysis: Optional[Dict],
        news_analysis: Optional[Dict],
        prediction_result: Dict
    ) -> List[Dict]:
        """
        Extract explainability factors from analyses (XAI).

        Args:
            tech_analysis: Technical analysis results
            news_analysis: News sentiment results
            prediction_result: Prediction result

        Returns:
            List of factor dictionaries for PredictionFactor creation
        """
        factors = []

        # Technical indicators
        if tech_analysis and tech_analysis.get('indicators'):
            indicators = tech_analysis['indicators']

            if indicators.get('rsi'):
                rsi_val = indicators['rsi'].get('value')
                if rsi_val:
                    factors.append({
                        'factor_type': 'indicator',
                        'factor_name': 'RSI',
                        'factor_value': str(rsi_val),
                        'weight': 0.2,
                        'description': f"RSI at {rsi_val:.2f} indicates {indicators['rsi']['signal']} conditions",
                        'indicator_period': 14
                    })

            if indicators.get('bollinger_bands'):
                bb = indicators['bollinger_bands']
                if bb['signal'] != 'neutral':
                    factors.append({
                        'factor_type': 'indicator',
                        'factor_name': 'Bollinger Bands',
                        'factor_value': bb['signal'],
                        'weight': 0.15,
                        'description': f"Price is {bb['signal']} relative to Bollinger Bands"
                    })

            if indicators.get('macd'):
                macd = indicators['macd']
                if macd['trend'] != 'neutral':
                    factors.append({
                        'factor_type': 'indicator',
                        'factor_name': 'MACD',
                        'factor_value': macd['trend'],
                        'weight': 0.2,
                        'description': f"MACD showing {macd['trend']} trend"
                    })

        # Chart patterns
        if tech_analysis and tech_analysis.get('patterns'):
            for pattern in tech_analysis['patterns']:
                if pattern['confidence'] >= 0.7:
                    factors.append({
                        'factor_type': 'pattern',
                        'factor_name': pattern['name'],
                        'factor_value': pattern['type'],
                        'weight': pattern['confidence'] * 0.3,
                        'description': f"{pattern['name']} pattern detected ({pattern['type']})"
                    })

        # News sentiment
        if news_analysis:
            factors.append({
                'factor_type': 'news',
                'factor_name': 'News Sentiment',
                'factor_value': news_analysis.get('sentiment', 'neutral'),
                'weight': 0.25,
                'description': news_analysis.get('summary', 'News sentiment analysis')
            })

        return factors

    def verify_predictions(self, symbols: Optional[List[str]] = None):
        """
        Verify past predictions for backtesting and continuous learning.

        Args:
            symbols: Optional list of symbols to verify (all if None)
        """
        # Get pending predictions that have expired
        query = Prediction.query.filter(
            Prediction.actual_outcome == 'pending',
            Prediction.expires_at <= datetime.utcnow()
        )

        if symbols:
            query = query.filter(Prediction.symbol.in_(symbols))

        predictions = query.all()

        for prediction in predictions:
            # Here you would fetch current price and verify prediction
            # For now, just mark as verified
            prediction.outcome_verified_at = datetime.utcnow()
            # Would calculate accuracy_score based on actual outcome
            # prediction.accuracy_score = ...
            # prediction.actual_outcome = 'correct' or 'incorrect'

        db.session.commit()

        current_app.logger.info(f"Verified {len(predictions)} predictions")

    def get_prediction_history(
        self,
        symbol: Optional[str] = None,
        user_id: Optional[int] = None,
        limit: int = 50
    ) -> List[Prediction]:
        """
        Retrieve prediction history for analysis.

        Args:
            symbol: Optional symbol filter
            user_id: Optional user filter
            limit: Maximum predictions to return

        Returns:
            List of predictions
        """
        query = Prediction.query.order_by(Prediction.created_at.desc())

        if symbol:
            query = query.filter(Prediction.symbol == symbol)
        if user_id:
            query = query.filter(Prediction.user_id == user_id)

        return query.limit(limit).all()

    def get_accuracy_stats(self, symbol: Optional[str] = None) -> Dict:
        """
        Calculate accuracy statistics for model performance.

        Args:
            symbol: Optional symbol filter

        Returns:
            Dictionary with accuracy statistics
        """
        query = Prediction.query.filter(Prediction.actual_outcome != 'pending')

        if symbol:
            query = query.filter(Prediction.symbol == symbol)

        total = query.count()
        correct = query.filter(Prediction.actual_outcome == 'correct').count()

        accuracy = (correct / total * 100) if total > 0 else 0

        return {
            'total_predictions': total,
            'correct_predictions': correct,
            'accuracy_percentage': accuracy,
            'symbol': symbol
        }
