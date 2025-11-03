"""
Portfolio management API endpoints.
"""
from flask import Blueprint, request, jsonify
from datetime import datetime

from app import db
from app.models.portfolio import Position, FavoriteAsset

bp = Blueprint('portfolio', __name__, url_prefix='/api/portfolio')


@bp.route('/positions', methods=['GET'])
def get_positions():
    """
    Get all positions for a user.
    Query params: user_id, is_open (optional)
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    query = Position.query.filter_by(user_id=user_id)

    is_open = request.args.get('is_open')
    if is_open is not None:
        query = query.filter_by(is_open=is_open.lower() == 'true')

    positions = query.order_by(Position.opened_at.desc()).all()

    return jsonify({
        'positions': [pos.to_dict() for pos in positions],
        'count': len(positions)
    })


@bp.route('/positions', methods=['POST'])
def create_position():
    """
    Create a new position.
    Body: {user_id, symbol, asset_name, position_type, quantity, entry_price, notes}
    """
    data = request.get_json()

    required = ['user_id', 'symbol', 'position_type', 'quantity', 'entry_price']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    if data['position_type'] not in ['BUY', 'SELL']:
        return jsonify({'error': 'position_type must be BUY or SELL'}), 400

    position = Position(
        user_id=data['user_id'],
        symbol=data['symbol'].upper(),
        asset_name=data.get('asset_name'),
        position_type=data['position_type'],
        quantity=data['quantity'],
        entry_price=data['entry_price'],
        current_price=data['entry_price'],  # Initialize with entry price
        notes=data.get('notes')
    )

    db.session.add(position)
    db.session.commit()

    return jsonify({
        'message': 'Position created',
        'position': position.to_dict()
    }), 201


@bp.route('/positions/<int:position_id>', methods=['PUT'])
def update_position(position_id):
    """
    Update position (current price, close position, etc.).
    Body: {current_price, is_open, notes}
    """
    position = Position.query.get_or_404(position_id)
    data = request.get_json()

    if 'current_price' in data:
        position.current_price = data['current_price']
        position.calculate_pnl()

    if 'is_open' in data:
        position.is_open = data['is_open']
        if not data['is_open']:
            position.closed_at = datetime.utcnow()
            position.calculate_pnl()

    if 'notes' in data:
        position.notes = data['notes']

    db.session.commit()

    return jsonify({
        'message': 'Position updated',
        'position': position.to_dict()
    })


@bp.route('/positions/<int:position_id>', methods=['DELETE'])
def delete_position(position_id):
    """Delete a position."""
    position = Position.query.get_or_404(position_id)

    db.session.delete(position)
    db.session.commit()

    return jsonify({'message': 'Position deleted'}), 200


@bp.route('/favorites', methods=['GET'])
def get_favorites():
    """
    Get favorite assets for a user.
    Query params: user_id
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    favorites = FavoriteAsset.query.filter_by(user_id=user_id).order_by(
        FavoriteAsset.added_at.desc()
    ).all()

    return jsonify({
        'favorites': [fav.to_dict() for fav in favorites],
        'count': len(favorites)
    })


@bp.route('/favorites', methods=['POST'])
def add_favorite():
    """
    Add asset to favorites.
    Body: {user_id, symbol, asset_name, asset_type, interest_reason, risk_tolerance, investment_horizon}
    """
    data = request.get_json()

    required = ['user_id', 'symbol']
    if not all(field in data for field in required):
        return jsonify({'error': 'Missing required fields'}), 400

    # Check if already exists
    existing = FavoriteAsset.query.filter_by(
        user_id=data['user_id'],
        symbol=data['symbol'].upper()
    ).first()

    if existing:
        return jsonify({'error': 'Asset already in favorites'}), 409

    favorite = FavoriteAsset(
        user_id=data['user_id'],
        symbol=data['symbol'].upper(),
        asset_name=data.get('asset_name'),
        asset_type=data.get('asset_type'),
        interest_reason=data.get('interest_reason'),
        risk_tolerance=data.get('risk_tolerance'),
        investment_horizon=data.get('investment_horizon')
    )

    db.session.add(favorite)
    db.session.commit()

    return jsonify({
        'message': 'Favorite added',
        'favorite': favorite.to_dict()
    }), 201


@bp.route('/favorites/<int:favorite_id>', methods=['PUT'])
def update_favorite(favorite_id):
    """
    Update favorite asset (track views, update preferences).
    Body: {interest_reason, risk_tolerance, investment_horizon, increment_view}
    """
    favorite = FavoriteAsset.query.get_or_404(favorite_id)
    data = request.get_json()

    if data.get('increment_view'):
        favorite.view_count += 1
        favorite.last_viewed_at = datetime.utcnow()

    if 'interest_reason' in data:
        favorite.interest_reason = data['interest_reason']

    if 'risk_tolerance' in data:
        favorite.risk_tolerance = data['risk_tolerance']

    if 'investment_horizon' in data:
        favorite.investment_horizon = data['investment_horizon']

    db.session.commit()

    return jsonify({
        'message': 'Favorite updated',
        'favorite': favorite.to_dict()
    })


@bp.route('/favorites/<int:favorite_id>', methods=['DELETE'])
def delete_favorite(favorite_id):
    """Remove asset from favorites."""
    favorite = FavoriteAsset.query.get_or_404(favorite_id)

    db.session.delete(favorite)
    db.session.commit()

    return jsonify({'message': 'Favorite removed'}), 200


@bp.route('/summary', methods=['GET'])
def get_portfolio_summary():
    """
    Get portfolio summary with P&L calculations.
    Query params: user_id
    """
    user_id = request.args.get('user_id', type=int)
    if not user_id:
        return jsonify({'error': 'user_id required'}), 400

    positions = Position.query.filter_by(user_id=user_id).all()

    total_realized = sum(
        float(pos.realized_pnl or 0) for pos in positions if not pos.is_open
    )
    total_unrealized = sum(
        float(pos.unrealized_pnl or 0) for pos in positions if pos.is_open
    )

    open_positions = [pos for pos in positions if pos.is_open]
    closed_positions = [pos for pos in positions if not pos.is_open]

    return jsonify({
        'user_id': user_id,
        'summary': {
            'total_positions': len(positions),
            'open_positions': len(open_positions),
            'closed_positions': len(closed_positions),
            'total_realized_pnl': total_realized,
            'total_unrealized_pnl': total_unrealized,
            'total_pnl': total_realized + total_unrealized
        },
        'open_positions': [pos.to_dict() for pos in open_positions[:10]],
        'recent_closed': [pos.to_dict() for pos in closed_positions[:10]]
    })
