"""
Automated News Scraper Service
Runs scheduled scraping tasks for all stocks in the portfolio
Scrapes at 08:00, 12:00, 16:00 WIB daily
"""
import sys
import os
from datetime import datetime, timedelta
import time
import pytz

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.news_scraper import IndonesianNewsScraper
from utils.sentiment_analyzer import IndonesianSentimentAnalyzer
from database.news_database import get_news_database
import yfinance as yf


class AutomatedScraperService:
    """Service for automated news scraping and sentiment analysis"""

    def __init__(self, stock_list):
        """
        Initialize automated scraper

        Args:
            stock_list: List of stock codes to monitor (e.g., ['BBCA', 'BBRI', ...])
        """
        self.stock_list = stock_list
        self.news_scraper = IndonesianNewsScraper()
        self.sentiment_analyzer = IndonesianSentimentAnalyzer()
        self.db = get_news_database()
        self.wib_tz = pytz.timezone('Asia/Jakarta')

        print(f"🤖 Automated Scraper initialized for {len(stock_list)} stocks")

    def scrape_and_store_news(self, stock_code):
        """
        Scrape news for a single stock and store in database

        Returns:
            dict with scraping results
        """
        print(f"\n📰 Scraping news for {stock_code}...")

        try:
            # Scrape from all 10 sources
            news_df = self.news_scraper.scrape_all(stock_code, limit=5)  # 5 per source = 50 max

            if news_df is None or news_df.empty:
                print(f"⚠️ No news found for {stock_code}")
                self.db.log_scraping_run(
                    stock_code=stock_code,
                    scrape_type='scheduled',
                    articles_scraped=0,
                    sources_scraped=0,
                    success=True
                )
                return {'success': True, 'articles': 0, 'sources': 0}

            # Analyze sentiment for all articles
            news_articles = news_df.to_dict('records')
            sentiment_result = self.sentiment_analyzer.analyze_articles(news_articles)

            # Prepare articles with sentiment for database
            articles_data = []
            for article, article_sentiment in zip(news_articles, sentiment_result.get('article_sentiments', [])):
                articles_data.append({
                    'stock_code': stock_code,
                    'source': article.get('source'),
                    'title': article.get('title'),
                    'url': article.get('url'),
                    'content': None,  # We don't scrape full content yet
                    'published_date': article.get('published'),
                    'sentiment_score': article_sentiment.get('sentiment_score'),
                    'sentiment_label': article_sentiment.get('sentiment_label'),
                    'has_fundamental_event': article_sentiment.get('has_fundamental_event', False)
                })

            # Store in database
            inserted = self.db.insert_news_batch(articles_data)

            # Update daily sentiment summary
            today = datetime.now(self.wib_tz).date().isoformat()
            self.db.update_daily_sentiment(
                stock_code=stock_code,
                date=today,
                avg_sentiment=sentiment_result.get('average_score', 0),
                total_articles=sentiment_result.get('total_articles', 0),
                positive_count=sentiment_result.get('positive_count', 0),
                negative_count=sentiment_result.get('negative_count', 0),
                neutral_count=sentiment_result.get('neutral_count', 0),
                fundamental_events_count=sentiment_result.get('fundamental_events_count', 0),
                sources_count=len(news_df['source'].unique())
            )

            # Log scraping run
            self.db.log_scraping_run(
                stock_code=stock_code,
                scrape_type='scheduled',
                articles_scraped=inserted,
                sources_scraped=len(news_df['source'].unique()),
                success=True
            )

            print(f"✅ {stock_code}: {inserted} articles stored, avg sentiment: {sentiment_result.get('average_score', 0):.3f}")

            return {
                'success': True,
                'articles': inserted,
                'sources': len(news_df['source'].unique()),
                'avg_sentiment': sentiment_result.get('average_score', 0)
            }

        except Exception as e:
            print(f"❌ Error scraping {stock_code}: {e}")
            self.db.log_scraping_run(
                stock_code=stock_code,
                scrape_type='scheduled',
                articles_scraped=0,
                sources_scraped=0,
                success=False,
                error_message=str(e)
            )
            return {'success': False, 'error': str(e)}

    def update_stock_prices(self, stock_code, days=7):
        """
        Update stock price history in database

        Args:
            stock_code: Stock code (e.g., 'BBCA')
            days: Number of days to fetch
        """
        try:
            ticker = f"{stock_code}.JK"
            stock = yf.Ticker(ticker)
            df = stock.history(period=f"{days}d", interval="1d")

            if df.empty:
                print(f"⚠️ No price data for {stock_code}")
                return

            # Prepare price data
            price_data = []
            for date, row in df.iterrows():
                price_data.append({
                    'stock_code': stock_code,
                    'date': date.date().isoformat(),
                    'open': row['Open'],
                    'high': row['High'],
                    'low': row['Low'],
                    'close': row['Close'],
                    'volume': int(row['Volume'])
                })

            # Store in database
            self.db.insert_price_batch(price_data)
            print(f"✅ {stock_code}: {len(price_data)} price records updated")

        except Exception as e:
            print(f"❌ Error updating prices for {stock_code}: {e}")

    def run_scraping_cycle(self):
        """
        Run one complete scraping cycle for all stocks

        This is called by the scheduler at 08:00, 12:00, 16:00 WIB
        """
        now_wib = datetime.now(self.wib_tz)
        print(f"\n{'='*60}")
        print(f"🚀 SCRAPING CYCLE STARTED")
        print(f"⏰ Time: {now_wib.strftime('%Y-%m-%d %H:%M:%S')} WIB")
        print(f"📊 Stocks: {len(self.stock_list)}")
        print(f"{'='*60}\n")

        total_articles = 0
        total_sources = 0
        success_count = 0
        failed_stocks = []

        # Scrape news for each stock
        for i, stock_code in enumerate(self.stock_list, 1):
            print(f"\n[{i}/{len(self.stock_list)}] Processing {stock_code}...")

            # Scrape news
            result = self.scrape_and_store_news(stock_code)

            if result['success']:
                total_articles += result.get('articles', 0)
                total_sources += result.get('sources', 0)
                success_count += 1
            else:
                failed_stocks.append(stock_code)

            # Update price data
            self.update_stock_prices(stock_code, days=7)

            # Rate limiting - wait 2 seconds between stocks
            if i < len(self.stock_list):
                time.sleep(2)

        # Summary
        print(f"\n{'='*60}")
        print(f"✅ SCRAPING CYCLE COMPLETED")
        print(f"📈 Success: {success_count}/{len(self.stock_list)} stocks")
        print(f"📰 Total articles: {total_articles}")
        print(f"🌐 Total sources: {total_sources}")
        if failed_stocks:
            print(f"❌ Failed: {', '.join(failed_stocks)}")
        print(f"⏰ Finished: {datetime.now(self.wib_tz).strftime('%Y-%m-%d %H:%M:%S')} WIB")
        print(f"{'='*60}\n")

        return {
            'success_count': success_count,
            'total_articles': total_articles,
            'total_sources': total_sources,
            'failed_stocks': failed_stocks
        }

    def run_continuous(self, scrape_times=['08:00', '12:00', '16:00']):
        """
        Run continuous service that scrapes at scheduled times

        Args:
            scrape_times: List of times in HH:MM format (WIB timezone)
        """
        print(f"\n{'='*60}")
        print(f"🤖 AUTOMATED SCRAPER SERVICE STARTED")
        print(f"📅 Schedule: {', '.join(scrape_times)} WIB daily")
        print(f"📊 Monitoring {len(self.stock_list)} stocks")
        print(f"{'='*60}\n")

        last_scrape_date = None

        while True:
            try:
                now_wib = datetime.now(self.wib_tz)
                current_time = now_wib.strftime('%H:%M')
                current_date = now_wib.date()

                # Check if it's time to scrape
                should_scrape = False

                # Check each scheduled time
                for scrape_time in scrape_times:
                    # Check if current time matches scheduled time (within 1 minute)
                    scheduled_hour, scheduled_min = map(int, scrape_time.split(':'))
                    if (now_wib.hour == scheduled_hour and
                        now_wib.minute == scheduled_min and
                        last_scrape_date != current_date):
                        should_scrape = True
                        break

                if should_scrape:
                    # Run scraping cycle
                    self.run_scraping_cycle()
                    last_scrape_date = current_date

                    # After scraping, show next scheduled time
                    next_time = self._get_next_scrape_time(scrape_times)
                    print(f"⏰ Next scrape: {next_time} WIB")

                # Wait 60 seconds before checking again
                time.sleep(60)

            except KeyboardInterrupt:
                print("\n🛑 Service stopped by user")
                break
            except Exception as e:
                print(f"❌ Error in continuous loop: {e}")
                time.sleep(60)

    def _get_next_scrape_time(self, scrape_times):
        """Get next scheduled scrape time"""
        now_wib = datetime.now(self.wib_tz)
        current_minutes = now_wib.hour * 60 + now_wib.minute

        for scrape_time in scrape_times:
            hour, minute = map(int, scrape_time.split(':'))
            scheduled_minutes = hour * 60 + minute

            if scheduled_minutes > current_minutes:
                return scrape_time

        # If no more today, return first time tomorrow
        return f"{scrape_times[0]} (tomorrow)"


def main():
    """Main entry point for running the service"""
    # Stock list - you can customize this
    STOCK_LIST = [
        'BBCA', 'BBRI', 'BMRI', 'TLKM', 'ASII',
        'UNVR', 'GOTO', 'ACES', 'ICBP', 'EMTK', 'SUPA'
    ]

    # Initialize service
    service = AutomatedScraperService(STOCK_LIST)

    # Run one cycle immediately for testing
    print("🧪 Running test cycle...")
    service.run_scraping_cycle()

    # Ask user if they want to run continuous mode
    print("\n" + "="*60)
    response = input("Run in continuous mode? (y/n): ")

    if response.lower() == 'y':
        # Run continuous service
        service.run_continuous(scrape_times=['08:00', '12:00', '16:00'])
    else:
        print("✅ Test cycle completed. Exiting.")


if __name__ == "__main__":
    main()
