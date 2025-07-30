#!/usr/bin/env python3
"""
Запуск персонального RAG-помощника
"""

import asyncio
import sys
from pathlib import Path

# Добавляем путь к пакету
sys.path.insert(0, str(Path(__file__).parent))

from telegram_mcp_bot.personal_assistant import main

if __name__ == "__main__":
    print("🤖 Запуск Personal RAG Assistant...")
    asyncio.run(main()) 