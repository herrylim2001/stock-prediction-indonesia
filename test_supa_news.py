#!/usr/bin/env python3
"""
Quick test script for SUPA news scraping and sentiment analysis
"""

import sys
sys.path.append('/home/user/stock-prediction-indonesia')

from utils.news_scraper import IndonesianNewsScraper
from utils.sentiment_analyzer import IndonesianSentimentAnalyzer

def test_supa_news():
    """Test news scraping and sentiment for SUPA"""

    print("="*80)
    print("🏦 TESTING SUPA (Sinarmas Multiartha - Super Bank)")
    print("="*80)
    print()

    # Initialize modules
    print("📰 Initializing news scraper (10 sources)...")
    scraper = IndonesianNewsScraper()

    print("🧠 Initializing sentiment analyzer (200+ keywords)...")
    analyzer = IndonesianSentimentAnalyzer()
    print()

    # Scrape news for SUPA
    print("🔍 Scraping news for SUPA from 10 sources...")
    print("   (This will take ~5-10 seconds due to rate limiting)")
    print()

    news_df = scraper.scrape_all("SUPA", limit=3)

    print()
    print("="*80)
    print("📊 NEWS SCRAPING RESULTS:")
    print("="*80)

    if news_df.empty:
        print("⚠️  No articles found for SUPA")
        print("   This might mean:")
        print("   - SUPA tidak banyak diberitakan")
        print("   - Scraper perlu adjustment untuk keyword")
        print("   - Network issue")
        return

    # Display summary
    print(f"✅ Found {len(news_df)} unique articles")
    print(f"📰 Sources: {news_df['source'].nunique()} different news outlets")
    print()
    print("Sources breakdown:")
    source_counts = news_df['source'].value_counts()
    for source, count in source_counts.items():
        print(f"   - {source}: {count} articles")
    print()

    # Analyze sentiment
    print("="*80)
    print("🧠 SENTIMENT ANALYSIS:")
    print("="*80)

    articles = news_df.to_dict('records')
    sentiment_result = analyzer.analyze_articles(articles)

    print(f"Overall Sentiment: {sentiment_result['overall_sentiment'].upper()}")
    print(f"Average Score: {sentiment_result['average_score']:.3f} (range: -1 to +1)")
    print(f"Total Articles: {sentiment_result['total_articles']}")
    print()

    # Sentiment distribution
    dist = sentiment_result['sentiment_distribution']
    print("Distribution:")
    print(f"   🟢 Positive: {dist['positive']}")
    print(f"   🟡 Neutral: {dist['neutral']}")
    print(f"   🔴 Negative: {dist['negative']}")
    print()

    # Show individual articles
    print("="*80)
    print("📄 INDIVIDUAL ARTICLES:")
    print("="*80)

    for i, article_sent in enumerate(sentiment_result['article_sentiments'][:5], 1):
        print(f"\n{i}. {article_sent['title'][:100]}...")
        print(f"   Sentiment: {article_sent['sentiment'].upper()} (score: {article_sent['score']:.3f})")
        print(f"   Confidence: {article_sent['confidence']:.3f}")

        # Check for fundamental events
        if article_sent.get('has_fundamental_event'):
            print(f"   🚨 FUNDAMENTAL EVENTS DETECTED:")
            for event in article_sent.get('fundamental_events', []):
                event_type = "🟢" if event['type'] == 'positive' else "🔴"
                print(f"      {event_type} {event['event']}")

        print(f"   Keywords: +{article_sent['positive_count']} / -{article_sent['negative_count']}")

    # Prediction impact
    print()
    print("="*80)
    print("🎯 PREDICTION IMPACT:")
    print("="*80)

    sentiment_score = sentiment_result['average_score']
    total_articles = sentiment_result['total_articles']

    # Calculate momentum boost (same logic as in app.py)
    sentiment_momentum = sentiment_score * 50

    if total_articles >= 20:
        sentiment_momentum *= 1.3
        coverage = "HIGH"
    elif total_articles >= 10:
        sentiment_momentum *= 1.15
        coverage = "MEDIUM"
    else:
        coverage = "LOW"

    # Add fundamental event impact
    fundamental_boost = 0
    for article_sent in sentiment_result['article_sentiments']:
        if article_sent.get('has_fundamental_event'):
            for event in article_sent.get('fundamental_events', []):
                if event['type'] == 'positive':
                    fundamental_boost += 25
                else:
                    fundamental_boost -= 25

    total_momentum = sentiment_momentum + fundamental_boost

    print(f"News Coverage: {coverage}")
    print(f"Sentiment Momentum: {sentiment_momentum:+.1f}")
    print(f"Fundamental Event Boost: {fundamental_boost:+.1f}")
    print(f"TOTAL MOMENTUM IMPACT: {total_momentum:+.1f}")
    print()

    if total_momentum > 30:
        print("💡 Impact: STRONG BULLISH signal dari news sentiment!")
        print("   Predictions akan sangat positif untuk SUPA")
    elif total_momentum > 10:
        print("💡 Impact: BULLISH signal dari news sentiment")
        print("   Predictions akan cenderung naik untuk SUPA")
    elif total_momentum < -30:
        print("💡 Impact: STRONG BEARISH signal dari news sentiment!")
        print("   Predictions akan sangat negatif untuk SUPA")
    elif total_momentum < -10:
        print("💡 Impact: BEARISH signal dari news sentiment")
        print("   Predictions akan cenderung turun untuk SUPA")
    else:
        print("💡 Impact: NEUTRAL sentiment")
        print("   News tidak memberikan signal kuat untuk SUPA")

    print()
    print("="*80)
    print("✅ TEST COMPLETE!")
    print("="*80)

if __name__ == "__main__":
    test_supa_news()
