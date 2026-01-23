# 🎥 LiveStream Prototype - Broadcasting Platform

Prototype aplikasi live streaming dengan model broadcasting seperti Bigo Live dan Hot51. Sistem ini terdiri dari 2 komponen utama: **Backoffice Panel** untuk manajemen talent dan **Client Viewer** untuk penonton.

## 📋 Deskripsi Project

Project ini adalah **mockup/prototype** yang dibuat untuk presentasi kepada client. Sistem mendemonstrasikan:

- ✅ Live streaming broadcasting platform
- ✅ Talent management system
- ✅ Real-time viewer interaction
- ✅ Performance monitoring dashboard
- ✅ Gift/Diamond system
- ✅ Live chat functionality

## 🏗️ Arsitektur Sistem

```
livestream-prototype/
├── backend/              # Backend API (Flask + Socket.IO)
│   ├── app.py           # Main application & API endpoints
│   ├── database.py      # In-memory database & data management
│   └── requirements.txt # Python dependencies
│
├── backoffice/          # Dashboard untuk Admin/Management
│   ├── index.html       # Main dashboard page
│   ├── css/style.css    # Styling
│   └── js/app.js        # Frontend logic
│
└── client/              # Viewer Application
    ├── index.html       # Main viewer page
    ├── css/style.css    # Styling
    └── js/app.js        # Frontend logic
```

## 🎯 Fitur Utama

### 1️⃣ **Backend API**

- **RESTful API** untuk manajemen data
- **WebSocket (Socket.IO)** untuk real-time updates
- **Talent Management** (CRUD operations)
- **Livestream Control** (start, end, monitoring)
- **Real-time Statistics** (viewers, diamonds, likes)

**API Endpoints:**

```
GET  /api/talents              - Get semua talent
GET  /api/talents/:id          - Get talent by ID
PUT  /api/talents/:id          - Update talent
PUT  /api/talents/:id/status   - Update talent status

GET  /api/livestreams          - Get active livestreams
GET  /api/livestreams/:id      - Get livestream by ID
POST /api/livestreams          - Create livestream
POST /api/livestreams/:id/end  - End livestream
POST /api/livestreams/:id/like - Add like
POST /api/livestreams/:id/gift - Send gift

GET  /api/stats                - Get platform statistics
```

### 2️⃣ **Backoffice Dashboard**

Panel admin untuk controlling dan monitoring sistem:

**Fitur:**
- 📊 Dashboard overview dengan real-time statistics
- 👥 Talent management (edit, update status)
- 📺 Active livestreams monitoring
- 📈 Performance analytics
- 🔄 Real-time updates via WebSocket

**Halaman:**
- **Dashboard** - Overview & quick stats
- **Talent Management** - Manage all talents
- **Active Livestreams** - Monitor live shows
- **Analytics** - Performance metrics

### 3️⃣ **Client Viewer**

Aplikasi untuk penonton (seperti Bigo/Hot51):

**Fitur:**
- 📺 Browse active livestreams
- ▶️ Watch live shows
- 💬 Live chat dengan talent & viewers lain
- ❤️ Like & reaction system
- 🎁 Send gifts (diamonds)
- 👥 Real-time viewer count
- 🔄 Auto-refresh livestream list

## 🚀 Cara Menjalankan

### Prerequisites

- Python 3.8+
- pip (Python package manager)
- Browser modern (Chrome, Firefox, Safari)

### Step 1: Install Dependencies

```bash
cd livestream-prototype/backend
pip install -r requirements.txt
```

### Step 2: Jalankan Backend Server

```bash
cd backend
python app.py
```

Server akan berjalan di: `http://localhost:5000`

### Step 3: Buka Backoffice Dashboard

Buka browser dan akses:
```
file:///path/to/livestream-prototype/backoffice/index.html
```

Atau jalankan dengan HTTP server sederhana:
```bash
cd backoffice
python -m http.server 8080
```

Lalu buka: `http://localhost:8080`

### Step 4: Buka Client Viewer

Buka browser dan akses:
```
file:///path/to/livestream-prototype/client/index.html
```

Atau jalankan dengan HTTP server:
```bash
cd client
python -m http.server 8081
```

Lalu buka: `http://localhost:8081`

## 📱 Cara Menggunakan

### **Backoffice Dashboard**

1. **Dashboard Overview**
   - Lihat total talents, active livestreams, viewers, dan diamonds
   - Monitor recent livestreams
   - Quick actions untuk refresh data

2. **Talent Management**
   - View semua talent dalam table
   - Edit talent (name, bio, status)
   - Change talent status (online/offline/live)
   - Search talents

3. **Active Livestreams**
   - Monitor semua livestream yang sedang aktif
   - Lihat real-time viewer count, likes, diamonds
   - Refresh data

### **Client Viewer**

1. **Browse Livestreams**
   - Lihat semua livestream yang sedang LIVE
   - Info: talent name, viewer count, likes, diamonds
   - Click card untuk masuk livestream

2. **Watch Livestream**
   - Join livestream room
   - Lihat viewer count real-time
   - Chat dengan viewers lain
   - Send likes (tap tombol ❤️)
   - Send gifts (pilih gift dari menu)
   - Follow talent

3. **Interact**
   - Type pesan di chat box
   - Press Enter atau click send
   - Tap Like button untuk reactions
   - Tap Gift untuk open gift menu

## 🎨 Demo Data

Sistem sudah dilengkapi dengan sample data:

**5 Talent:**
- Sarah Beauty (Online)
- Mike Gaming (Live)
- Lisa Music (Offline)
- David Fitness (Live)
- Anna Cook (Online)

**Active Livestreams:**
- Mike Gaming's Live Stream
- David Fitness's Live Stream

## 🔄 Real-time Features

Sistem menggunakan **Socket.IO** untuk real-time communication:

**Events:**
- `livestream_started` - Livestream baru dimulai
- `livestream_ended` - Livestream berakhir
- `viewer_joined` - Viewer join
- `viewer_left` - Viewer leave
- `new_comment` - Chat message baru
- `like_animation` - Like dikirim
- `gift_received` - Gift diterima
- `talent_updated` - Talent data updated
- `talent_status_changed` - Status talent berubah

## 🎁 Gift System

**Available Gifts:**
- 💐 Rose - 1 diamond
- ⭐ Star - 5 diamonds
- 👑 Crown - 10 diamonds
- 🚀 Rocket - 50 diamonds
- 🏆 Trophy - 100 diamonds
- 💎 Diamond - 500 diamonds

## 📊 Statistics Tracking

**Platform Stats:**
- Total Talents
- Active Livestreams
- Total Viewers (concurrent)
- Total Diamonds Earned

**Talent Stats:**
- Followers
- Total Viewers (all-time)
- Total Diamonds Earned
- Level

**Livestream Stats:**
- Current Viewers
- Likes
- Diamonds (from gifts)
- Duration

## 🔧 Teknologi yang Digunakan

**Backend:**
- Python 3.8+
- Flask (Web Framework)
- Flask-SocketIO (WebSocket)
- Flask-CORS (Cross-Origin Resource Sharing)
- Eventlet (Async support)

**Frontend:**
- HTML5
- CSS3 (with animations)
- Vanilla JavaScript (ES6+)
- Socket.IO Client
- Font Awesome Icons

## 🎯 Use Case untuk Client Integration

Prototype ini mendemonstrasikan bagaimana sistem bisa diintegrasikan ke platform client:

### **Skenario 1: Mobile App Integration**
Client bisa menggunakan API endpoints untuk:
- Fetch livestreams
- Send comments, likes, gifts
- Get real-time updates via WebSocket

### **Skenario 2: Web Platform Integration**
Client bisa embed viewer component:
- Responsive design
- Real-time chat
- Gift system
- Viewer analytics

### **Skenario 3: Backoffice Integration**
Admin panel bisa diintegrasikan untuk:
- Talent management
- Content moderation
- Performance monitoring
- Revenue tracking

## 📝 Catatan Penting

⚠️ **Ini adalah PROTOTYPE/MOCKUP:**

1. **Database In-Memory** - Data akan hilang saat server restart
2. **Video Streaming** - Menggunakan placeholder animation (bukan real video stream)
3. **Authentication** - Belum ada system login/auth
4. **Payment** - Gift system belum terintegrasi dengan payment gateway
5. **Scalability** - Belum dioptimasi untuk production

## 🚀 Next Steps untuk Production

Untuk implementasi production, perlu ditambahkan:

1. **Real Database** (PostgreSQL/MongoDB)
2. **Video Streaming Infrastructure** (WebRTC/HLS/RTMP)
3. **Authentication & Authorization** (JWT/OAuth)
4. **Payment Gateway Integration**
5. **CDN untuk Video Delivery**
6. **Load Balancing & Scaling**
7. **Content Moderation System**
8. **Analytics & Reporting**
9. **Mobile App (iOS/Android)**
10. **Security Enhancements**

## 📞 Support

Untuk pertanyaan atau diskusi lebih lanjut tentang prototype ini, silakan hubungi tim development.

---

**© 2025 LiveStream Prototype - Demo Version**
