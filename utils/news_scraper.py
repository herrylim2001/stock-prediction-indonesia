"""
News Scraper for Indonesian Financial Media
Scrapes news from 10+ Indonesian financial news sources
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import pandas as pd
import re
import time

class IndonesianNewsScraper:
    """Scraper for Indonesian financial news - EXPANDED to 10+ sources"""

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.sources = {
            'detik': 'https://finance.detik.com/',
            'cnbc': 'https://www.cnbcindonesia.com/',
            'kontan': 'https://www.kontan.co.id/',
            'cnn': 'https://www.cnnindonesia.com/',
            'investor': 'https://investor.id/',
            'idx_channel': 'https://www.idxchannel.com/',
            'bisnis': 'https://market.bisnis.com/',
            'kompas': 'https://money.kompas.com/',
            'tempo': 'https://bisnis.tempo.co/',
            'bareksa': 'https://www.bareksa.com/'
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

    def scrape_cnn_indonesia(self, keyword="saham", limit=10):
        """Scrape news from CNN Indonesia"""
        try:
            search_url = f"https://www.cnnindonesia.com/search/?query={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all('article', limit=limit):
                try:
                    title_elem = article.find('h2') or article.find('a')
                    link_elem = article.find('a')
                    time_elem = article.find('span', class_='date')

                    if title_elem and link_elem:
                        articles.append({
                            'source': 'CNN Indonesia',
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping CNN Indonesia: {e}")
            return []

    def scrape_investor_daily(self, keyword="saham", limit=10):
        """Scrape news from Investor Daily"""
        try:
            search_url = f"https://investor.id/search?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all(['article', 'div'], class_=['post', 'article-item'], limit=limit):
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a')
                    time_elem = article.find(['time', 'span'], class_=['date', 'time'])

                    if title_elem and link_elem:
                        url = link_elem.get('href', '')
                        if not url.startswith('http'):
                            url = 'https://investor.id' + url

                        articles.append({
                            'source': 'Investor Daily',
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Investor Daily: {e}")
            return []

    def scrape_idx_channel(self, keyword="saham", limit=10):
        """Scrape news from IDX Channel"""
        try:
            search_url = f"https://www.idxchannel.com/search?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all(['article', 'div'], class_=['article', 'news-item'], limit=limit):
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a')
                    time_elem = article.find(['time', 'span'], class_=['date', 'time'])

                    if title_elem and link_elem:
                        url = link_elem.get('href', '')
                        if not url.startswith('http'):
                            url = 'https://www.idxchannel.com' + url

                        articles.append({
                            'source': 'IDX Channel',
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping IDX Channel: {e}")
            return []

    def scrape_bisnis_com(self, keyword="saham", limit=10):
        """Scrape news from Bisnis.com"""
        try:
            search_url = f"https://market.bisnis.com/search?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all(['article', 'div'], class_=['article', 'list-news'], limit=limit):
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a')
                    time_elem = article.find(['time', 'span'], class_=['date', 'time'])

                    if title_elem and link_elem:
                        url = link_elem.get('href', '')
                        if not url.startswith('http'):
                            url = 'https://market.bisnis.com' + url

                        articles.append({
                            'source': 'Bisnis.com',
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Bisnis.com: {e}")
            return []

    def scrape_kompas_money(self, keyword="saham", limit=10):
        """Scrape news from Kompas Money"""
        try:
            search_url = f"https://money.kompas.com/search/{keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all(['article', 'div'], class_=['article__list', 'latest__item'], limit=limit):
                try:
                    title_elem = article.find(['h3', 'h2', 'a'])
                    link_elem = article.find('a')
                    time_elem = article.find(['time', 'span', 'div'], class_=['article__date', 'date'])

                    if title_elem and link_elem:
                        articles.append({
                            'source': 'Kompas Money',
                            'title': title_elem.get_text(strip=True),
                            'url': link_elem.get('href', ''),
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Kompas Money: {e}")
            return []

    def scrape_tempo_bisnis(self, keyword="saham", limit=10):
        """Scrape news from Tempo Bisnis"""
        try:
            search_url = f"https://bisnis.tempo.co/search?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all(['article', 'div'], class_=['card', 'list-news'], limit=limit):
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a')
                    time_elem = article.find(['time', 'span'], class_=['date', 'time'])

                    if title_elem and link_elem:
                        url = link_elem.get('href', '')
                        if not url.startswith('http'):
                            url = 'https://bisnis.tempo.co' + url

                        articles.append({
                            'source': 'Tempo Bisnis',
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Tempo Bisnis: {e}")
            return []

    def scrape_bareksa(self, keyword="saham", limit=10):
        """Scrape news from Bareksa"""
        try:
            search_url = f"https://www.bareksa.com/search?q={keyword}"
            response = requests.get(search_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')

            articles = []
            for article in soup.find_all(['article', 'div'], class_=['article', 'news-item'], limit=limit):
                try:
                    title_elem = article.find(['h2', 'h3', 'a'])
                    link_elem = article.find('a')
                    time_elem = article.find(['time', 'span'], class_=['date', 'time'])

                    if title_elem and link_elem:
                        url = link_elem.get('href', '')
                        if not url.startswith('http'):
                            url = 'https://www.bareksa.com' + url

                        articles.append({
                            'source': 'Bareksa',
                            'title': title_elem.get_text(strip=True),
                            'url': url,
                            'published': time_elem.get_text(strip=True) if time_elem else 'N/A',
                            'scraped_at': datetime.now()
                        })
                except Exception as e:
                    continue

            return articles
        except Exception as e:
            print(f"Error scraping Bareksa: {e}")
            return []

    def scrape_all(self, stock_code, limit=3):
        """
        Scrape news from ALL 10 sources for a specific stock

        Args:
            stock_code: Stock ticker (e.g., 'BBCA', 'TLKM')
            limit: Articles per source (default: 3)

        Returns:
            DataFrame with all articles sorted by recency
        """
        keyword = f"saham {stock_code}"

        all_articles = []

        # Scrape from ALL 10 sources with rate limiting to avoid being blocked
        print(f"📰 Scraping news for {stock_code} from 10 sources...")

        # Original 3 sources
        all_articles.extend(self.scrape_detik_finance(keyword, limit))
        time.sleep(0.5)  # Rate limiting
        all_articles.extend(self.scrape_cnbc_indonesia(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_kontan(keyword, limit))
        time.sleep(0.5)

        # NEW 7 sources
        all_articles.extend(self.scrape_cnn_indonesia(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_investor_daily(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_idx_channel(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_bisnis_com(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_kompas_money(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_tempo_bisnis(keyword, limit))
        time.sleep(0.5)
        all_articles.extend(self.scrape_bareksa(keyword, limit))

        # Convert to DataFrame
        if all_articles:
            df = pd.DataFrame(all_articles)
            df = df.drop_duplicates(subset=['title'], keep='first')
            df = df.sort_values('scraped_at', ascending=False)
            print(f"✅ Found {len(df)} unique articles from {df['source'].nunique()} sources")
            return df

        print("⚠️ No articles found")
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
