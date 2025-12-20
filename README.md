# 📈 Indonesian Stock Prediction System

## Sistem Prediksi Saham Indonesia dengan Machine Learning

### 📋 Ringkasan Project

Sistem ini dirancang untuk membantu trader/investor Indonesia dalam:
- **Memprediksi pergerakan harga saham** (per jam dan harian)
- **Memberikan rekomendasi BUY/SELL/HOLD**
- **Menghitung lot yang optimal** berdasarkan risk management
- **Forecast trend** 1 jam, 4 jam, 1 hari, dan 3 hari ke depan

---

## 🎯 Konfigurasi Kamu

| Parameter | Nilai | Keterangan |
|-----------|-------|------------|
| Modal Total | Rp 100.000.000 | Modal trading |
| Risk per Trade | 1% | = Rp 1.000.000 max loss per trade |
| Timeframe | Per Jam + Swing (3-5 hari) | Dual timeframe |
| Jumlah Saham | 10 saham | Target awal |

### 10 Saham Target

| No | Kode | Nama Perusahaan | Sektor |
|----|------|-----------------|--------|
| 1 | BBCA | Bank Central Asia | Keuangan |
| 2 | BBRI | Bank Rakyat Indonesia | Keuangan |
| 3 | TLKM | Telkom Indonesia | Telekomunikasi |
| 4 | ASII | Astra International | Otomotif |
| 5 | UNVR | Unilever Indonesia | Consumer Goods |
| 6 | BMRI | Bank Mandiri | Keuangan |
| 7 | GOTO | GoTo Gojek Tokopedia | Teknologi |
| 8 | ACES | Ace Hardware Indonesia | Retail |
| 9 | ICBP | Indofood CBP Sukses Makmur | Consumer Goods |
| 10 | EMTK | Elang Mahkota Teknologi | Media & Teknologi |

---

## 📁 Struktur Data & Templates

```
stock-prediction-system/
├── data/
│   ├── 01_stock_master.xlsx        # Daftar saham target
│   ├── 02_hourly_prices.xlsx       # Data harga per jam (sample)
│   ├── 03_daily_prices.xlsx        # Data harga harian (sample)
│   ├── 04_trading_config.xlsx      # Konfigurasi trading
│   ├── 05_prediction_output.xlsx   # Template output prediksi
│   ├── 06_technical_indicators.xlsx# Konfigurasi indikator
│   ├── template_hourly_prices.csv  # CSV template hourly
│   └── template_daily_prices.csv   # CSV template daily
├── models/                         # ML models (akan dibuat)
├── utils/                          # Utility scripts
├── api/                            # API endpoints
└── dashboard/                      # Web dashboard
```

---

## 📊 Format Data yang Diperlukan

### 1. Data Harga Per Jam (Hourly)

| Kolom | Tipe | Contoh | Keterangan |
|-------|------|--------|------------|
| timestamp | datetime | 2025-01-15 09:00:00 | Waktu WIB |
| date | string | 2025-01-15 | Tanggal |
| hour | int | 9 | Jam (9-16) |
| open | float | 9500 | Harga pembukaan |
| high | float | 9550 | Harga tertinggi |
| low | float | 9480 | Harga terendah |
| close | float | 9520 | Harga penutupan |
| volume | int | 150000 | Volume transaksi |
| value | int | 1428000000 | Nilai transaksi (opsional) |

### 2. Data Harga Harian (Daily)

| Kolom | Tipe | Contoh | Keterangan |
|-------|------|--------|------------|
| date | string | 2025-01-15 | Tanggal |
| open | float | 9500 | Harga pembukaan |
| high | float | 9650 | Harga tertinggi |
| low | float | 9450 | Harga terendah |
| close | float | 9600 | Harga penutupan |
| volume | int | 15000000 | Volume transaksi |
| value | int | 144000000000 | Nilai transaksi |
| change | float | 100 | Perubahan harga |
| change_pct | float | 1.05 | Perubahan (%) |

---

## 🔧 Cara Mendapatkan Data Saham Indonesia

### Opsi 1: Yahoo Finance (Gratis - Terbatas)
```python
import yfinance as yf

# Format ticker IDX: KODE.JK
bbca = yf.Ticker("BBCA.JK")
data = bbca.history(period="1y", interval="1d")
```

**Catatan:** Yahoo Finance untuk IDX kadang delay dan tidak lengkap.

### Opsi 2: Sectors.app API (Freemium)
- Website: https://sectors.app
- Menyediakan data fundamental dan harga
- Coverage 99% saham IDX

### Opsi 3: IDX Data Services (Official - Berbayar)
- Website: https://www.idx.co.id/en/products/idx-data-services/
- Real-time dan historical data resmi dari BEI

### Opsi 4: Manual Export dari Aplikasi Trading
Kamu bisa export data dari:
- **Stockbit**: Menu Research > Stock > Export
- **IPOT**: Menu Market Analysis > Chart > Export
- **Ajaib**: Menu Chartbit > Download data

### Opsi 5: Invezgo API (Local Provider)
- Website: https://invezgo.com/data-api-saham-indonesia
- REST API dengan data IDX

---

## 📐 Kalkulasi Risk Management

### Formula Lot Recommendation

```python
# Konfigurasi kamu:
modal_total = 100_000_000  # Rp 100 juta
risk_per_trade = 0.01      # 1%
max_loss_per_trade = modal_total * risk_per_trade  # = Rp 1.000.000

# Contoh kalkulasi untuk BBCA:
current_price = 9500       # Harga saat ini
stop_loss_pct = 0.02       # Stop loss 2%
stop_loss_price = current_price * (1 - stop_loss_pct)  # = 9310

risk_per_share = current_price - stop_loss_price  # = 190
max_shares = max_loss_per_trade / risk_per_share  # = 5263 lembar
lot_size = 100
recommended_lots = int(max_shares / lot_size)     # = 52 lot

# Verifikasi modal yang dibutuhkan:
capital_needed = recommended_lots * lot_size * current_price
# = 52 * 100 * 9500 = Rp 49.400.000 (OK, < 100 juta)

# Max position size check (10% of portfolio):
max_position = modal_total * 0.10  # = Rp 10.000.000
final_lots = min(recommended_lots, int(max_position / (lot_size * current_price)))
# = min(52, 10) = 10 lot
```

---

## 🤖 Model Machine Learning

### Primary Model: LSTM (Long Short-Term Memory)

```
Input Features:
├── Price Data (OHLCV)
├── Technical Indicators
│   ├── SMA (10, 50)
│   ├── EMA (12, 26)
│   ├── RSI (14)
│   ├── MACD (12, 26, 9)
│   ├── Bollinger Bands (20, 2)
│   ├── ATR (14)
│   └── Volume indicators
└── Time Features (hour, day_of_week)

LSTM Architecture:
├── Input Layer (sequence_length=60)
├── LSTM Layer 1 (128 units, return_sequences=True)
├── Dropout (0.2)
├── LSTM Layer 2 (64 units, return_sequences=True)
├── Dropout (0.2)
├── LSTM Layer 3 (32 units)
├── Dropout (0.2)
├── Dense Layer (16 units, ReLU)
└── Output Layer (4 units: 1h, 4h, 1d, 3d predictions)
```

### Prediction Timeframes

| Timeframe | Use Case | Confidence Target |
|-----------|----------|-------------------|
| 1 Jam | Day trading, scalping | 65-70% |
| 4 Jam | Intraday swing | 68-72% |
| 1 Hari | Daily position | 70-75% |
| 3 Hari | Swing trading | 65-72% |

**Rekomendasi Swing Trading:** 3-5 hari adalah timeframe optimal untuk swing trading di pasar Indonesia karena:
- Cukup waktu untuk trend berkembang
- Menghindari noise intraday
- Fee trading lebih efisien

---

## 🚀 Deployment Plan (Cloud)

### Recommended Stack

```
┌─────────────────────────────────────────────────────────────┐
│                     CLOUD ARCHITECTURE                       │
├─────────────────────────────────────────────────────────────┤
│  Frontend (Vercel/Netlify)                                  │
│  └── Next.js Dashboard                                      │
├─────────────────────────────────────────────────────────────┤
│  Backend API (Railway/Render/GCP Cloud Run)                 │
│  └── FastAPI + Python                                       │
├─────────────────────────────────────────────────────────────┤
│  ML Model Server                                            │
│  └── TensorFlow Serving / FastAPI + Model                   │
├─────────────────────────────────────────────────────────────┤
│  Database                                                    │
│  └── PostgreSQL (Supabase/Railway) + TimescaleDB            │
├─────────────────────────────────────────────────────────────┤
│  Scheduler (Cron Jobs)                                      │
│  └── Data fetching setiap jam trading                       │
└─────────────────────────────────────────────────────────────┘
```

### Cost Estimate (Monthly)

| Service | Provider | Est. Cost |
|---------|----------|-----------|
| Frontend | Vercel Free | $0 |
| Backend API | Railway Hobby | $5 |
| Database | Supabase Free | $0 |
| ML Server | GCP Cloud Run | ~$10-20 |
| **Total** | | **~$15-25/bulan** |

---

## 📱 Output yang Akan Dihasilkan

### 1. Prediction Dashboard
- Real-time stock prices
- Prediction charts (1h, 4h, 1d, 3d)
- Signal indicators (BUY/SELL/HOLD)
- Confidence scores

### 2. Trading Recommendations
```json
{
  "stock_code": "BBCA",
  "current_price": 9500,
  "predictions": {
    "1h": {"price": 9520, "trend": "UP", "confidence": 0.72},
    "4h": {"price": 9580, "trend": "UP", "confidence": 0.68},
    "1d": {"price": 9650, "trend": "UP", "confidence": 0.71},
    "3d": {"price": 9800, "trend": "UP", "confidence": 0.65}
  },
  "signal": "BUY",
  "recommendation": {
    "action": "BUY",
    "lots": 10,
    "entry_price": 9500,
    "stop_loss": 9310,
    "take_profit": 9880,
    "risk_reward_ratio": 2.0
  }
}
```

### 3. Alert System
- Push notification saat signal muncul
- Email daily summary
- Portfolio tracking

---

## ⚠️ DISCLAIMER PENTING

```
╔═══════════════════════════════════════════════════════════════════╗
║                         ⚠️ PERINGATAN ⚠️                          ║
╠═══════════════════════════════════════════════════════════════════╣
║  Sistem ini BUKAN financial advice dan TIDAK menjamin profit.     ║
║                                                                   ║
║  • Pasar saham sangat volatile dan tidak dapat diprediksi 100%    ║
║  • Gunakan sistem ini sebagai ALAT BANTU analisis saja            ║
║  • Selalu lakukan riset mandiri sebelum trading                   ║
║  • Jangan investasikan uang yang tidak siap Anda rugi             ║
║  • Past performance does not guarantee future results             ║
║                                                                   ║
║  Pengembang tidak bertanggung jawab atas kerugian trading.        ║
╚═══════════════════════════════════════════════════════════════════╝
```

---

## 🔜 Next Steps

1. **[CURRENT]** ✅ Template data sudah dibuat
2. **[NEXT]** Upload/collect historical data untuk 10 saham target
3. **[NEXT]** Build preprocessing & feature engineering pipeline
4. **[NEXT]** Train LSTM model
5. **[NEXT]** Build FastAPI backend
6. **[NEXT]** Build Next.js dashboard
7. **[NEXT]** Deploy ke cloud

---

## 📞 Support

Jika ada pertanyaan atau butuh bantuan, silakan tanyakan!

Created for Jo - December 2025
