-- =========================================
-- EMOTIVA-MATH Database Schema
-- MySQL/MariaDB Database Setup
-- =========================================

-- Create database (using backticks for special characters)
CREATE DATABASE IF NOT EXISTS `emotiva_math` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `emotiva_math`;

-- =========================================
-- Table: users
-- Menyimpan profil pembelajaran user
-- =========================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100) NOT NULL,
    gaya_belajar ENUM('visual', 'auditori', 'kinestetik') NOT NULL,
    level ENUM('pemula', 'menengah', 'mahir') DEFAULT 'pemula',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_gaya_belajar (gaya_belajar),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: emotions
-- Menyimpan log emosi user
-- =========================================
CREATE TABLE IF NOT EXISTS emotions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    emosi ENUM('cemas', 'bingung', 'netral', 'percaya_diri') NOT NULL,
    context VARCHAR(200),
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_emosi (emosi),
    INDEX idx_waktu (waktu)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: learning_logs
-- Menyimpan aktivitas pembelajaran user
-- =========================================
CREATE TABLE IF NOT EXISTS learning_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    materi VARCHAR(100) NOT NULL,
    tipe_aktivitas ENUM('belajar', 'latihan', 'quiz') DEFAULT 'belajar',
    skor INT DEFAULT 0,
    durasi INT DEFAULT 0 COMMENT 'Durasi dalam detik',
    waktu TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_materi (materi),
    INDEX idx_tipe_aktivitas (tipe_aktivitas),
    INDEX idx_waktu (waktu)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: teacher_materials
-- CRITICAL: Sumber SATU-SATUNYA pengetahuan sistem
-- Materi pembelajaran HANYA dari guru
-- =========================================
CREATE TABLE IF NOT EXISTS teacher_materials (
    id INT AUTO_INCREMENT PRIMARY KEY,
    judul VARCHAR(200) NOT NULL,
    topik ENUM('kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma') NOT NULL,
    konten TEXT NOT NULL COMMENT 'Materi lengkap dari guru',
    level ENUM('pemula', 'menengah', 'mahir') DEFAULT 'pemula',
    created_by VARCHAR(100) DEFAULT 'Admin' COMMENT 'Nama guru/pembuat',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_topik (topik),
    INDEX idx_level (level),
    FULLTEXT INDEX idx_konten (konten, judul) COMMENT 'For text search'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: quiz_questions
-- Menyimpan soal-soal latihan/quiz yang di-generate
-- =========================================
CREATE TABLE IF NOT EXISTS quiz_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    topik ENUM('kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma') NOT NULL,
    level ENUM('pemula', 'menengah', 'mahir') NOT NULL,
    pertanyaan TEXT NOT NULL COMMENT 'Soal/pertanyaan',
    pilihan_a VARCHAR(500),
    pilihan_b VARCHAR(500),
    pilihan_c VARCHAR(500),
    pilihan_d VARCHAR(500),
    jawaban_benar ENUM('A', 'B', 'C', 'D') NOT NULL,
    penjelasan TEXT COMMENT 'Penjelasan jawaban',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_topik (topik),
    INDEX idx_level (level)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: quiz_attempts
-- Menyimpan percobaan quiz user
-- =========================================
CREATE TABLE IF NOT EXISTS quiz_attempts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    topik ENUM('kubus', 'balok', 'bola', 'tabung', 'kerucut', 'limas', 'prisma') NOT NULL,
    level ENUM('pemula', 'menengah', 'mahir') NOT NULL,
    total_soal INT NOT NULL,
    benar INT DEFAULT 0,
    salah INT DEFAULT 0,
    skor DECIMAL(5,2) NOT NULL COMMENT 'Persentase 0-100',
    durasi INT DEFAULT 0 COMMENT 'Durasi dalam detik',
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_topik (topik),
    INDEX idx_skor (skor),
    INDEX idx_completed_at (completed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Table: quiz_answers
-- Menyimpan jawaban user per soal
-- =========================================
CREATE TABLE IF NOT EXISTS quiz_answers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    attempt_id INT NOT NULL,
    question_id INT NOT NULL,
    jawaban_user ENUM('A', 'B', 'C', 'D') NOT NULL,
    is_correct BOOLEAN NOT NULL,
    waktu_jawab TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attempt_id) REFERENCES quiz_attempts(id) ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES quiz_questions(id) ON DELETE CASCADE,
    INDEX idx_attempt_id (attempt_id),
    INDEX idx_question_id (question_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- =========================================
-- Sample Data (Optional)
-- =========================================

-- Insert sample user
INSERT INTO users (nama, gaya_belajar, level) VALUES
('Demo User', 'visual', 'pemula');

-- Get the last inserted user ID
SET @user_id = LAST_INSERT_ID();

-- Insert sample emotions
INSERT INTO emotions (user_id, emosi, context) VALUES
(@user_id, 'percaya_diri', 'Memulai pembelajaran Kubus'),
(@user_id, 'bingung', 'Mengerjakan soal volume Balok');

-- Insert sample learning logs
INSERT INTO learning_logs (user_id, materi, tipe_aktivitas, skor, durasi) VALUES
(@user_id, 'Kubus - Pengenalan', 'belajar', 0, 300),
(@user_id, 'Quiz Kubus Dasar', 'quiz', 80, 120);

-- =========================================
-- Sample Teacher Materials (CRITICAL DATA)
-- =========================================

INSERT INTO teacher_materials (judul, topik, konten, level, created_by) VALUES
(
    'Pengenalan Kubus - Dasar',
    'kubus',
    'KUBUS adalah bangun ruang tiga dimensi yang dibatasi oleh 6 buah sisi berbentuk persegi yang kongruen (sama dan sebangun).

CIRI-CIRI KUBUS:
1. Memiliki 6 sisi berbentuk persegi yang sama besar
2. Memiliki 12 rusuk yang sama panjang
3. Memiliki 8 titik sudut
4. Semua sudutnya siku-siku (90 derajat)
5. Memiliki 12 diagonal bidang yang sama panjang
6. Memiliki 4 diagonal ruang yang sama panjang

RUMUS KUBUS (rusuk = s):
- Volume = s × s × s = s³
- Luas Permukaan = 6 × s²
- Panjang diagonal bidang = s√2
- Panjang diagonal ruang = s√3

CONTOH SOAL:
Sebuah kubus memiliki panjang rusuk 5 cm. Hitunglah:
a) Volume kubus
b) Luas permukaan kubus

JAWABAN:
a) Volume = s³ = 5³ = 125 cm³
b) Luas Permukaan = 6 × s² = 6 × 5² = 6 × 25 = 150 cm²',
    'pemula',
    'Pak Budi'
),
(
    'Volume dan Luas Permukaan Kubus',
    'kubus',
    'MEMAHAMI VOLUME KUBUS

Volume adalah ukuran ruang tiga dimensi yang ditempati oleh suatu benda. Untuk kubus, kita menghitung berapa banyak kubus satuan yang bisa masuk ke dalamnya.

Bayangkan kubus dengan rusuk 3 cm. Kita bisa membagi kubus ini menjadi kubus-kubus kecil berukuran 1 cm × 1 cm × 1 cm.
- Panjang: 3 kubus
- Lebar: 3 kubus  
- Tinggi: 3 kubus
- Total: 3 × 3 × 3 = 27 kubus kecil

Jadi Volume = rusuk × rusuk × rusuk = s³

MEMAHAMI LUAS PERMUKAAN KUBUS

Luas permukaan adalah total luas semua sisi yang membentuk kubus. Kubus memiliki 6 sisi yang sama besar.

Jika satu sisi memiliki luas s × s = s², maka:
Luas Permukaan = 6 × s²

LATIHAN:
1. Kubus A: rusuk 4 cm → Volume = 4³ = 64 cm³, Luas = 6×4² = 96 cm²
2. Kubus B: rusuk 10 cm → Volume = 10³ = 1000 cm³, Luas = 6×10² = 600 cm²',
    'pemula',
    'Pak Budi'
),
(
    'Pengenalan Balok',
    'balok',
    'BALOK adalah bangun ruang tiga dimensi yang dibatasi oleh 6 buah sisi berbentuk persegi panjang.

PERBEDAAN KUBUS DAN BALOK:
- Kubus: semua sisi sama besar (persegi)
- Balok: sisi-sisi berpasangan (persegi panjang)

CIRI-CIRI BALOK:
1. Memiliki 6 sisi berbentuk persegi panjang
2. Sisi-sisi yang berhadapan sama besar dan sejajar
3. Memiliki 12 rusuk (4 panjang, 4 lebar, 4 tinggi)
4. Memiliki 8 titik sudut
5. Semua sudutnya siku-siku (90 derajat)

RUMUS BALOK (p=panjang, l=lebar, t=tinggi):
- Volume = p × l × t
- Luas Permukaan = 2(pl + pt + lt)

CONTOH BENDA BERBENTUK BALOK:
- Kotak pensil
- Kulkas
- Buku
- Kardus

CONTOH SOAL:
Sebuah balok memiliki panjang 8 cm, lebar 5 cm, dan tinggi 4 cm.
a) Volume = p × l × t = 8 × 5 × 4 = 160 cm³
b) Luas Permukaan = 2(pl + pt + lt) = 2(40 + 32 + 20) = 2(92) = 184 cm²',
    'pemula',
    'Pak Budi'
);

-- =========================================
-- Verify Installation
-- =========================================

-- Show all tables
SHOW TABLES;

-- Count records
SELECT 'users' as table_name, COUNT(*) as record_count FROM users
UNION ALL
SELECT 'emotions', COUNT(*) FROM emotions
UNION ALL
SELECT 'learning_logs', COUNT(*) FROM learning_logs;

-- =========================================
-- Useful Queries
-- =========================================

-- Get user with stats
SELECT 
    u.id,
    u.nama,
    u.gaya_belajar,
    u.level,
    COUNT(DISTINCT e.id) as total_emotions,
    COUNT(DISTINCT l.id) as total_activities,
    u.created_at
FROM users u
LEFT JOIN emotions e ON u.id = e.user_id
LEFT JOIN learning_logs l ON u.id = l.user_id
GROUP BY u.id;

-- Get emotion distribution
SELECT emosi, COUNT(*) as count
FROM emotions
GROUP BY emosi
ORDER BY count DESC;

-- Get learning activity stats
SELECT 
    tipe_aktivitas,
    COUNT(*) as total_activities,
    AVG(skor) as avg_score,
    SUM(durasi) as total_duration_seconds
FROM learning_logs
GROUP BY tipe_aktivitas;
