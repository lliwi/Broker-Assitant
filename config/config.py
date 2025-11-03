"""
Configuration settings for Broker Assistant application.
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://brokerassistant:password@localhost:5432/brokerassistant')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    DB_ENCRYPTION_KEY = os.getenv('DB_ENCRYPTION_KEY', '')

    # Redis
    REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    CACHE_TTL_SECONDS = int(os.getenv('CACHE_TTL_SECONDS', '300'))

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    KAFKA_TOPIC_PRICES = os.getenv('KAFKA_TOPIC_PRICES', 'stock_prices')
    KAFKA_TOPIC_NEWS = os.getenv('KAFKA_TOPIC_NEWS', 'stock_news')

    # AI API Keys
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')

    # Financial Data APIs
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', '')
    FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY', '')
    NEWS_API_KEY = os.getenv('NEWS_API_KEY', '')

    # Application Settings
    MAX_ASSETS_SCAN = int(os.getenv('MAX_ASSETS_SCAN', '500'))
    PATTERN_CONFIDENCE_THRESHOLD = float(os.getenv('PATTERN_CONFIDENCE_THRESHOLD', '0.8'))

    # Technical Indicators Settings
    BOLLINGER_PERIOD = 20
    RSI_PERIOD = 14
    STOCHASTIC_PERIOD = 14


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    TESTING = False


class TestingConfig(Config):
    """Testing configuration."""
    DEBUG = True
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


config_by_name = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
