# CoinRadar — Telegram бот цен BTC/ETH/TON (USD + RUB)

## Локальный запуск
1. Создай `.env` рядом с `main.py`:
   ```
   BOT_TOKEN=ВАШ_ТОКЕН_БОТА
   ```
2. Python 3.10+
3. Установи зависимости и запусти:
   ```bash
   python -m venv venv
   # Windows: .\venv\Scripts\Activate.ps1
   # Linux/Mac: source venv/bin/activate
   pip install -r requirements.txt
   python main.py
   ```

## Деплой на Render (Free)
- Репозиторий должен содержать: `main.py`, `requirements.txt`, `Procfile`.
- В Render создайте **Background Worker**:
  - Start Command: `python main.py` (или оставьте Procfile: `worker: python main.py`)
  - Environment Variables: `BOT_TOKEN=...`
  - Plan: Free
