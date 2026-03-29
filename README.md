# 🤖 Kripto Sinyal Botu

Binance'den 15 dakikalık OHLCV verisi çekip **MACD crossover + RSI** koşuluna göre Telegram'a SHORT/LONG sinyali gönderen Python botu.

---

## 📋 Özellikler

- **MACD** (12/26/9) aşağı/yukarı kesişim tespiti
- **RSI** (14) filtresi — SHORT için RSI > 70, LONG için RSI < 30
- Birden fazla coin takibi (virgülle ayrılmış liste)
- Telegram'a detaylı mesaj: fiyat, RSI değeri, MACD değeri, TradingView linki
- Railway'de sürekli çalışır, 15 dakikada bir kontrol eder

---

## 🚀 Kurulum

### 1. Telegram Botu Oluştur

1. Telegram'da **@BotFather**'a yaz → `/newbot` → isim ver → **token** al
2. **@userinfobot**'a bir mesaj at → **chat_id** al

### 2. Repoyu Klonla

```bash
git clone https://github.com/KULLANICI_ADIN/crypto-signal-bot.git
cd crypto-signal-bot
```

### 3. `.env` Dosyasını Oluştur

```bash
cp .env.example .env
```

`.env` içini doldur:

```
TELEGRAM_BOT_TOKEN=1234567890:ABCdef...
TELEGRAM_CHAT_ID=123456789
COINS=BTC/USDT,ETH/USDT,SOL/USDT
```

### 4. Lokal Test

```bash
pip install -r requirements.txt
python bot.py
```

---

## ☁️ Railway'e Deploy

1. [railway.app](https://railway.app) → GitHub ile giriş
2. **New Project → Deploy from GitHub repo** → bu repoyu seç
3. **Variables** sekmesine `.env` değerlerini tek tek ekle:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
   - `COINS`
4. Deploy tamamlanınca bot otomatik başlar

---

## 📊 Sinyal Koşulları

| Sinyal | MACD Koşulu | RSI Koşulu |
|--------|-------------|------------|
| 🔴 SHORT | MACD çizgisi sinyal çizgisini **aşağı** kesiyor | RSI **> 70** |
| 🟢 LONG  | MACD çizgisi sinyal çizgisini **yukarı** kesiyor | RSI **< 30** |

---

## 📱 Telegram Mesaj Örneği

```
🔴 SHORT SİNYALİ
━━━━━━━━━━━━━━━━━━
🪙 Coin: BTC/USDT
💰 Fiyat: $67,420.0000
📊 RSI (14): 73.45
📈 MACD: -12.3400
📉 Sinyal: -8.2100
⏱ Zaman Dilimi: 15 dakika
📋 Koşul: MACD aşağı kesti + RSI aşırı alım bölgesinde
🕐 Zaman: 2025-03-29 14:30 UTC
━━━━━━━━━━━━━━━━━━
🔗 TradingView'da Aç
```

---

## ⚙️ Parametreleri Değiştirme

`bot.py` içinde:

```python
RSI_OVERBOUGHT = 70   # SHORT eşiği
RSI_OVERSOLD   = 30   # LONG eşiği
MACD_FAST      = 12
MACD_SLOW      = 26
MACD_SIGNAL    = 9
CHECK_EVERY    = 60 * 15  # Kontrol sıklığı (saniye)
```

---

## ⚠️ Uyarı

Bu bot yalnızca **bilgilendirme amaçlıdır**. Finansal tavsiye değildir. Kripto para işlemleri yüksek risk içerir.
