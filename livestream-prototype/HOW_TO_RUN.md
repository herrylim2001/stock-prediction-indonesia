# 🚀 Cara Menjalankan Prototype - Panduan Lengkap

## Method 1: Cara Paling Mudah (Recommended)

### Step 1: Install Dependencies

```bash
cd /home/user/stock-prediction-indonesia/livestream-prototype/backend
pip install Flask Flask-CORS Flask-SocketIO python-socketio eventlet
```

### Step 2: Jalankan Backend Server

Buka terminal pertama:

```bash
cd /home/user/stock-prediction-indonesia/livestream-prototype/backend
python app.py
```

Server akan menampilkan:
```
Server running on http://localhost:5000
```

**JANGAN TUTUP TERMINAL INI** - biarkan server tetap berjalan

### Step 3: Jalankan HTTP Server untuk Frontend

Buka terminal kedua (terminal baru):

```bash
cd /home/user/stock-prediction-indonesia/livestream-prototype
python -m http.server 8080
```

Atau gunakan Python 3:
```bash
python3 -m http.server 8080
```

Server akan menampilkan:
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

### Step 4: Buka di Browser

Sekarang buka browser Anda dan akses:

**🎛️ Backoffice Dashboard (Admin Panel):**
```
http://localhost:8080/backoffice/index.html
```

**📱 Client Viewer (User App):**
```
http://localhost:8080/client/index.html
```

**📖 Quick Start Guide:**
```
http://localhost:8080/QUICK_START_GUIDE.html
```

---

## Method 2: Tanpa HTTP Server (Buka File Langsung)

Jika Anda tidak ingin menjalankan HTTP server, bisa buka file HTML langsung:

### Step 1: Jalankan Backend Server

```bash
cd /home/user/stock-prediction-indonesia/livestream-prototype/backend
python app.py
```

### Step 2: Buka File HTML di Browser

**Cara 1 - Menggunakan File Explorer:**
1. Buka file explorer
2. Navigate ke folder `livestream-prototype`
3. Double-click file:
   - `backoffice/index.html` untuk Backoffice
   - `client/index.html` untuk Client Viewer

**Cara 2 - Dari Terminal:**

```bash
# Mac
open backoffice/index.html
open client/index.html

# Linux
xdg-open backoffice/index.html
xdg-open client/index.html

# Windows
start backoffice/index.html
start client/index.html
```

---

## Method 3: Menggunakan Auto-Start Script

### Linux/Mac:

```bash
cd /home/user/stock-prediction-indonesia/livestream-prototype
chmod +x START_SERVER.sh
./START_SERVER.sh
```

Kemudian buka:
- `backoffice/index.html`
- `client/index.html`

### Windows:

Double-click file: `START_SERVER.bat`

Kemudian buka:
- `backoffice/index.html`
- `client/index.html`

---

## 🎬 Testing Prototype

### Test 1: Backoffice Dashboard

1. Buka: `http://localhost:8080/backoffice/index.html`
2. Lihat Dashboard - harusnya muncul statistics (5 talents, 2 livestreams)
3. Click "Talent Management" di sidebar
4. Lihat table dengan 5 talents
5. Click "Active Livestreams" - harusnya ada 2 livestreams aktif

### Test 2: Client Viewer

1. Buka: `http://localhost:8080/client/index.html`
2. Harusnya muncul 2 livestream cards (Mike Gaming & David Fitness)
3. Click salah satu card untuk join livestream
4. Test fitur:
   - Ketik pesan di chat box dan send
   - Click tombol ❤️ (Like) - harusnya muncul floating hearts
   - Click tombol 🎁 (Gift) - pilih gift dan send

### Test 3: Real-time Sync

1. Buka Backoffice di satu tab/window
2. Buka Client di tab/window lain
3. Di Client: join livestream dan send likes/gifts
4. Di Backoffice: lihat statistics update real-time!

---

## ⚠️ Troubleshooting

### Problem: "Cannot connect to server"

**Solusi:**
- Pastikan backend server sudah berjalan di `http://localhost:5000`
- Check terminal - harusnya ada log "Server running on..."
- Test dengan curl: `curl http://localhost:5000/`

### Problem: "Module not found" atau import error

**Solusi:**
```bash
pip install Flask Flask-CORS Flask-SocketIO python-socketio eventlet
```

Atau dengan requirements.txt:
```bash
cd backend
pip install -r requirements.txt
```

### Problem: Page tidak muncul / blank

**Solusi:**
- Pastikan HTTP server sudah berjalan
- Check URL - pastikan menggunakan `http://localhost:8080/...`
- Buka browser console (F12) - lihat error messages

### Problem: CORS error

**Solusi:**
- Gunakan HTTP server (Method 1) bukan buka file langsung
- Pastikan backend sudah enable CORS (sudah terinstall Flask-CORS)

---

## 📞 URL Summary

Setelah semua server berjalan:

| Component | URL |
|-----------|-----|
| Backend API | http://localhost:5000 |
| API Docs | http://localhost:5000/api/talents |
| Backoffice | http://localhost:8080/backoffice/index.html |
| Client Viewer | http://localhost:8080/client/index.html |
| Quick Guide | http://localhost:8080/QUICK_START_GUIDE.html |

---

## 🎯 Demo Checklist

- [ ] Backend server running on port 5000
- [ ] HTTP server running on port 8080 (optional)
- [ ] Backoffice dashboard can be accessed
- [ ] Client viewer can be accessed
- [ ] Can see 2 active livestreams
- [ ] Can join livestream and see video placeholder
- [ ] Can send chat messages
- [ ] Can send likes (see floating hearts)
- [ ] Can send gifts
- [ ] Real-time sync works between backoffice and client

---

Selamat mencoba! 🎉
