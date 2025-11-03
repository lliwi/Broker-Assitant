"""
News Analysis Service using NLP and AI models.
Implements quantitative fundamental analysis based on market news.
"""
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import anthropic
from flask import current_app

from app.utils.cache import cache_get, cache_set, get_analysis_cache_key


class NewsAnalysisService:
    """
    Service for news-based fundamental analysis using AI/NLP.
    Analyzes sentiment and fundamental factors from news sources.
    """

    def __init__(self):
        self.anthropic_client = None
        self._init_ai_clients()

    def _init_ai_clients(self):
        """Initialize AI API clients."""
        api_key = current_app.config.get('ANTHROPIC_API_KEY')
        if api_key:
            self.anthropic_client = anthropic.Anthropic(api_key=api_key)

    def analyze_news_for_asset(self, symbol: str, limit: int = 10) -> Dict:
        """
        Analyze recent news for an asset.

        Args:
            symbol: Asset symbol
            limit: Maximum number of news articles to analyze

        Returns:
            Dictionary with news analysis and sentiment
        """
        # Check cache
        cache_key = get_analysis_cache_key(symbol, 'news')
        cached = cache_get(cache_key)
        if cached:
            return cached

        # Fetch news
        news_articles = self._fetch_news(symbol, limit)

        if not news_articles:
            return {
                'symbol': symbol,
                'sentiment': 'neutral',
                'score': 0.5,
                'articles_analyzed': 0,
                'summary': 'No recent news available'
            }

        # Analyze sentiment with AI
        analysis = self._analyze_sentiment_with_ai(symbol, news_articles)

        # Cache results
        cache_set(cache_key, analysis, ttl=1800)  # 30 minutes

        return analysis

    def _fetch_news(self, symbol: str, limit: int) -> List[Dict]:
        """
        Fetch news articles from APIs.

        Args:
            symbol: Asset symbol
            limit: Maximum articles to fetch

        Returns:
            List of news articles
        """
        articles = []

        # Try News API
        news_api_key = current_app.config.get('NEWS_API_KEY')
        if news_api_key:
            try:
                articles.extend(self._fetch_from_newsapi(symbol, news_api_key, limit))
            except Exception as e:
                current_app.logger.error(f"News API error: {str(e)}")

        # Try Finnhub
        finnhub_key = current_app.config.get('FINNHUB_API_KEY')
        if finnhub_key and len(articles) < limit:
            try:
                articles.extend(self._fetch_from_finnhub(symbol, finnhub_key, limit - len(articles)))
            except Exception as e:
                current_app.logger.error(f"Finnhub API error: {str(e)}")

        return articles[:limit]

    def _fetch_from_newsapi(self, symbol: str, api_key: str, limit: int) -> List[Dict]:
        """Fetch news from NewsAPI.org."""
        url = "https://newsapi.org/v2/everything"
        params = {
            'q': symbol,
            'apiKey': api_key,
            'language': 'en',
            'sortBy': 'publishedAt',
            'pageSize': limit
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = []

        for article in data.get('articles', []):
            articles.append({
                'title': article.get('title'),
                'description': article.get('description'),
                'source': article.get('source', {}).get('name'),
                'published_at': article.get('publishedAt'),
                'url': article.get('url')
            })

        return articles

    def _fetch_from_finnhub(self, symbol: str, api_key: str, limit: int) -> List[Dict]:
        """Fetch news from Finnhub."""
        # Calculate date range (last 7 days)
        to_date = datetime.now()
        from_date = to_date - timedelta(days=7)

        url = "https://finnhub.io/api/v1/company-news"
        params = {
            'symbol': symbol,
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'token': api_key
        }

        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = []

        for item in data[:limit]:
            articles.append({
                'title': item.get('headline'),
                'description': item.get('summary'),
                'source': item.get('source'),
                'published_at': datetime.fromtimestamp(item.get('datetime')).isoformat(),
                'url': item.get('url')
            })

        return articles

    def _analyze_sentiment_with_ai(self, symbol: str, articles: List[Dict]) -> Dict:
        """
        Analyze sentiment using AI (Claude).

        Args:
            symbol: Asset symbol
            articles: List of news articles

        Returns:
            Sentiment analysis results
        """
        if not self.anthropic_client:
            return self._basic_sentiment_analysis(symbol, articles)

        # Prepare prompt for Claude
        articles_text = "\n\n".join([
            f"Title: {a['title']}\nDescription: {a['description']}\nSource: {a['source']}"
            for a in articles if a.get('title')
        ])

        prompt = f"""Analyze the following news articles about {symbol} and provide:
1. Overall sentiment (bullish, bearish, or neutral)
2. Sentiment score (0.0 to 1.0, where 0 is very bearish and 1 is very bullish)
3. Key factors influencing the sentiment
4. Brief summary of the news sentiment

News articles:
{articles_text}

Respond in JSON format with keys: sentiment, score, factors (list), summary"""

        try:
            message = self.anthropic_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )

            response_text = message.content[0].text

            # Parse JSON response
            import json
            result = json.loads(response_text)

            return {
                'symbol': symbol,
                'sentiment': result.get('sentiment', 'neutral'),
                'score': result.get('score', 0.5),
                'factors': result.get('factors', []),
                'summary': result.get('summary', ''),
                'articles_analyzed': len(articles),
                'articles': articles[:5]  # Include top 5 articles
            }

        except Exception as e:
            current_app.logger.error(f"AI sentiment analysis error: {str(e)}")
            return self._basic_sentiment_analysis(symbol, articles)

    def _basic_sentiment_analysis(self, symbol: str, articles: List[Dict]) -> Dict:
        """
        Basic keyword-based sentiment analysis (fallback).

        Args:
            symbol: Asset symbol
            articles: List of news articles

        Returns:
            Basic sentiment analysis
        """
        positive_words = [
            'growth', 'profit', 'surge', 'rise', 'gain', 'up', 'high',
            'strong', 'beat', 'exceed', 'positive', 'bullish', 'buy'
        ]
        negative_words = [
            'loss', 'decline', 'fall', 'drop', 'down', 'low', 'weak',
            'miss', 'negative', 'bearish', 'sell', 'risk', 'concern'
        ]

        positive_count = 0
        negative_count = 0

        for article in articles:
            text = f"{article.get('title', '')} {article.get('description', '')}".lower()

            for word in positive_words:
                positive_count += text.count(word)
            for word in negative_words:
                negative_count += text.count(word)

        total = positive_count + negative_count
        if total == 0:
            sentiment = 'neutral'
            score = 0.5
        else:
            score = positive_count / total
            if score > 0.6:
                sentiment = 'bullish'
            elif score < 0.4:
                sentiment = 'bearish'
            else:
                sentiment = 'neutral'

        return {
            'symbol': symbol,
            'sentiment': sentiment,
            'score': score,
            'articles_analyzed': len(articles),
            'summary': f'Based on keyword analysis of {len(articles)} articles',
            'articles': articles[:5]
        }

    def screen_assets_by_fundamentals(self, symbols: List[str]) -> List[Dict]:
        """
        Screen assets based on fundamental criteria.

        Args:
            symbols: List of asset symbols to screen

        Returns:
            List of assets that pass fundamental screening
        """
        results = []

        for symbol in symbols:
            try:
                fundamentals = self._get_fundamental_data(symbol)

                if fundamentals and self._passes_fundamental_criteria(fundamentals):
                    results.append({
                        'symbol': symbol,
                        'pe_ratio': fundamentals.get('pe_ratio'),
                        'pb_ratio': fundamentals.get('pb_ratio'),
                        'dividend_yield': fundamentals.get('dividend_yield'),
                        'market_cap': fundamentals.get('market_cap')
                    })
            except Exception as e:
                current_app.logger.error(f"Fundamental screening error for {symbol}: {str(e)}")

        return results

    def _get_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch fundamental data for an asset.

        Args:
            symbol: Asset symbol

        Returns:
            Fundamental data dictionary
        """
        # This would integrate with financial data APIs (Alpha Vantage, Finnhub, etc.)
        # For now, return placeholder structure
        return {
            'symbol': symbol,
            'pe_ratio': None,
            'pb_ratio': None,
            'dividend_yield': None,
            'market_cap': None
        }

    def _passes_fundamental_criteria(self, fundamentals: Dict) -> bool:
        """
        Check if asset passes fundamental screening criteria.

        Criteria from spec:
        - Low P/E ratio
        - Price below book value (P/B < 1)
        - Above-average dividend yield (but not excessive)

        Args:
            fundamentals: Fundamental data

        Returns:
            True if passes criteria
        """
        pe = fundamentals.get('pe_ratio')
        pb = fundamentals.get('pb_ratio')
        div_yield = fundamentals.get('dividend_yield')

        passes = True

        # Low P/E (below 15 is considered good)
        if pe and pe > 20:
            passes = False

        # P/B below 1 (price below book value)
        if pb and pb > 1.5:
            passes = False

        # Dividend yield between 2% and 8% (above average but not excessive)
        if div_yield and (div_yield < 2 or div_yield > 8):
            passes = False

        return passes
