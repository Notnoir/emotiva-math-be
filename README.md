# 🧠 EMOTIVA-MATH Backend API

**Emotion-Aware Adaptive Mathematics Learning System - Backend Service**

Topik Matematika: **Bangun Ruang (3D Shapes)**

---

## 📋 Technology Stack

- **Framework**: Flask 3.0.0
- **CORS**: Flask-CORS 4.0.0
- **Database**: MySQL 8.0+ (dengan PyMySQL driver)
- **ORM**: SQLAlchemy 3.1.1
- **Python**: 3.8+

---

## 🚀 Cara Menjalankan Backend

### Prerequisites

1. **Python 3.8+** sudah terinstall
2. **MySQL Server** sudah running
3. **MySQL Client** (optional, untuk testing manual)

### Setup Instructions

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 2. Setup MySQL Database

**Opsi A: Otomatis (Recommended)**

```bash
# Copy .env.example ke .env
copy .env.example .env

# Edit .env dan sesuaikan MySQL credentials
# MYSQL_USER=root
# MYSQL_PASSWORD=your_password
# MYSQL_DATABASE=emotiva_math

# Jalankan setup script
python setup_database.py
```

**Opsi B: Manual**

```bash
# Login ke MySQL
mysql -u root -p

# Jalankan schema.sql
source database/schema.sql

# Atau
mysql -u root -p emotiva_math < database/schema.sql
```

#### 3. Configure Environment Variables

Edit file `.env`:

```env
# MySQL Configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=emotiva_math
```

#### 4. Jalankan Server

```bash
python run.py
```

Server akan berjalan di: **http://localhost:5000**

---

## 🔌 API Endpoints

### Base URL: `http://localhost:5000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Root endpoint - API info |
| GET | `/api/health` | Health check endpoint |
| GET | `/api/info` | System information |
| GET | `/api/profile` | Get all user profiles |
| POST | `/api/profile` | Create new profile |
| GET | `/api/profile/<id>` | Get specific profile |
| PUT | `/api/profile/<id>` | Update profile |
| POST | `/api/emotion` | Log emotion |
| GET | `/api/emotion/<user_id>` | Get emotion history |
| GET | `/api/learning-logs/<user_id>` | Get learning logs |
| POST | `/api/learning-logs/<user_id>` | Create learning log |

---

## 📝 Testing Endpoints

### 1. Health Check
```bash
curl http://localhost:5000/api/health
```

### 2. Create User Profile
```bash
curl -X POST http://localhost:5000/api/profile \
  -H "Content-Type: application/json" \
  -d "{\"nama\": \"Andi\", \"gaya_belajar\": \"visual\"}"
```

### 3. Log Emotion
```bash
curl -X POST http://localhost:5000/api/emotion \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": 1, \"emosi\": \"percaya_diri\", \"context\": \"Belajar Kubus\"}"
```

### 4. Run Test Script
```bash
python test_api.py
```

---

## 🗄️ Database Schema

### Tables

**users**
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `nama` (VARCHAR(100), NOT NULL)
- `gaya_belajar` (ENUM: visual, auditori, kinestetik)
- `level` (ENUM: pemula, menengah, mahir)
- `created_at`, `updated_at` (TIMESTAMP)

**emotions**
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (INT, FOREIGN KEY → users.id)
- `emosi` (ENUM: cemas, bingung, netral, percaya_diri)
- `context` (VARCHAR(200))
- `waktu` (TIMESTAMP)

**learning_logs**
- `id` (INT, PRIMARY KEY, AUTO_INCREMENT)
- `user_id` (INT, FOREIGN KEY → users.id)
- `materi` (VARCHAR(100))
- `tipe_aktivitas` (ENUM: belajar, latihan, quiz)
- `skor`, `durasi` (INT)
- `waktu` (TIMESTAMP)

---

## 📁 Struktur Project

```
be-emotiva-math/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Konfigurasi (MySQL)
│   ├── routes.py            # API endpoints
│   └── models.py            # Database models
├── database/
│   └── schema.sql           # MySQL schema
├── .env.example             # Environment template
├── .env                     # Environment variables (gitignored)
├── requirements.txt         # Python dependencies
├── setup_database.py        # Database setup script
├── test_api.py             # API testing script
├── run.py                  # Entry point
└── README.md               # Dokumentasi ini
```

---

## 🔄 Development Roadmap

- [x] **Tahap 1**: Flask setup + CORS + Health check ✅
- [x] **Tahap 2**: MySQL Database + Learning Profile API ✅
- [x] **Tahap 3**: Frontend React + Vite + Tailwind ✅
- [ ] **Tahap 4**: Kuesioner Gaya Belajar (Enhanced)
- [ ] **Tahap 5**: Emotion-Aware Module (Enhanced)
- [ ] **Tahap 6**: Adaptive Learning Engine (AI Core)
- [ ] **Tahap 7**: AR/3D Visualization
- [ ] **Tahap 8**: Latihan & Evaluasi
- [ ] **Tahap 9**: Analytics & Logging
- [ ] **Tahap 10**: Finalisasi & Demo

---

## 🐛 Troubleshooting

### Error: Can't connect to MySQL server

```bash
# Cek MySQL service running
# Windows:
net start MySQL80

# Linux/Mac:
sudo systemctl start mysql
```

### Error: Access denied for user

```bash
# Reset MySQL password atau update .env dengan credentials yang benar
MYSQL_USER=root
MYSQL_PASSWORD=your_correct_password
```

### Error: Database doesn't exist

```bash
# Jalankan setup script
python setup_database.py
```

### Port 5000 sudah digunakan

Edit `run.py` dan ubah port:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

---

## 📊 Useful MySQL Commands

```sql
-- Login ke MySQL
mysql -u root -p

-- Pilih database
USE emotiva_math;

-- Lihat semua tabel
SHOW TABLES;

-- Lihat struktur tabel
DESCRIBE users;

-- Lihat semua users
SELECT * FROM users;

-- Delete semua data tapi keep structure
TRUNCATE TABLE emotions;
TRUNCATE TABLE learning_logs;
TRUNCATE TABLE users;

-- Drop database (hati-hati!)
DROP DATABASE emotiva_math;
```

---

## 👨‍💻 Developer

Tugas Besar Kecerdasan Buatan  
Institut Teknologi Nasional Bandung

**Status**: Phase 1-3 Complete ✅ (MySQL Edition)
