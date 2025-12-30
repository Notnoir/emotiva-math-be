# 🤖 LLM SETUP GUIDE - Google Gemini

EMOTIVA-MATH sekarang mendukung **LLM (Large Language Model)** untuk generate penjelasan yang lebih natural dan personalized!

## 🚀 Cara Setup LLM

### 1️⃣ Dapatkan Google Gemini API Key (GRATIS!)

1. Buka: https://makersuite.google.com/app/apikey
2. Login dengan Google Account
3. Klik **"Create API Key"**
4. Copy API key yang didapat

### 2️⃣ Setup Environment Variable

Edit file `.env` di folder `be-emotiva-math`:

```env
# Google Gemini API Configuration
GEMINI_API_KEY=AIzaSy...your_actual_key_here
USE_LLM=True
```

### 3️⃣ Restart Backend Server

```bash
# Stop server (CTRL+C)
# Start lagi
python run.py
```

Jika berhasil, akan muncul:
```
✅ LLM (Google Gemini) initialized successfully
```

---

## 🎯 Cara Kerja Hybrid AI

Sistem menggunakan **Hybrid Approach**:

```
┌─────────────────────────────────────┐
│  User Request (topic + profile)     │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Rule-Based AI Engine                │
│  - Calculate difficulty              │
│  - Determine structure               │
│ -  Get formulas & examples          │
└──────────────┬──────────────────────┘
               │
               ▼
      ┌────────┴────────┐
      │  LLM Available? │
      └────────┬────────┘
          Yes  │  No
     ┌─────────┴─────────┐
     │                    │
     ▼                    ▼
┌─────────┐         ┌──────────┐
│ Gemini  │         │ Template │
│ AI      │         │ Based    │
└─────────┘         └──────────┘
     │                    │
     └────────┬───────────┘
              ▼
     ┌──────────────────┐
     │ Adaptive Content │
     └──────────────────┘
```

### Keuntungan Hybrid:

- ✅ **LLM aktif** → Penjelasan natural, variatif, engaging
- ❌ **LLM tidak ada** → Fallback ke template (tetap berfungsi!)
- 🎯 **Rule-based** tetap kontrol logic (difficulty, structure)
- 🤖 **LLM** hanya untuk content generation

---

## 📊 Perbedaan Rule-Based vs LLM

### Rule-Based (Template):
```
🟦 KUBUS - Penjelasan Visual

Bayangkan sebuah dadu! Itulah bentuk kubus.

📐 Karakteristik:
• Memiliki 6 sisi berbentuk persegi yang sama
• Semua rusuk memiliki panjang yang sama (s)
...
```

### LLM-Powered (Dynamic):
```
Halo! 😊 Senang bisa membantu kamu belajar tentang kubus!

Oke, bayangin kamu lagi pegang dadu... nah itulah yang 
namanya kubus! Sekarang coba lihat baik-baik:

🎯 Yang Perlu Kamu Tahu:
Kubus itu bangun ruang yang unik karena semua sisinya 
persis sama - bentuknya persegi dan ukurannya sama besar.
...
```

**Perbedaan:**
- LLM lebih conversational & friendly
- Adaptif ke emotion (*tone* berubah)
- Penjelasan lebih engaging
- Variasi setiap request

---

## 🧪 Testing LLM

```bash
# Test dengan emotion berbeda
curl -X POST http://localhost:5000/api/adaptive/content \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": 1,
    "topic": "kubus",
    "emosi": "cemas"
  }'
```

Coba bandingkan dengan:
```json
{ "emosi": "percaya_diri" }
```

Tone & kompleksitas akan berbeda!

---

## 💰 Biaya

**Google Gemini API: GRATIS!**

- Free tier: 60 requests/minute
- Cukup untuk demo & development
- Tidak perlu kartu kredit

---

## ⚙️ Troubleshooting

### "LLM disabled - using rule-based content"

**Penyebab:**
- `USE_LLM=False` di `.env`
- `GEMINI_API_KEY` tidak diset
- API key salah

**Solusi:**
1. Cek file `.env` ada dan benar
2. Pastikan `USE_LLM=True`
3. Pastikan API key valid
4. Restart server

### Error: "API key not valid"

**Solusi:**
1. Generate API key baru
2. Pastikan tidak ada spaces di awal/akhir
3. Format: `GEMINI_API_KEY=AIzaSy...` (tanpa quotes)

---

## 🎓 Best Practice

1. **Development**: Gunakan LLM untuk varietas
2. **Production**: Pertimbangkan rate limiting
3. **Fallback**: Selalu ada template backup
4. **Testing**: Test both modes (LLM on/off)

---

## 📝 File yang Penting

```
be-emotiva-math/
├── .env                    # Tempat API key
├── app/
│   ├── llm_service.py     # LLM logic
│   ├── ai_engine.py       # Hybrid engine
│   └── routes.py          # API endpoints
```

---

**✨ EMOTIVA-MATH sekarang powered by Google Gemini AI!**

Untuk pertanyaan atau issues, refer ke documentation atau contact developer.
