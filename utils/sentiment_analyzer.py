"""
Sentiment Analyzer for Indonesian Financial News
Analyzes sentiment of news articles in Bahasa Indonesia
"""
import re
from typing import Dict, List

class IndonesianSentimentAnalyzer:
    """Sentiment analyzer for Indonesian financial news"""

    def __init__(self):
        # Positive keywords (bullish indicators)
        self.positive_keywords = [
            'naik', 'meningkat', 'tumbuh', 'positif', 'untung', 'profit', 'laba',
            'menguat', 'optimis', 'bullish', 'rebound', 'rally', 'gain',
            'ekspansi', 'berkembang', 'cemerlang', 'bagus', 'baik', 'kuat',
            'peningkatan', 'pertumbuhan', 'surplus', 'recovery', 'pemulihan',
            'breakthrough', 'terobosan', 'inovasi', 'prestasi', 'capaian'
        ]

        # Negative keywords (bearish indicators)
        self.negative_keywords = [
            'turun', 'menurun', 'jatuh', 'negatif', 'rugi', 'merosot',
            'melemah', 'pesimis', 'bearish', 'crash', 'collapse', 'loss',
            'penurunan', 'susut', 'defisit', 'krisis', 'resesi', 'buruk',
            'lemah', 'anjlok', 'terpuruk', 'stagnan', 'koreksi', 'tekanan',
            'risiko', 'ancaman', 'kekhawatiran', 'uncertainty', 'ketidakpastian'
        ]

        # Neutral keywords
        self.neutral_keywords = [
            'stabil', 'flat', 'sideways', 'konsolidasi', 'wait and see',
            'tunggu', 'monitor', 'observe', 'pantau', 'datar'
        ]

        # Strong indicators (2x weight)
        self.strong_positive = [
            'sangat naik', 'lonjakan', 'melesat', 'melonjak', 'booming',
            'skyrocket', 'record high', 'rekor', 'fantastis', 'luar biasa'
        ]

        self.strong_negative = [
            'sangat turun', 'anjlok drastis', 'crash', 'collapsed', 'krisis parah',
            'ambruk', 'terpuruk parah', 'kehancuran', 'bencana'
        ]

    def analyze_text(self, text: str) -> Dict:
        """
        Analyze sentiment of a text

        Returns:
            dict: {
                'sentiment': 'positive'|'negative'|'neutral',
                'score': float (-1 to 1),
                'confidence': float (0 to 1)
            }
        """
        if not text:
            return {'sentiment': 'neutral', 'score': 0.0, 'confidence': 0.0}

        text_lower = text.lower()

        # Count keywords
        pos_count = sum(1 for word in self.positive_keywords if word in text_lower)
        neg_count = sum(1 for word in self.negative_keywords if word in text_lower)
        neu_count = sum(1 for word in self.neutral_keywords if word in text_lower)

        # Count strong indicators (2x weight)
        strong_pos = sum(2 for phrase in self.strong_positive if phrase in text_lower)
        strong_neg = sum(2 for phrase in self.strong_negative if phrase in text_lower)

        # Calculate total scores
        total_pos = pos_count + strong_pos
        total_neg = neg_count + strong_neg
        total_words = total_pos + total_neg + neu_count

        # Calculate sentiment score (-1 to 1)
        if total_words == 0:
            score = 0.0
            sentiment = 'neutral'
            confidence = 0.0
        else:
            score = (total_pos - total_neg) / max(total_words, 1)
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]

            # Determine sentiment category
            if score > 0.2:
                sentiment = 'positive'
            elif score < -0.2:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            # Calculate confidence based on number of keywords found
            confidence = min(total_words / 10.0, 1.0)  # Max confidence at 10+ keywords

        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'confidence': round(confidence, 3),
            'positive_count': total_pos,
            'negative_count': total_neg,
            'neutral_count': neu_count
        }

    def analyze_articles(self, articles: List[Dict]) -> Dict:
        """
        Analyze sentiment of multiple articles

        Args:
            articles: List of dicts with 'title' field

        Returns:
            dict: Overall sentiment analysis
        """
        if not articles:
            return {
                'overall_sentiment': 'neutral',
                'average_score': 0.0,
                'sentiment_distribution': {'positive': 0, 'negative': 0, 'neutral': 0},
                'article_sentiments': []
            }

        article_sentiments = []
        scores = []

        for article in articles:
            title = article.get('title', '')
            sentiment_result = self.analyze_text(title)
            article_sentiments.append({
                'title': title,
                **sentiment_result
            })
            scores.append(sentiment_result['score'])

        # Calculate overall metrics
        avg_score = sum(scores) / len(scores) if scores else 0.0

        sentiment_dist = {
            'positive': sum(1 for s in article_sentiments if s['sentiment'] == 'positive'),
            'negative': sum(1 for s in article_sentiments if s['sentiment'] == 'negative'),
            'neutral': sum(1 for s in article_sentiments if s['sentiment'] == 'neutral')
        }

        # Determine overall sentiment
        if avg_score > 0.2:
            overall = 'positive'
        elif avg_score < -0.2:
            overall = 'negative'
        else:
            overall = 'neutral'

        return {
            'overall_sentiment': overall,
            'average_score': round(avg_score, 3),
            'sentiment_distribution': sentiment_dist,
            'total_articles': len(articles),
            'article_sentiments': article_sentiments
        }

    def get_market_sentiment_signal(self, sentiment_score: float) -> str:
        """Convert sentiment score to trading signal"""
        if sentiment_score > 0.4:
            return "STRONG BUY"
        elif sentiment_score > 0.15:
            return "BUY"
        elif sentiment_score < -0.4:
            return "STRONG SELL"
        elif sentiment_score < -0.15:
            return "SELL"
        else:
            return "HOLD"


# Example usage
if __name__ == "__main__":
    analyzer = IndonesianSentimentAnalyzer()

    # Test with sample news titles
    test_titles = [
        "Saham BBCA naik 5% hari ini seiring optimisme pasar",
        "BBRI anjlok 3% akibat tekanan global",
        "TLKM stabil di tengah konsolidasi pasar",
        "Investor optimis dengan kinerja ASII yang melonjak",
        "Krisis global mengancam saham sektor keuangan"
    ]

    print("Testing Sentiment Analyzer:\n")
    for title in test_titles:
        result = analyzer.analyze_text(title)
        print(f"Title: {title}")
        print(f"Sentiment: {result['sentiment']} (score: {result['score']}, confidence: {result['confidence']})")
        print(f"Signal: {analyzer.get_market_sentiment_signal(result['score'])}")
        print("-" * 80)
