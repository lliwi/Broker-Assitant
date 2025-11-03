"""
WebSocket routes for real-time price updates.
Integrates Kafka stream with WebSocket for browser distribution.
"""
from flask_socketio import emit, join_room, leave_room
from flask import request
from app import socketio
from app.services.kafka_service import get_kafka_service
import logging

logger = logging.getLogger(__name__)


@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    logger.info(f"Client connected: {request.sid}")
    emit('connection_response', {'status': 'connected', 'sid': request.sid})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    logger.info(f"Client disconnected: {request.sid}")


@socketio.on('subscribe_symbol')
def handle_subscribe(data):
    """
    Subscribe client to real-time updates for a symbol.

    Args:
        data: {'symbol': 'AAPL'}
    """
    symbol = data.get('symbol')
    if not symbol:
        emit('error', {'message': 'Symbol required'})
        return

    # Join room for this symbol
    join_room(f"symbol_{symbol}")
    logger.info(f"Client {request.sid} subscribed to {symbol}")

    emit('subscribed', {'symbol': symbol, 'status': 'success'})


@socketio.on('unsubscribe_symbol')
def handle_unsubscribe(data):
    """
    Unsubscribe client from symbol updates.

    Args:
        data: {'symbol': 'AAPL'}
    """
    symbol = data.get('symbol')
    if not symbol:
        emit('error', {'message': 'Symbol required'})
        return

    # Leave room
    leave_room(f"symbol_{symbol}")
    logger.info(f"Client {request.sid} unsubscribed from {symbol}")

    emit('unsubscribed', {'symbol': symbol, 'status': 'success'})


@socketio.on('subscribe_portfolio')
def handle_subscribe_portfolio(data):
    """
    Subscribe to updates for multiple symbols (user's portfolio).

    Args:
        data: {'symbols': ['AAPL', 'GOOGL', 'MSFT']}
    """
    symbols = data.get('symbols', [])

    for symbol in symbols:
        join_room(f"symbol_{symbol}")

    logger.info(f"Client {request.sid} subscribed to portfolio: {symbols}")
    emit('portfolio_subscribed', {'symbols': symbols, 'status': 'success'})


def broadcast_price_update(price_data: dict):
    """
    Broadcast price update to subscribed clients.
    Called by Kafka consumer callback.

    Args:
        price_data: Price data from Kafka
    """
    symbol = price_data.get('symbol')
    if not symbol:
        return

    # Emit to all clients in this symbol's room
    socketio.emit(
        'price_update',
        price_data,
        room=f"symbol_{symbol}",
        namespace='/'
    )


def start_kafka_to_websocket_bridge():
    """
    Start bridge that forwards Kafka messages to WebSocket clients.
    Should be called on application startup.
    """
    kafka_service = get_kafka_service()

    # Subscribe to all price updates and forward to WebSocket
    kafka_service.subscribe_to_prices(
        callback=broadcast_price_update
    )

    logger.info("Kafka-to-WebSocket bridge started")
