# 🚀 Panduan Upload ke GitHub

## Cara 1: Via GitHub Web (Termudah)

### Step 1: Buat Repository Baru
1. Buka https://github.com
2. Login ke akun GitHub kamu
3. Klik tombol **"+"** di pojok kanan atas → **"New repository"**
4. Isi informasi repository:
   - **Repository name**: `stock-prediction-indonesia` (atau nama lain)
   - **Description**: `Indonesian Stock Prediction System using LSTM Machine Learning`
   - **Public** atau **Private** (sesuai keinginan)
   - ✅ Centang **"Add a README file"** → JANGAN dicentang (kita sudah punya)
   - Klik **"Create repository"**

### Step 2: Upload Files
1. Di halaman repository yang baru dibuat, klik **"uploading an existing file"**
2. Drag & drop semua file dari folder `stock-prediction-system`
3. Atau klik **"choose your files"** dan pilih semua file
4. Isi commit message: `Initial commit - Stock prediction system`
5. Klik **"Commit changes"**

---

## Cara 2: Via Git Command Line (Recommended)

### Step 1: Install Git (jika belum)
```bash
# Windows (download dari)
https://git-scm.com/download/win

# Mac
brew install git

# Linux (Ubuntu/Debian)
sudo apt install git
```

### Step 2: Setup Git Config
```bash
git config --global user.name "Nama Kamu"
git config --global user.email "email@kamu.com"
```

### Step 3: Buat Repository di GitHub
1. Buka https://github.com/new
2. Buat repository baru dengan nama `stock-prediction-indonesia`
3. **JANGAN** centang apapun (biarkan kosong)
4. Klik **"Create repository"**

### Step 4: Upload via Terminal
```bash
# Masuk ke folder project
cd stock-prediction-system

# Initialize git
git init

# Add semua files
git add .

# Commit
git commit -m "Initial commit - Stock prediction system"

# Rename branch ke main
git branch -M main

# Tambahkan remote (GANTI dengan URL repository kamu)
git remote add origin https://github.com/USERNAME/stock-prediction-indonesia.git

# Push ke GitHub
git push -u origin main
```

### Step 5: Autentikasi
Jika diminta login:
- **Username**: username GitHub kamu
- **Password**: Personal Access Token (bukan password biasa!)

#### Cara Buat Personal Access Token:
1. Buka https://github.com/settings/tokens
2. Klik **"Generate new token (classic)"**
3. Beri nama: `git-cli`
4. Centang: `repo` (full control)
5. Klik **"Generate token"**
6. **COPY token** (hanya tampil sekali!)
7. Gunakan token ini sebagai password saat `git push`

---

## Cara 3: Via GitHub Desktop (Visual/GUI)

### Step 1: Download GitHub Desktop
Download dari: https://desktop.github.com

### Step 2: Login ke GitHub
1. Buka GitHub Desktop
2. Klik **File** → **Options** → **Accounts**
3. Sign in ke GitHub

### Step 3: Add Local Repository
1. Klik **File** → **Add local repository**
2. Pilih folder `stock-prediction-system`
3. Jika belum jadi git repo, klik **"create a repository"**

### Step 4: Publish ke GitHub
1. Klik **"Publish repository"**
2. Isi nama dan description
3. Pilih Public/Private
4. Klik **"Publish repository"**

---

## 📁 Struktur Folder yang Akan Di-upload

```
stock-prediction-indonesia/
├── .gitignore              # File yang diabaikan git
├── LICENSE                 # MIT License
├── README.md               # Dokumentasi utama
├── requirements.txt        # Python dependencies
├── create_templates.py     # Script generator template
├── data/
│   ├── .gitkeep
│   ├── template_hourly.csv # Template data per jam
│   └── template_daily.csv  # Template data harian
├── utils/
│   └── data_fetcher.py     # Script fetch data
├── models/
│   └── .gitkeep            # Placeholder untuk ML models
├── api/
│   └── .gitkeep            # Placeholder untuk API
└── dashboard/
    └── .gitkeep            # Placeholder untuk dashboard
```

---

## ⚠️ Catatan Penting

1. **File Excel (.xlsx)** tidak di-upload karena:
   - Ukuran besar
   - Berisi sample data yang bisa di-generate ulang
   - Jalankan `python create_templates.py` untuk generate

2. **Data sensitif** jangan di-upload:
   - API keys
   - Password
   - Data trading pribadi

3. **Model files** (.h5, .pkl) juga diabaikan karena besar
   - Upload ke Google Drive/Dropbox jika perlu share

---

## ✅ Checklist Sebelum Upload

- [ ] Sudah buat repository di GitHub
- [ ] Sudah setup git config (nama & email)
- [ ] Sudah punya Personal Access Token (jika pakai CLI)
- [ ] Tidak ada data sensitif di folder project
- [ ] File .gitignore sudah benar

---

## 🆘 Troubleshooting

### Error: "Permission denied"
```bash
# Reset remote URL dengan token
git remote set-url origin https://TOKEN@github.com/USERNAME/REPO.git
```

### Error: "Repository not found"
- Pastikan URL repository benar
- Pastikan sudah login dengan akun yang benar

### Error: "Failed to push some refs"
```bash
# Pull dulu sebelum push
git pull origin main --rebase
git push origin main
```

---

Butuh bantuan lebih lanjut? Tanyakan saja! 🙌
