"""
Main routes for Broker Assistant.
"""
from flask import Blueprint, jsonify, render_template_string

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """
    API index page with available endpoints.
    """
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Broker Assistant API</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                border-bottom: 3px solid #007bff;
                padding-bottom: 10px;
            }
            h2 {
                color: #007bff;
                margin-top: 30px;
            }
            .endpoint {
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 5px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .method {
                display: inline-block;
                padding: 5px 10px;
                border-radius: 3px;
                font-weight: bold;
                margin-right: 10px;
            }
            .get { background-color: #61affe; color: white; }
            .post { background-color: #49cc90; color: white; }
            .put { background-color: #fca130; color: white; }
            .delete { background-color: #f93e3e; color: white; }
            code {
                background: #f4f4f4;
                padding: 2px 6px;
                border-radius: 3px;
                font-family: monospace;
            }
            .status {
                margin: 20px 0;
                padding: 15px;
                background: #d4edda;
                border: 1px solid #c3e6cb;
                border-radius: 5px;
                color: #155724;
            }
        </style>
    </head>
    <body>
        <h1>🤖 Broker Assistant API</h1>
        <div class="status">
            <strong>Status:</strong> Running ✓
        </div>

        <div style="margin: 20px 0; padding: 20px; background: linear-gradient(135deg, #1f6feb 0%, #58a6ff 100%); border-radius: 8px;">
            <h3 style="color: white; margin-bottom: 10px;">🚀 Trading Dashboard</h3>
            <p style="color: rgba(255,255,255,0.9); margin-bottom: 15px; font-size: 14px;">
                Accede al dashboard completo con análisis técnico, gráficos interactivos y sugerencias IA
            </p>
            <a href="/dashboard" style="display: inline-block; background: white; color: #1f6feb; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: 600;">
                Abrir Dashboard →
            </a>
        </div>

        <h2>📊 Portfolio Endpoints</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/portfolio/positions</code>
            <p>Get all open positions for a user</p>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/portfolio/positions</code>
            <p>Create a new position</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/portfolio/favorites</code>
            <p>Get user's favorite assets</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/portfolio/summary</code>
            <p>Get portfolio summary with total P&L</p>
        </div>

        <h2>📈 Analysis Endpoints</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/analysis/technical/:symbol</code>
            <p>Get technical analysis for a symbol (RSI, Bollinger Bands, MACD, patterns)</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/analysis/news/:symbol</code>
            <p>Get news sentiment analysis for a symbol</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/analysis/predict/:symbol</code>
            <p>Get AI prediction with explainability factors (XAI)</p>
        </div>
        <div class="endpoint">
            <span class="method post">POST</span>
            <code>/api/analysis/scan</code>
            <p>Scan multiple symbols for trading opportunities</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/analysis/predictions</code>
            <p>Get prediction history for backtesting</p>
        </div>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/api/analysis/accuracy</code>
            <p>Get model accuracy metrics</p>
        </div>

        <h2>🔌 WebSocket Events</h2>
        <div class="endpoint">
            <strong>Event:</strong> <code>subscribe_symbol</code>
            <p>Subscribe to real-time price updates for a symbol</p>
        </div>
        <div class="endpoint">
            <strong>Event:</strong> <code>unsubscribe_symbol</code>
            <p>Unsubscribe from price updates</p>
        </div>
        <div class="endpoint">
            <strong>Event:</strong> <code>subscribe_portfolio</code>
            <p>Subscribe to portfolio updates</p>
        </div>

        <h2>🧪 Test Endpoints</h2>
        <div class="endpoint">
            <span class="method get">GET</span>
            <code>/health</code>
            <p>Health check endpoint</p>
        </div>

        <footer style="margin-top: 50px; padding-top: 20px; border-top: 1px solid #ddd; color: #666;">
            <p>Broker Assistant - AI-Powered Stock Investment Assistant</p>
            <p>Technical Analysis + News Sentiment + Explainable AI Predictions</p>
        </footer>
    </body>
    </html>
    """
    return render_template_string(html)


@bp.route('/health')
def health():
    """
    Health check endpoint.
    """
    return jsonify({
        'status': 'healthy',
        'service': 'Broker Assistant',
        'version': '1.0.0'
    })


@bp.route('/test-websocket')
def test_websocket():
    """
    WebSocket test page.
    """
    from flask import render_template
    return render_template('test_websocket.html')


@bp.route('/dashboard')
def dashboard():
    """
    Main trading dashboard.
    """
    from flask import render_template
    return render_template('dashboard.html')
