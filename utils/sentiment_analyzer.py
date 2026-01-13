"""
Sentiment Analyzer for Indonesian Financial News
ENHANCED: 200+ keywords + Fundamental Event Detection
"""
import re
from typing import Dict, List
from datetime import datetime, timedelta

class IndonesianSentimentAnalyzer:
    """ENHANCED sentiment analyzer for Indonesian financial news"""

    def __init__(self):
        # === EXPANDED POSITIVE KEYWORDS (100+ bullish indicators) ===
        self.positive_keywords = [
            # Price movement
            'naik', 'meningkat', 'tumbuh', 'menguat', 'melesat', 'rally', 'gain', 'rebound',
            'melonjak', 'menanjak', 'beranjak naik', 'terangkat', 'melambung', 'membaik',

            # Performance
            'positif', 'untung', 'profit', 'laba', 'cuan', 'surplus', 'kinerja baik',
            'performa bagus', 'pencapaian', 'capaian', 'prestasi', 'rekor', 'tertinggi',

            # Market sentiment
            'optimis', 'bullish', 'optimisme', 'antusias', 'greget', 'bergairah',
            'semangat', 'kepercayaan tinggi', 'yakin', 'percaya diri', 'positif outlook',

            # Growth & expansion
            'ekspansi', 'berkembang', 'tumbuh pesat', 'pertumbuhan', 'peningkatan',
            'akselerasi', 'momentum', 'dinamis', 'agresif', 'masif', 'progres',

            # Innovation & breakthrough
            'terobosan', 'inovasi', 'breakthrough', 'disruptif', 'transformasi',
            'modernisasi', 'digitalisasi', 'efisiensi', 'produktif', 'kompetitif',

            # Financial health
            'sehat', 'solid', 'kuat', 'tangguh', 'kokoh', 'stabil positif',
            'likuid', 'bonafide', 'kredibel', 'terpercaya', 'fundamental kuat',

            # Business success
            'sukses', 'berhasil', 'cemerlang', 'gemilang', 'moncer', 'cakep',
            'bagus', 'baik', 'mantap', 'oke', 'jos', 'ciamik', 'apik',

            # Recovery & improvement
            'recovery', 'pemulihan', 'pulih', 'bangkit', 'rebound', 'turnaround',
            'perbaikan', 'membaik', 'meningkat', 'menguat kembali',

            # Investment & demand
            'permintaan tinggi', 'diminati', 'dicari', 'populer', 'favorit',
            'investasi', 'akuisisi', 'ekspor naik', 'penjualan meningkat',

            # Dividend & earnings
            'dividen', 'dividend', 'bagi hasil', 'earning naik', 'eps naik',
            'revenue naik', 'pendapatan naik', 'margin naik', 'roi tinggi'
        ]

        # === EXPANDED NEGATIVE KEYWORDS (100+ bearish indicators) ===
        self.negative_keywords = [
            # Price movement
            'turun', 'menurun', 'jatuh', 'merosot', 'anjlok', 'terjun', 'ambles',
            'melemah', 'terkoreksi', 'susut', 'menyusut', 'tergerus', 'terpangkas',

            # Performance
            'negatif', 'rugi', 'loss', 'defisit', 'merugi', 'boncos', 'bangkrut',
            'pailit', 'kolaps', 'gagal', 'buruk', 'jelek', 'payah', 'terburuk',

            # Market sentiment
            'pesimis', 'bearish', 'khawatir', 'cemas', 'takut', 'panik', 'waspada',
            'hati-hati', 'wait and see', 'menunggu', 'ragu', 'tidak yakin',

            # Crisis & problems
            'krisis', 'resesi', 'stagflasi', 'inflasi tinggi', 'pelemahan',
            'perlambatan', 'kontraksi', 'tekanan', 'hambatan', 'kendala',

            # Bankruptcy & failure
            'bangkrut', 'pailit', 'kolaps', 'crash', 'ambruk', 'terpuruk',
            'collapse', 'gagal bayar', 'default', 'likuidasi', 'tutup',

            # Financial problems
            'utang', 'debt', 'terlilit', 'beban', 'burden', 'NPL tinggi',
            'kredit macet', 'piutang ragu', 'cash flow negatif', 'burn rate tinggi',

            # Operational issues
            'produksi turun', 'sales turun', 'revenue turun', 'margin tertekan',
            'biaya naik', 'cost overrun', 'delay', 'terlambat', 'mundur',

            # Regulatory & legal
            'sanksi', 'denda', 'penalty', 'investigasi', 'audit', 'pelanggaran',
            'fraud', 'korupsi', 'skandal', 'kasus', 'gugatan', 'lawsuit',

            # Market risks
            'risiko', 'ancaman', 'bahaya', 'warning', 'peringatan', 'volatilitas tinggi',
            'uncertainty', 'ketidakpastian', 'kekhawatiran', 'kegagalan',

            # Downgrade & negative outlook
            'downgrade', 'penurunan rating', 'outlook negatif', 'revisi turun',
            'target turun', 'estimasi turun', 'proyeksi turun'
        ]

        # === NEUTRAL KEYWORDS ===
        self.neutral_keywords = [
            'stabil', 'flat', 'sideways', 'konsolidasi', 'wait and see',
            'tunggu', 'monitor', 'observe', 'pantau', 'datar', 'variatif',
            'mixed', 'campur aduk', 'fluktuatif ringan', 'berimbang'
        ]

        # === STRONG POSITIVE INDICATORS (3x weight) ===
        self.strong_positive = [
            'sangat naik', 'lonjakan tajam', 'melesat tinggi', 'melonjak drastis',
            'booming', 'skyrocket', 'record high', 'rekor tertinggi', 'ATH',
            'all time high', 'fantastis', 'luar biasa', 'spektakuler',
            'fenomenal', 'bombastis', 'extraordinary', 'breakout', 'surge'
        ]

        # === STRONG NEGATIVE INDICATORS (3x weight) ===
        self.strong_negative = [
            'sangat turun', 'anjlok drastis', 'crash parah', 'collapsed',
            'krisis parah', 'ambruk', 'terpuruk parah', 'kehancuran',
            'bencana', 'meltdown', 'free fall', 'jatuh bebas', 'record low',
            'rekor terendah', 'ATL', 'all time low', 'panic selling'
        ]

        # === FUNDAMENTAL EVENTS (high impact) ===
        self.fundamental_positive = [
            'buyback', 'stock split', 'dividen naik', 'dividend increase',
            'earnings beat', 'laba melampaui', 'akuisisi positif', 'merger',
            'kontrak besar', 'ekspansi besar', 'IPO sukses', 'listing',
            'right issue oversubscribed', 'CEO baru yang kuat', 'manajemen baru'
        ]

        self.fundamental_negative = [
            'earnings miss', 'laba turun', 'right issue', 'delisting',
            'suspend', 'ditangguhkan', 'CEO resign', 'CEO mundur',
            'management reshuffle', 'restrukturisasi utang', 'debt restructuring',
            'dividen dipotong', 'dividend cut', 'profit warning', 'guidance turun'
        ]

    def analyze_text(self, text: str) -> Dict:
        """
        ENHANCED: Analyze sentiment with 200+ keywords + fundamental event detection

        Returns:
            dict: {
                'sentiment': 'positive'|'negative'|'neutral',
                'score': float (-1 to 1),
                'confidence': float (0 to 1),
                'fundamental_events': list of detected events
            }
        """
        if not text:
            return {
                'sentiment': 'neutral',
                'score': 0.0,
                'confidence': 0.0,
                'fundamental_events': []
            }

        text_lower = text.lower()

        # Count regular keywords (1x weight)
        pos_count = sum(1 for word in self.positive_keywords if word in text_lower)
        neg_count = sum(1 for word in self.negative_keywords if word in text_lower)
        neu_count = sum(1 for word in self.neutral_keywords if word in text_lower)

        # Count strong indicators (3x weight - increased from 2x!)
        strong_pos = sum(3 for phrase in self.strong_positive if phrase in text_lower)
        strong_neg = sum(3 for phrase in self.strong_negative if phrase in text_lower)

        # Detect fundamental events (5x weight - VERY high impact!)
        fundamental_events = []
        fundamental_pos = 0
        fundamental_neg = 0

        for event in self.fundamental_positive:
            if event in text_lower:
                fundamental_events.append({'type': 'positive', 'event': event})
                fundamental_pos += 5  # 5x weight!

        for event in self.fundamental_negative:
            if event in text_lower:
                fundamental_events.append({'type': 'negative', 'event': event})
                fundamental_neg += 5  # 5x weight!

        # Calculate total scores with all weights
        total_pos = pos_count + strong_pos + fundamental_pos
        total_neg = neg_count + strong_neg + fundamental_neg
        total_words = pos_count + neg_count + neu_count + (strong_pos // 3) + (strong_neg // 3) + len(fundamental_events)

        # Calculate sentiment score (-1 to 1)
        if total_words == 0:
            score = 0.0
            sentiment = 'neutral'
            confidence = 0.0
        else:
            # Weighted score calculation
            score = (total_pos - total_neg) / max(total_pos + total_neg + neu_count, 1)
            score = max(-1.0, min(1.0, score))  # Clamp to [-1, 1]

            # Determine sentiment category (tighter thresholds for better accuracy)
            if score > 0.15:
                sentiment = 'positive'
            elif score < -0.15:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'

            # Calculate confidence based on number of keywords found
            # Higher confidence with more keywords
            confidence = min(total_words / 15.0, 1.0)  # Max confidence at 15+ keywords

            # Boost confidence if fundamental events detected
            if fundamental_events:
                confidence = min(confidence + 0.2, 1.0)  # +20% confidence for fundamental events

        return {
            'sentiment': sentiment,
            'score': round(score, 3),
            'confidence': round(confidence, 3),
            'positive_count': total_pos,
            'negative_count': total_neg,
            'neutral_count': neu_count,
            'fundamental_events': fundamental_events,
            'has_fundamental_event': len(fundamental_events) > 0
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
