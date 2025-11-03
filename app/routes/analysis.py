"""
Analysis API endpoints for technical/fundamental analysis and predictions.
"""
from flask import Blueprint, request, jsonify
import pandas as pd
from datetime import datetime

from app import db
from app.services.technical_analysis import TechnicalAnalysisService
from app.services.news_analysis import NewsAnalysisService
from app.services.prediction_service import PredictionService

bp = Blueprint('analysis', __name__, url_prefix='/api/analysis')


@bp.route('/technical/<symbol>', methods=['POST'])
def analyze_technical(symbol):
    """
    Perform technical analysis on an asset.
    Body: {price_data: [{timestamp, open, high, low, close, volume}, ...]}
    """
    data = request.get_json()
    price_data = data.get('price_data')

    if not price_data:
        return jsonify({'error': 'price_data required'}), 400

    try:
        # Convert to DataFrame
        df = pd.DataFrame(price_data)
        required_cols = ['open', 'high', 'low', 'close', 'volume']

        if not all(col in df.columns for col in required_cols):
            return jsonify({'error': f'Missing required columns: {required_cols}'}), 400

        # Perform analysis
        service = TechnicalAnalysisService()
        result = service.analyze_asset(symbol.upper(), df)

        return jsonify({
            'symbol': symbol.upper(),
            'analysis': result,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/news/<symbol>', methods=['GET'])
def analyze_news(symbol):
    """
    Analyze news sentiment for an asset.
    Query params: limit (default 10)
    """
    limit = request.args.get('limit', 10, type=int)

    try:
        service = NewsAnalysisService()
        result = service.analyze_news_for_asset(symbol.upper(), limit)

        return jsonify({
            'symbol': symbol.upper(),
            'analysis': result,
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/predict/<symbol>', methods=['POST'])
def generate_prediction(symbol):
    """
    Generate AI prediction for an asset.
    Body: {
        price_data: [{timestamp, open, high, low, close, volume}, ...],
        analysis_type: 'technical' | 'fundamental' | 'hybrid',
        user_id: (optional)
    }
    """
    data = request.get_json()
    price_data = data.get('price_data')
    analysis_type = data.get('analysis_type', 'hybrid')
    user_id = data.get('user_id')

    if not price_data:
        return jsonify({'error': 'price_data required'}), 400

    if analysis_type not in ['technical', 'fundamental', 'hybrid']:
        return jsonify({'error': 'Invalid analysis_type'}), 400

    try:
        # Convert to DataFrame
        df = pd.DataFrame(price_data)

        # Generate prediction
        service = PredictionService()
        prediction = service.generate_prediction(
            symbol.upper(),
            df,
            analysis_type,
            user_id
        )

        return jsonify({
            'message': 'Prediction generated',
            'prediction': prediction.to_dict()
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/predictions', methods=['GET'])
def get_predictions():
    """
    Get prediction history.
    Query params: symbol (optional), user_id (optional), limit (default 50)
    """
    symbol = request.args.get('symbol')
    user_id = request.args.get('user_id', type=int)
    limit = request.args.get('limit', 50, type=int)

    try:
        service = PredictionService()
        predictions = service.get_prediction_history(
            symbol=symbol.upper() if symbol else None,
            user_id=user_id,
            limit=limit
        )

        return jsonify({
            'predictions': [pred.to_dict() for pred in predictions],
            'count': len(predictions)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/predictions/<int:prediction_id>', methods=['GET'])
def get_prediction(prediction_id):
    """Get specific prediction with full details."""
    from app.models.prediction import Prediction

    prediction = Prediction.query.get_or_404(prediction_id)

    return jsonify({
        'prediction': prediction.to_dict(include_factors=True)
    })


@bp.route('/predictions/<int:prediction_id>/execute', methods=['POST'])
def mark_prediction_executed(prediction_id):
    """
    Mark prediction as executed by user.
    Body: {user_id}
    """
    from app.models.prediction import Prediction

    prediction = Prediction.query.get_or_404(prediction_id)
    data = request.get_json()

    user_id = data.get('user_id')
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    prediction.user_executed = True
    prediction.user_id = user_id

    db.session.commit()

    return jsonify({
        'message': 'Prediction marked as executed',
        'prediction': prediction.to_dict()
    })


@bp.route('/predictions/verify', methods=['POST'])
def verify_predictions():
    """
    Trigger prediction verification for backtesting.
    Body: {symbols: ['AAPL', 'GOOGL']} (optional)
    """
    data = request.get_json() or {}
    symbols = data.get('symbols')

    try:
        service = PredictionService()
        service.verify_predictions(symbols)

        return jsonify({
            'message': 'Predictions verified',
            'symbols': symbols
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/accuracy', methods=['GET'])
def get_accuracy_stats():
    """
    Get prediction accuracy statistics.
    Query params: symbol (optional)
    """
    symbol = request.args.get('symbol')

    try:
        service = PredictionService()
        stats = service.get_accuracy_stats(
            symbol=symbol.upper() if symbol else None
        )

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/scan', methods=['POST'])
def scan_assets():
    """
    Scan multiple assets for trading opportunities.
    Body: {
        symbols: ['AAPL', 'GOOGL', ...],
        price_data: {
            'AAPL': [{timestamp, open, high, low, close, volume}, ...],
            'GOOGL': [...]
        }
    }
    """
    data = request.get_json()
    symbols = data.get('symbols', [])
    price_data_dict = data.get('price_data', {})

    if not symbols or not price_data_dict:
        return jsonify({'error': 'symbols and price_data required'}), 400

    try:
        # Convert price data to DataFrames
        df_dict = {}
        for symbol, prices in price_data_dict.items():
            df_dict[symbol] = pd.DataFrame(prices)

        # Scan assets
        service = TechnicalAnalysisService()
        opportunities = service.scan_multiple_assets(symbols, df_dict)

        return jsonify({
            'opportunities': opportunities,
            'count': len(opportunities),
            'timestamp': datetime.utcnow().isoformat()
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@bp.route('/fundamental/screen', methods=['POST'])
def screen_fundamentals():
    """
    Screen assets by fundamental criteria.
    Body: {symbols: ['AAPL', 'GOOGL', ...]}
    """
    data = request.get_json()
    symbols = data.get('symbols', [])

    if not symbols:
        return jsonify({'error': 'symbols required'}), 400

    try:
        service = NewsAnalysisService()
        results = service.screen_assets_by_fundamentals(symbols)

        return jsonify({
            'assets': results,
            'count': len(results),
            'criteria': {
                'pe_ratio': 'Low (< 20)',
                'pb_ratio': 'Below book value (< 1.5)',
                'dividend_yield': 'Above average (2-8%)'
            }
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500
