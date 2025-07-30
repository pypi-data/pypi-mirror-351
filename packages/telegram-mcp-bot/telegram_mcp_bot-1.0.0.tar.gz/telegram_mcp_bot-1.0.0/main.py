#!/usr/bin/env python3
"""
Главный файл для запуска Telegram MCP Bot
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к пакету
sys.path.insert(0, str(Path(__file__).parent))

from telegram_mcp_bot.telegram_collector_direct import main

if __name__ == "__main__":
    print("🚀 Запуск Telegram MCP Bot...")
    asyncio.run(main())
