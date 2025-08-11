import asyncio
import os
from typing import Dict, List

import httpx
from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from dotenv import load_dotenv

# Load token from env (Render: set BOT_TOKEN in Environment Variables)
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    raise SystemExit("No BOT_TOKEN provided. Set it in .env (local) or in hosting env vars.")

bot = Bot(BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

ID_ALIASES = {
    "btc": ["bitcoin"],
    "eth": ["ethereum"],
    "ton": ["toncoin", "the-open-network"],
}
DEFAULT_COINS = ["btc", "eth", "ton"]
COINGECKO_URL = "https://api.coingecko.com/api/v3/simple/price"

def fmt_money(v: float) -> str:
    return f"{v:,.2f}"

async def fetch_prices(symbols: List[str]) -> Dict[str, Dict[str, float]]:
    ids: List[str] = []
    for s in symbols:
        ids += ID_ALIASES.get(s, [])
    ids = list(dict.fromkeys(ids))

    params = {"ids": ",".join(ids), "vs_currencies": "usd,rub"}
    headers = {"Accept": "application/json", "User-Agent": "coinradar-bot/1.0"}

    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(COINGECKO_URL, params=params, headers=headers)
        r.raise_for_status()
        data = r.json()

    out: Dict[str, Dict[str, float]] = {}
    for sym in symbols:
        for coin_id in ID_ALIASES.get(sym, []):
            if coin_id in data:
                out[sym] = data[coin_id]
                break
    return out

@dp.message(CommandStart())
async def on_start(m: Message):
    await m.answer(
        "Привет! Я покажу цены <b>BTC/ETH/TON</b> в <b>USD</b> и <b>RUB</b>\n"
        "Команды:\n"
        "• /price — текущие цены\n"
        "• /price btc eth — выбрать тикеры (btc, eth, ton)"
    )

@dp.message(Command("price"))
async def on_price(m: Message):
    parts = (m.text or "").split()
    syms = [p.lower() for p in parts[1:]] or DEFAULT_COINS

    norm: List[str] = []
    for s in syms:
        if s in ID_ALIASES and s not in norm:
            norm.append(s)

    if not norm:
        await m.reply("Укажи любые из: btc, eth, ton. Пример: <code>/price eth ton</code>")
        return

    try:
        prices = await fetch_prices(norm)
    except httpx.HTTPError as e:
        await m.reply(f"Не удалось получить цены: {e}")
        return

    if not prices:
        await m.reply("Похоже, цены недоступны. Попробуй позже.")
        return

    lines = []
    for s in norm:
        p = prices.get(s)
        if not p:
            lines.append(f"• {s.upper()}: нет данных")
            continue
        usd = fmt_money(p.get("usd", 0.0))
        rub = fmt_money(p.get("rub", 0.0))
        lines.append(f"• <b>{s.upper()}</b>: ${usd} | ₽{rub}")

    await m.reply("\n".join(lines))

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        pass
