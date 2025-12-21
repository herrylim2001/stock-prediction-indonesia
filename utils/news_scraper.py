"""
News Scraper for Indonesian Financial Media
Scrapes news from Detik Finance, RTI Business, CNBC Indonesia
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import re

class IndonesianNewsScraper:
    """Scraper for Indonesian financial news"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        self.sources = {
            'detik': 'https://finance.detik.com/',
            'cnbc': 'https://www.cnbcindonesia.com/',
            'kontan': 'https://www.kontan.co.id/'
        }

    def scrape_detik_finance(self, keyword="saham", limit=10):
        """Scrape news from Detik Finance"""
        try:
            search_url = f"https://finance.detik.com/search?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all('article', limit=limit):
                try:
                    title_elem = article.find('h3') or article.find('h2')
                    link_elem = article.find('a')
                    time_elem = article.find('time') or article.find('span', class_='date')

                    if title_elem and link_elem:
                        articles.append({
                            'source': 'Detik Finance',
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Detik: {e}")
            return []

    def scrape_cnbc_indonesia(self, keyword="saham", limit=10):
        """Scrape news from CNBC Indonesia"""
        try:
            search_url = f"https://www.cnbcindonesia.com/search?query={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all('div', class_='list_content', limit=limit):
                try:
                    title_elem = article.find('h4') or article.find('a')
                    link_elem = article.find('a')
                    time_elem = article.find('span', class_='date')

                    if title_elem and link_elem:
                        articles.append({
                            'source': 'CNBC Indonesia',
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping CNBC: {e}")
            return []

    def scrape_kontan(self, keyword="saham", limit=10):
        """Scrape news from Kontan"""
        try:
            search_url = f"https://www.kontan.co.id/search/?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all('div', class_='item-berita', limit=limit):
                try:
                    title_elem = article.find('h3') or article.find('a')
                    link_elem = article.find('a')
                    time_elem = article.find('span', class_='waktu')

                    if title_elem and link_elem:
                        articles.append({
                            'source': 'Kontan',
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Kontan: {e}")
            return []

    def scrape_all(self, stock_code, limit=5):
        """Scrape news from all sources for a specific stock"""
        keyword = f"saham {stock_code}"

        all_articles = []

        # Scrape from all sources
        all_articles.extend(self.scrape_detik_finance(keyword, limit))
        all_articles.extend(self.scrape_cnbc_indonesia(keyword, limit))
        all_articles.extend(self.scrape_kontan(keyword, limit))

        # Convert to DataFrame
        if all_articles:
            df = pd.DataFrame(all_articles)
            df = df.drop_duplicates(subset=['title'], keep='first')
            df = df.sort_values('scraped_at', ascending=False)
            return df

        return pd.DataFrame()

    def get_stock_news_summary(self, stock_code, days=7):
        """Get news summary for a stock in the last N days"""
        df = self.scrape_all(stock_code)

        if df.empty:
            return {
                'total_articles': 0,
                'sources': [],
                'latest_news': []
            }

        return {
            'total_articles': len(df),
            'sources': df['source'].unique().tolist(),
            'latest_news': df.head(5).to_dict('records')
        }


# Example usage
if __name__ == "__main__":
    scraper = IndonesianNewsScraper()

    # Test scraping for BBCA
    print("Testing news scraper for BBCA...")
    news = scraper.scrape_all("BBCA", limit=3)

    if not news.empty:
        print(f"\nFound {len(news)} articles:")
        for _, article in news.iterrows():
            print(f"- [{article['source']}] {article['title'][:80]}...")
    else:
        print("No articles found")
