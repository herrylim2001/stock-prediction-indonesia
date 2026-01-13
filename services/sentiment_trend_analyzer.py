"""
Sentiment Trend Analyzer
Analyzes historical sentiment data to identify trends and patterns
Provides 7-day and 30-day trend analysis for improved predictions
"""
import sys
import os
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.news_database import get_news_database


class SentimentTrendAnalyzer:
    """Analyzer for sentiment trends and patterns"""

    def __init__(self):
        self.db = get_news_database()

    def get_sentiment_trend(self, stock_code, days=7):
        """
        Get sentiment trend for the last N days

        Returns:
            dict with trend analysis
        """
        df = self.db.get_sentiment_trend(stock_code, days=days)

        if df.empty:
            return {
                'trend_available': False,
                'message': f'No sentiment data available for last {days} days'
            }

        # Calculate trend metrics
        avg_sentiment = df['avg_sentiment'].mean()
        sentiment_std = df['avg_sentiment'].std()
        total_articles = df['total_articles'].sum()
        total_fundamental_events = df['fundamental_events_count'].sum()

        # Calculate trend direction (linear regression slope)
        if len(df) >= 2:
            x = np.arange(len(df))
            y = df['avg_sentiment'].values
            slope = np.polyfit(x, y, 1)[0]

            if slope > 0.01:
                trend_direction = "IMPROVING"
                trend_strength = min(abs(slope) * 100, 100)
            elif slope < -0.01:
                trend_direction = "DECLINING"
                trend_strength = min(abs(slope) * 100, 100)
            else:
                trend_direction = "STABLE"
                trend_strength = 0
        else:
            trend_direction = "INSUFFICIENT_DATA"
            trend_strength = 0
            slope = 0

        # Recent vs historical comparison
        recent_sentiment = df.head(3)['avg_sentiment'].mean()  # Last 3 days
        older_sentiment = df.tail(3)['avg_sentiment'].mean()   # 3 days before
        sentiment_change = recent_sentiment - older_sentiment

        # Momentum score (-100 to +100)
        momentum_score = sentiment_change * 100

        # Volatility (how stable is sentiment?)
        volatility = sentiment_std if not pd.isna(sentiment_std) else 0

        return {
            'trend_available': True,
            'days_analyzed': len(df),
            'avg_sentiment': avg_sentiment,
            'recent_sentiment': recent_sentiment,
            'sentiment_change': sentiment_change,
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'momentum_score': momentum_score,
            'volatility': volatility,
            'slope': slope,
            'total_articles': int(total_articles),
            'total_fundamental_events': int(total_fundamental_events),
            'data': df.to_dict('records')
        }

    def get_multi_timeframe_sentiment(self, stock_code):
        """
        Get sentiment across multiple timeframes: 7-day and 30-day

        Returns:
            dict with sentiment analysis for different timeframes
        """
        trend_7d = self.get_sentiment_trend(stock_code, days=7)
        trend_30d = self.get_sentiment_trend(stock_code, days=30)

        # Compare short-term vs long-term
        if trend_7d['trend_available'] and trend_30d['trend_available']:
            # Divergence detection
            if (trend_7d['trend_direction'] == 'IMPROVING' and
                trend_30d['trend_direction'] == 'DECLINING'):
                divergence = "BULLISH_REVERSAL"  # Short term improving despite long-term decline
                divergence_strength = abs(trend_7d['momentum_score'])
            elif (trend_7d['trend_direction'] == 'DECLINING' and
                  trend_30d['trend_direction'] == 'IMPROVING'):
                divergence = "BEARISH_REVERSAL"  # Short term declining despite long-term improvement
                divergence_strength = abs(trend_7d['momentum_score'])
            elif (trend_7d['trend_direction'] == trend_30d['trend_direction'] and
                  trend_7d['trend_direction'] != 'STABLE'):
                divergence = "CONFIRMED_TREND"  # Both timeframes agree
                divergence_strength = (abs(trend_7d['momentum_score']) + abs(trend_30d['momentum_score'])) / 2
            else:
                divergence = "NEUTRAL"
                divergence_strength = 0

            alignment_score = 1.0 if divergence == "CONFIRMED_TREND" else 0.5 if divergence == "NEUTRAL" else 0.3
        else:
            divergence = "INSUFFICIENT_DATA"
            divergence_strength = 0
            alignment_score = 0

        return {
            '7_day': trend_7d,
            '30_day': trend_30d,
            'divergence': divergence,
            'divergence_strength': divergence_strength,
            'alignment_score': alignment_score
        }

    def get_sentiment_momentum_indicator(self, stock_code):
        """
        Calculate sentiment momentum indicator for prediction integration

        Returns:
            dict with momentum indicator value and metadata
        """
        multi_tf = self.get_multi_timeframe_sentiment(stock_code)

        if not multi_tf['7_day']['trend_available']:
            return {
                'available': False,
                'momentum': 0,
                'confidence': 0,
                'message': 'No historical sentiment data'
            }

        trend_7d = multi_tf['7_day']
        trend_30d = multi_tf['30_day']

        # Base momentum from 7-day trend
        base_momentum = trend_7d['momentum_score']

        # Adjust based on trend strength
        strength_multiplier = 1 + (trend_7d['trend_strength'] / 100)

        # Adjust based on fundamental events (high impact!)
        if trend_7d['total_fundamental_events'] > 0:
            fundamental_boost = trend_7d['total_fundamental_events'] * 15  # +15 per event
            if trend_7d['avg_sentiment'] > 0:
                base_momentum += fundamental_boost
            else:
                base_momentum -= fundamental_boost

        # Multi-timeframe confirmation bonus
        if multi_tf['divergence'] == 'CONFIRMED_TREND':
            base_momentum *= 1.3  # 30% boost for confirmed trend
        elif multi_tf['divergence'] in ['BULLISH_REVERSAL', 'BEARISH_REVERSAL']:
            base_momentum *= 1.2  # 20% boost for reversal signal

        # Final momentum (capped at ±100)
        final_momentum = np.clip(base_momentum * strength_multiplier, -100, 100)

        # Confidence based on data availability and consistency
        confidence = 0.5  # Base confidence
        if trend_7d['days_analyzed'] >= 7:
            confidence += 0.2
        if trend_7d['total_articles'] >= 30:
            confidence += 0.15
        if trend_7d['volatility'] < 0.3:  # Low volatility = more predictable
            confidence += 0.15
        if multi_tf['divergence'] == 'CONFIRMED_TREND':
            confidence += 0.1

        confidence = min(confidence, 1.0)

        return {
            'available': True,
            'momentum': final_momentum,
            'confidence': confidence,
            'trend_direction': trend_7d['trend_direction'],
            'divergence': multi_tf['divergence'],
            'fundamental_events': trend_7d['total_fundamental_events'],
            'total_articles': trend_7d['total_articles'],
            'volatility': trend_7d['volatility'],
            '7d_sentiment': trend_7d['avg_sentiment'],
            '30d_sentiment': trend_30d['avg_sentiment'] if trend_30d['trend_available'] else None
        }

    def get_correlation_analysis(self, stock_code, days=30):
        """
        Analyze correlation between sentiment and price movement

        Returns:
            dict with correlation metrics
        """
        df = self.db.get_correlation_data(stock_code, days=days)

        if df.empty or len(df) < 5:
            return {
                'available': False,
                'message': 'Insufficient data for correlation analysis'
            }

        # Filter rows with both sentiment and price data
        valid_df = df.dropna(subset=['avg_sentiment', 'daily_change_pct'])

        if len(valid_df) < 5:
            return {
                'available': False,
                'message': 'Insufficient overlapping sentiment and price data'
            }

        # Calculate correlation
        correlation = valid_df['avg_sentiment'].corr(valid_df['daily_change_pct'])

        # Classify correlation strength
        if abs(correlation) > 0.7:
            correlation_strength = "STRONG"
        elif abs(correlation) > 0.4:
            correlation_strength = "MODERATE"
        elif abs(correlation) > 0.2:
            correlation_strength = "WEAK"
        else:
            correlation_strength = "NEGLIGIBLE"

        # Direction accuracy (does positive sentiment lead to price increase?)
        valid_df['sentiment_direction'] = valid_df['avg_sentiment'].apply(
            lambda x: 'positive' if x > 0.1 else 'negative' if x < -0.1 else 'neutral'
        )
        valid_df['price_direction'] = valid_df['daily_change_pct'].apply(
            lambda x: 'up' if x > 0 else 'down'
        )

        # Count matches
        positive_sentiment_df = valid_df[valid_df['sentiment_direction'] == 'positive']
        if len(positive_sentiment_df) > 0:
            positive_accuracy = (positive_sentiment_df['price_direction'] == 'up').sum() / len(positive_sentiment_df)
        else:
            positive_accuracy = 0

        negative_sentiment_df = valid_df[valid_df['sentiment_direction'] == 'negative']
        if len(negative_sentiment_df) > 0:
            negative_accuracy = (negative_sentiment_df['price_direction'] == 'down').sum() / len(negative_sentiment_df)
        else:
            negative_accuracy = 0

        overall_direction_accuracy = (positive_accuracy + negative_accuracy) / 2 if (positive_accuracy or negative_accuracy) else 0

        return {
            'available': True,
            'correlation': correlation,
            'correlation_strength': correlation_strength,
            'direction_accuracy': overall_direction_accuracy,
            'positive_sentiment_accuracy': positive_accuracy,
            'negative_sentiment_accuracy': negative_accuracy,
            'days_analyzed': len(valid_df),
            'total_days': len(df)
        }

    def get_breaking_news_alert(self, stock_code, hours=3):
        """
        Check for breaking news or sudden sentiment shifts

        Returns:
            dict with alert info
        """
        recent_news = self.db.get_recent_news(stock_code, hours=hours)

        if recent_news.empty:
            return {
                'alert': False,
                'message': 'No recent news'
            }

        # Check for fundamental events in recent news
        fundamental_news = recent_news[recent_news['has_fundamental_event'] == True]

        if not fundamental_news.empty:
            avg_sentiment = recent_news['sentiment_score'].mean()

            return {
                'alert': True,
                'type': 'FUNDAMENTAL_EVENT',
                'count': len(fundamental_news),
                'sentiment': avg_sentiment,
                'articles': recent_news[['title', 'source', 'sentiment_score']].head(5).to_dict('records')
            }

        # Check for high article volume (unusual activity)
        if len(recent_news) >= 10:
            avg_sentiment = recent_news['sentiment_score'].mean()

            return {
                'alert': True,
                'type': 'HIGH_ACTIVITY',
                'count': len(recent_news),
                'sentiment': avg_sentiment,
                'articles': recent_news[['title', 'source', 'sentiment_score']].head(5).to_dict('records')
            }

        # Check for extreme sentiment
        avg_sentiment = recent_news['sentiment_score'].mean()
        if abs(avg_sentiment) > 0.5:
            return {
                'alert': True,
                'type': 'EXTREME_SENTIMENT',
                'sentiment': avg_sentiment,
                'direction': 'VERY_POSITIVE' if avg_sentiment > 0 else 'VERY_NEGATIVE',
                'count': len(recent_news),
                'articles': recent_news[['title', 'source', 'sentiment_score']].head(5).to_dict('records')
            }

        return {
            'alert': False,
            'message': f'{len(recent_news)} recent articles, normal sentiment'
        }


# Singleton instance
_analyzer_instance = None

def get_sentiment_trend_analyzer():
    """Get singleton trend analyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = SentimentTrendAnalyzer()
    return _analyzer_instance
