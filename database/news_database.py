"""
News Database Module
SQLite database for storing historical news, sentiment, and price data
For automated daily learning and sentiment trend tracking
"""
import sqlite3
import pandas as pd
from datetime import datetime, timedelta
import json
import os


class NewsDatabase:
    """Database manager for news articles and sentiment analysis"""

    def __init__(self, db_path='data/stock_news.db'):
        """Initialize database connection"""
        self.db_path = db_path

        # Create data directory if not exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

    def _init_database(self):
        """Create database tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Table 1: News Articles
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                source TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT,
                content TEXT,
                published_date TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                sentiment_score REAL,
                sentiment_label TEXT,
                has_fundamental_event BOOLEAN DEFAULT 0,
                UNIQUE(stock_code, title, source)
            )
        """)

        # Table 2: Sentiment Daily Summary
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sentiment_daily (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                date DATE NOT NULL,
                avg_sentiment REAL,
                total_articles INTEGER,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                fundamental_events_count INTEGER,
                sources_count INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, date)
            )
        """)

        # Table 3: Stock Price History (for correlation analysis)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS stock_prices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                date DATE NOT NULL,
                open REAL,
                high REAL,
                low REAL,
                close REAL,
                volume INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, date)
            )
        """)

        # Table 4: Scraping Logs (track scraping runs)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT,
                scrape_type TEXT,
                articles_scraped INTEGER,
                sources_scraped INTEGER,
                success BOOLEAN,
                error_message TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Table 5: Prediction Accuracy Log (track daily predictions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_accuracy (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                stock_code TEXT NOT NULL,
                prediction_date DATE NOT NULL,
                target_date DATE NOT NULL,
                predicted_price REAL,
                predicted_trend TEXT,
                actual_price REAL,
                actual_trend TEXT,
                error_pct REAL,
                direction_correct BOOLEAN,
                confidence REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(stock_code, prediction_date, target_date)
            )
        """)

        # Create indexes for faster queries
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_news_stock_date ON news_articles(stock_code, scraped_at)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sentiment_stock_date ON sentiment_daily(stock_code, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prices_stock_date ON stock_prices(stock_code, date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_accuracy_stock_date ON prediction_accuracy(stock_code, prediction_date)")

        conn.commit()
        conn.close()

        print(f"✅ Database initialized: {self.db_path}")

    def insert_news_article(self, stock_code, source, title, url, content=None,
                           published_date=None, sentiment_score=None,
                           sentiment_label=None, has_fundamental_event=False):
        """Insert a news article into database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        try:
            cursor.execute("""
                INSERT OR IGNORE INTO news_articles
                (stock_code, source, title, url, content, published_date,
                 sentiment_score, sentiment_label, has_fundamental_event)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (stock_code, source, title, url, content, published_date,
                  sentiment_score, sentiment_label, has_fundamental_event))

            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Error inserting article: {e}")
            return None
        finally:
            conn.close()

    def insert_news_batch(self, articles_data):
        """Insert multiple articles at once (more efficient)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        inserted = 0
        for article in articles_data:
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO news_articles
                    (stock_code, source, title, url, content, published_date,
                     sentiment_score, sentiment_label, has_fundamental_event)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.get('stock_code'),
                    article.get('source'),
                    article.get('title'),
                    article.get('url'),
                    article.get('content'),
                    article.get('published_date'),
                    article.get('sentiment_score'),
                    article.get('sentiment_label'),
                    article.get('has_fundamental_event', False)
                ))
                if cursor.rowcount > 0:
                    inserted += 1
            except Exception as e:
                print(f"Error inserting article: {e}")
                continue

        conn.commit()
        conn.close()
        return inserted

    def update_daily_sentiment(self, stock_code, date, avg_sentiment, total_articles,
                              positive_count, negative_count, neutral_count,
                              fundamental_events_count, sources_count):
        """Update daily sentiment summary"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO sentiment_daily
            (stock_code, date, avg_sentiment, total_articles, positive_count,
             negative_count, neutral_count, fundamental_events_count, sources_count)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_code, date, avg_sentiment, total_articles, positive_count,
              negative_count, neutral_count, fundamental_events_count, sources_count))

        conn.commit()
        conn.close()

    def get_sentiment_trend(self, stock_code, days=7):
        """Get sentiment trend for last N days"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT date, avg_sentiment, total_articles,
                   positive_count, negative_count, neutral_count,
                   fundamental_events_count
            FROM sentiment_daily
            WHERE stock_code = ?
            AND date >= date('now', '-' || ? || ' days')
            ORDER BY date DESC
        """

        df = pd.read_sql_query(query, conn, params=(stock_code, days))
        conn.close()

        return df

    def get_recent_news(self, stock_code, hours=24, limit=100):
        """Get recent news articles for a stock"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT * FROM news_articles
            WHERE stock_code = ?
            AND scraped_at >= datetime('now', '-' || ? || ' hours')
            ORDER BY scraped_at DESC
            LIMIT ?
        """

        df = pd.read_sql_query(query, conn, params=(stock_code, hours, limit))
        conn.close()

        return df

    def insert_stock_price(self, stock_code, date, open_price, high, low, close, volume):
        """Insert daily stock price"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO stock_prices
            (stock_code, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (stock_code, date, open_price, high, low, close, volume))

        conn.commit()
        conn.close()

    def insert_price_batch(self, price_data):
        """Insert multiple price records"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        for price in price_data:
            cursor.execute("""
                INSERT OR REPLACE INTO stock_prices
                (stock_code, date, open, high, low, close, volume)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                price.get('stock_code'),
                price.get('date'),
                price.get('open'),
                price.get('high'),
                price.get('low'),
                price.get('close'),
                price.get('volume')
            ))

        conn.commit()
        conn.close()

    def log_scraping_run(self, stock_code, scrape_type, articles_scraped,
                        sources_scraped, success=True, error_message=None):
        """Log a scraping run"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO scraping_logs
            (stock_code, scrape_type, articles_scraped, sources_scraped,
             success, error_message)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (stock_code, scrape_type, articles_scraped, sources_scraped,
              success, error_message))

        conn.commit()
        conn.close()

    def insert_prediction_accuracy(self, stock_code, prediction_date, target_date,
                                   predicted_price, predicted_trend, actual_price=None,
                                   actual_trend=None, error_pct=None,
                                   direction_correct=None, confidence=None):
        """Log prediction accuracy"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT OR REPLACE INTO prediction_accuracy
            (stock_code, prediction_date, target_date, predicted_price,
             predicted_trend, actual_price, actual_trend, error_pct,
             direction_correct, confidence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (stock_code, prediction_date, target_date, predicted_price,
              predicted_trend, actual_price, actual_trend, error_pct,
              direction_correct, confidence))

        conn.commit()
        conn.close()

    def get_prediction_accuracy_stats(self, stock_code, days=30):
        """Get prediction accuracy statistics"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT
                COUNT(*) as total_predictions,
                AVG(ABS(error_pct)) as avg_error_pct,
                MIN(ABS(error_pct)) as best_error_pct,
                MAX(ABS(error_pct)) as worst_error_pct,
                SUM(CASE WHEN direction_correct = 1 THEN 1 ELSE 0 END) * 100.0 / COUNT(*) as direction_accuracy,
                AVG(confidence) as avg_confidence
            FROM prediction_accuracy
            WHERE stock_code = ?
            AND actual_price IS NOT NULL
            AND prediction_date >= date('now', '-' || ? || ' days')
        """

        cursor = conn.cursor()
        cursor.execute(query, (stock_code, days))
        result = cursor.fetchone()
        conn.close()

        if result:
            return {
                'total_predictions': result[0],
                'avg_error_pct': result[1],
                'best_error_pct': result[2],
                'worst_error_pct': result[3],
                'direction_accuracy': result[4],
                'avg_confidence': result[5]
            }
        return None

    def get_correlation_data(self, stock_code, days=30):
        """Get sentiment vs price movement correlation data"""
        conn = sqlite3.connect(self.db_path)

        query = """
            SELECT
                p.date,
                p.close,
                p.open,
                s.avg_sentiment,
                s.total_articles,
                s.fundamental_events_count,
                (p.close - p.open) / p.open * 100 as daily_change_pct
            FROM stock_prices p
            LEFT JOIN sentiment_daily s ON p.stock_code = s.stock_code AND p.date = s.date
            WHERE p.stock_code = ?
            AND p.date >= date('now', '-' || ? || ' days')
            ORDER BY p.date DESC
        """

        df = pd.read_sql_query(query, conn, params=(stock_code, days))
        conn.close()

        return df

    def cleanup_old_data(self, days_to_keep=90):
        """Clean up old data to save space (keep last N days)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Delete old news articles
        cursor.execute("""
            DELETE FROM news_articles
            WHERE scraped_at < date('now', '-' || ? || ' days')
        """, (days_to_keep,))

        deleted_news = cursor.rowcount

        # Delete old scraping logs
        cursor.execute("""
            DELETE FROM scraping_logs
            WHERE scraped_at < date('now', '-' || ? || ' days')
        """, (days_to_keep,))

        deleted_logs = cursor.rowcount

        conn.commit()
        conn.close()

        print(f"🧹 Cleaned up: {deleted_news} old articles, {deleted_logs} old logs")
        return deleted_news, deleted_logs

    def get_stats(self):
        """Get database statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        stats = {}

        # Count articles
        cursor.execute("SELECT COUNT(*) FROM news_articles")
        stats['total_articles'] = cursor.fetchone()[0]

        # Count daily sentiment records
        cursor.execute("SELECT COUNT(*) FROM sentiment_daily")
        stats['total_daily_sentiments'] = cursor.fetchone()[0]

        # Count price records
        cursor.execute("SELECT COUNT(*) FROM stock_prices")
        stats['total_prices'] = cursor.fetchone()[0]

        # Count predictions
        cursor.execute("SELECT COUNT(*) FROM prediction_accuracy")
        stats['total_predictions'] = cursor.fetchone()[0]

        # Latest scrape
        cursor.execute("SELECT MAX(scraped_at) FROM news_articles")
        stats['latest_news_scrape'] = cursor.fetchone()[0]

        conn.close()
        return stats


# Singleton instance
_db_instance = None

def get_news_database():
    """Get singleton database instance"""
    global _db_instance
    if _db_instance is None:
        _db_instance = NewsDatabase()
    return _db_instance
