import os
import time
import logging
from datetime import datetime
import ccxt
import pandas as pd
import ta
import requests
from dotenv import load_dotenv

load_dotenv()

# ── Konfigürasyon ──────────────────────────────────────────────
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID   = os.getenv("TELEGRAM_CHAT_ID")

COINS = os.getenv("COINS", "BTC/USDT,ETH/USDT,SOL/USDT").split(",")
TIMEFRAME  = "15m"
CHECK_EVERY = 60 * 15   # 15 dakikada bir kontrol

# RSI eşikleri
RSI_OVERBOUGHT = 70    # SHORT sinyali
RSI_OVERSOLD   = 30    # LONG sinyali (opsiyonel)

# MACD parametreleri
MACD_FAST   = 12
MACD_SLOW   = 26
MACD_SIGNAL = 9

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger(__name__)

exchange = ccxt.binance({"enableRateLimit": True})

# ── Telegram ───────────────────────────────────────────────────
def send_telegram(message: str) -> None:
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, json=payload, timeout=10)
        r.raise_for_status()
        log.info("Telegram mesajı gönderildi.")
    except Exception as e:
        log.error(f"Telegram hatası: {e}")


def build_message(symbol: str, signal: str, price: float,
                  rsi: float, macd: float, macd_sig: float) -> str:
    emoji   = "🔴 SHORT SİNYALİ" if signal == "SHORT" else "🟢 LONG SİNYALİ"
    slug    = symbol.replace("/", "")
    tv_link = f"https://www.tradingview.com/chart/?symbol=BINANCE:{slug}"

    direction = (
        "MACD aşağı kesti + RSI aşırı alım bölgesinde"
        if signal == "SHORT"
        else "MACD yukarı kesti + RSI aşırı satım bölgesinde"
    )

    return (
        f"<b>{emoji}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🪙 <b>Coin:</b> {symbol}\n"
        f"💰 <b>Fiyat:</b> ${price:,.4f}\n"
        f"📊 <b>RSI (14):</b> {rsi:.2f}\n"
        f"📈 <b>MACD:</b> {macd:.4f}\n"
        f"📉 <b>Sinyal:</b> {macd_sig:.4f}\n"
        f"⏱ <b>Zaman Dilimi:</b> 15 dakika\n"
        f"📋 <b>Koşul:</b> {direction}\n"
        f"🕐 <b>Zaman:</b> {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🔗 <a href='{tv_link}'>TradingView'da Aç</a>"
    )


# ── Veri & İndikatörler ────────────────────────────────────────
def fetch_ohlcv(symbol: str, limit: int = 100) -> pd.DataFrame:
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=TIMEFRAME, limit=limit)
    df = pd.DataFrame(ohlcv, columns=["timestamp", "open", "high", "low", "close", "volume"])
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
    return df


def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df["rsi"] = ta.momentum.RSIIndicator(df["close"], window=14).rsi()
    macd = ta.trend.MACD(df["close"], window_fast=MACD_FAST, window_slow=MACD_SLOW, window_sign=MACD_SIGNAL)
    df["macd"]        = macd.macd()
    df["macd_signal"] = macd.macd_signal()
    return df.dropna()


def check_signal(df: pd.DataFrame) -> str | None:
    """
    SHORT: MACD çizgisi sinyal çizgisini aşağı kesiyor VE RSI > 70
    LONG:  MACD çizgisi sinyal çizgisini yukarı kesiyor VE RSI < 30
    """
    prev = df.iloc[-2]
    curr = df.iloc[-1]

    macd_cross_down = (prev["macd"] > prev["macd_signal"]) and (curr["macd"] < curr["macd_signal"])
    macd_cross_up   = (prev["macd"] < prev["macd_signal"]) and (curr["macd"] > curr["macd_signal"])

    if macd_cross_down and curr["rsi"] > RSI_OVERBOUGHT:
        return "SHORT"
    if macd_cross_up and curr["rsi"] < RSI_OVERSOLD:
        return "LONG"
    return None


# ── Ana döngü ──────────────────────────────────────────────────
def run() -> None:
    log.info(f"Bot başladı. Takip edilen coinler: {COINS}")
    send_telegram(
        "🤖 <b>Kripto Sinyal Botu Başladı</b>\n"
        f"Coinler: {', '.join(COINS)}\n"
        f"Zaman dilimi: {TIMEFRAME} | RSI eşiği: {RSI_OVERBOUGHT}"
    )

    while True:
        for symbol in COINS:
            symbol = symbol.strip()
            try:
                df     = fetch_ohlcv(symbol)
                df     = calculate_indicators(df)
                signal = check_signal(df)

                last   = df.iloc[-1]
                log.info(
                    f"{symbol} | Fiyat: {last['close']:.4f} | "
                    f"RSI: {last['rsi']:.2f} | MACD: {last['macd']:.4f}"
                )

                if signal:
                    msg = build_message(
                        symbol=symbol,
                        signal=signal,
                        price=float(last["close"]),
                        rsi=float(last["rsi"]),
                        macd=float(last["macd"]),
                        macd_sig=float(last["macd_signal"]),
                    )
                    send_telegram(msg)
                    log.info(f"SİNYAL: {symbol} → {signal}")

            except Exception as e:
                log.error(f"{symbol} hatası: {e}")

        log.info(f"Sonraki kontrol {CHECK_EVERY // 60} dakika sonra...")
        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    run()
