"""
Services module for automated scraping and sentiment analysis
"""
from .automated_scraper import AutomatedScraperService
from .sentiment_trend_analyzer import SentimentTrendAnalyzer, get_sentiment_trend_analyzer

__all__ = ['AutomatedScraperService', 'SentimentTrendAnalyzer', 'get_sentiment_trend_analyzer']
