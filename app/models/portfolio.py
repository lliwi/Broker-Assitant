"""
Portfolio models for positions and favorite assets.
Includes AES-256 encryption for sensitive data.
"""
from datetime import datetime
from app import db
from cryptography.fernet import Fernet
from flask import current_app


class Position(db.Model):
    """
    User's open positions (buy/sell operations tracking).
    Sensitive data is encrypted with AES-256.
    """

    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    asset_name = db.Column(db.String(200))

    # Position details (encrypted)
    position_type = db.Column(db.String(10), nullable=False)  # 'BUY' or 'SELL'
    quantity = db.Column(db.Numeric(15, 4), nullable=False)
    entry_price = db.Column(db.Numeric(15, 4), nullable=False)
    current_price = db.Column(db.Numeric(15, 4))

    # Encrypted fields
    _encrypted_notes = db.Column('encrypted_notes', db.Text)

    # Timestamps
    opened_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    is_open = db.Column(db.Boolean, default=True, nullable=False, index=True)

    # Performance tracking
    realized_pnl = db.Column(db.Numeric(15, 4))
    unrealized_pnl = db.Column(db.Numeric(15, 4))

    def __repr__(self):
        return f'<Position {self.symbol} - {self.position_type}>'

    @property
    def notes(self):
        """Decrypt notes."""
        if not self._encrypted_notes:
            return None
        key = current_app.config['DB_ENCRYPTION_KEY']
        if not key:
            return None
        f = Fernet(key.encode())
        return f.decrypt(self._encrypted_notes.encode()).decode()

    @notes.setter
    def notes(self, value):
        """Encrypt notes."""
        if not value:
            self._encrypted_notes = None
            return
        key = current_app.config['DB_ENCRYPTION_KEY']
        if not key:
            self._encrypted_notes = value
            return
        f = Fernet(key.encode())
        self._encrypted_notes = f.encrypt(value.encode()).decode()

    def calculate_pnl(self):
        """Calculate profit/loss for the position."""
        if not self.current_price:
            return None

        if self.position_type == 'BUY':
            pnl = (self.current_price - self.entry_price) * self.quantity
        else:  # SELL
            pnl = (self.entry_price - self.current_price) * self.quantity

        if self.is_open:
            self.unrealized_pnl = pnl
        else:
            self.realized_pnl = pnl

        return float(pnl)

    def to_dict(self):
        """Convert position to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'asset_name': self.asset_name,
            'position_type': self.position_type,
            'quantity': float(self.quantity),
            'entry_price': float(self.entry_price),
            'current_price': float(self.current_price) if self.current_price else None,
            'unrealized_pnl': float(self.unrealized_pnl) if self.unrealized_pnl else None,
            'realized_pnl': float(self.realized_pnl) if self.realized_pnl else None,
            'opened_at': self.opened_at.isoformat(),
            'closed_at': self.closed_at.isoformat() if self.closed_at else None,
            'is_open': self.is_open,
            'notes': self.notes
        }


class FavoriteAsset(db.Model):
    """
    User's favorite assets for watchlist.
    Generates labeled data for ML personalization.
    """

    __tablename__ = 'favorite_assets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    symbol = db.Column(db.String(20), nullable=False, index=True)
    asset_name = db.Column(db.String(200))
    asset_type = db.Column(db.String(50))  # stock, crypto, etf, etc.

    # User preferences (labeled data for ML)
    interest_reason = db.Column(db.String(500))  # Why user is interested
    risk_tolerance = db.Column(db.String(20))  # low, medium, high
    investment_horizon = db.Column(db.String(20))  # short, medium, long

    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_viewed_at = db.Column(db.DateTime)
    view_count = db.Column(db.Integer, default=0)

    # Unique constraint
    __table_args__ = (
        db.UniqueConstraint('user_id', 'symbol', name='unique_user_favorite'),
    )

    def __repr__(self):
        return f'<FavoriteAsset {self.symbol}>'

    def to_dict(self):
        """Convert favorite asset to dictionary."""
        return {
            'id': self.id,
            'symbol': self.symbol,
            'asset_name': self.asset_name,
            'asset_type': self.asset_type,
            'interest_reason': self.interest_reason,
            'risk_tolerance': self.risk_tolerance,
            'investment_horizon': self.investment_horizon,
            'added_at': self.added_at.isoformat(),
            'last_viewed_at': self.last_viewed_at.isoformat() if self.last_viewed_at else None,
            'view_count': self.view_count
        }
