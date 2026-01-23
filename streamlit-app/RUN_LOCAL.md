# 🏃 Cara Menjalankan Aplikasi Lokal

## Quick Start (3 Langkah)

### 1️⃣ Install Dependencies

```bash
cd streamlit-app
pip install streamlit pandas plotly
```

Atau gunakan requirements.txt:

```bash
pip install -r requirements.txt
```

### 2️⃣ Jalankan Aplikasi

```bash
streamlit run streamlit_app.py
```

### 3️⃣ Buka di Browser

Aplikasi akan otomatis terbuka di browser pada:
```
http://localhost:8501
```

Jika tidak otomatis buka, copy-paste URL tersebut ke browser.

---

## 🎯 Yang Akan Anda Lihat

### Home Page (Dashboard)
- Platform statistics
- Top performers leaderboard
- Platform metrics
- Recent activity

### Navigation Sidebar
Gunakan sidebar di kiri untuk navigasi ke:
- 👥 Talent Management
- 📺 Livestreams
- 📈 Analytics

---

## 🧪 Testing

### Test Fitur di Talent Management:
1. Filter by status (All/Live/Online/Offline)
2. Search talents by name
3. Switch between Table View & Card View
4. Edit talent (click Edit button)
5. Change talent status

### Test Fitur di Livestreams:
1. View active livestreams
2. Filter by category
3. Sort by viewers/likes/diamonds
4. Create new livestream (jika tidak ada)
5. End livestream

### Test Fitur di Analytics:
1. View growth charts
2. Check revenue trends
3. Compare top performers
4. View pie charts & radar charts
5. Select talents to compare

---

## ⚙️ Configuration

### Port
Default port: 8501

Untuk menggunakan port lain:
```bash
streamlit run streamlit_app.py --server.port 8502
```

### Theme
Edit `.streamlit/config.toml` untuk customize theme

---

## 🐛 Troubleshooting

### ModuleNotFoundError
```bash
pip install streamlit pandas plotly
```

### Port Already in Use
```bash
# Gunakan port lain
streamlit run streamlit_app.py --server.port 8502
```

### Data Not Showing
- Refresh browser (Ctrl+R atau Cmd+R)
- Check console untuk errors
- Restart aplikasi

---

## 📊 Sample Data

Aplikasi dilengkapi dengan 8 sample talents:
- 2 talents sedang LIVE
- 3 talents ONLINE
- 3 talents OFFLINE

Data akan reset setiap kali refresh page (session state).

---

## 🔄 Development Mode

Streamlit auto-reload saat file berubah:

1. Edit file Python
2. Save
3. Streamlit detect changes
4. Click "Rerun" di browser (atau auto-rerun jika enabled)

---

## 💡 Tips

- **Sidebar:** Buka/tutup dengan arrow di kiri atas
- **Theme:** Toggle light/dark di settings (⋮)
- **Fullscreen:** Click expand icon di pojok charts
- **Download:** Export data di Analytics page

---

Selamat mencoba! 🎉
