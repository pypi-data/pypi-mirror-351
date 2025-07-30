#!/usr/bin/env python3
"""
Естественный Telegram агент-коллектор с MCP
Полагается на автоматический выбор инструментов
"""

import asyncio
import logging
import os
import re
import uuid
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from agent_runner import setup_agent

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GROUP_CHAT_ID = os.getenv("GROUP_CHAT_ID", "-4864366522")

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен в .env")

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Глобальная переменная для агента
agent_runner = None

def extract_urls(text: str) -> list[str]:
    """Извлекает URL из текста сообщения"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    return re.findall(url_pattern, text)

def is_valid_url(url: str) -> bool:
    """Проверяет, является ли URL валидным"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

async def process_link_naturally(url: str, metadata: dict) -> str:
    """Обрабатывает ссылку естественным способом через MCP"""
    try:
        thread_id = str(uuid.uuid4())
        
        # Естественный промпт без указания конкретных инструментов
        prompt = f"""Мне нужно обработать ссылку из Telegram группы и сохранить её содержимое.

Ссылка: {url}

Задача:
- Перейди по этой ссылке и получи её содержимое
- Сохрани полученное содержимое в ChromaDB в коллекцию "telegram_group_messages"
- Используй эти метаданные при сохранении: {metadata}

Выбери подходящие инструменты для выполнения этой задачи и выполни её."""

        result = await agent_runner(prompt, thread_id=thread_id)
        return result
        
    except Exception as e:
        error_msg = f"Ошибка обработки ссылки {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def process_text_naturally(text: str, metadata: dict) -> str:
    """Обрабатывает текст естественным способом через MCP"""
    try:
        thread_id = str(uuid.uuid4())
        
        # Естественный промпт для текста
        prompt = f"""Мне нужно сохранить текстовое сообщение из Telegram группы.

Текст сообщения: "{text}"

Задача:
- Сохрани этот текст в ChromaDB в коллекцию "telegram_group_messages"
- Используй эти метаданные: {metadata}

Выбери подходящий инструмент для сохранения и выполни задачу."""

        result = await agent_runner(prompt, thread_id=thread_id)
        return result
        
    except Exception as e:
        error_msg = f"Ошибка обработки текста: {str(e)}"
        logger.error(error_msg)
        return error_msg

@dp.message()
async def handle_group_message(message: types.Message):
    """Обрабатывает сообщения из группового чата"""
    
    # Проверяем, что сообщение из нужной группы
    if str(message.chat.id) != str(GROUP_CHAT_ID):
        return
    
    # Проверяем, что это групповой чат
    if message.chat.type not in ['group', 'supergroup']:
        return
    
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return
    
    # Игнорируем пустые сообщения и команды
    if not message.text or message.text.startswith('/'):
        return
    
    logger.info(f"📨 Новое сообщение от @{message.from_user.username}: {message.text[:100]}...")
    
    try:
        # Подготавливаем базовые метаданные
        base_metadata = {
            "source": "telegram_group",
            "chat_id": str(message.chat.id),
            "chat_title": message.chat.title or "Unknown",
            "user_id": str(message.from_user.id),
            "username": message.from_user.username or "unknown",
            "message_id": str(message.message_id),
            "timestamp": datetime.now().isoformat(),
        }
        
        # Извлекаем ссылки из сообщения
        urls = extract_urls(message.text)
        
        if urls:
            logger.info(f"🔗 Найдено ссылок: {len(urls)}")
            
            # Обрабатываем каждую ссылку
            for i, url in enumerate(urls):
                if not is_valid_url(url):
                    continue
                    
                logger.info(f"🌐 Обрабатываем ссылку {i+1}: {url}")
                
                # Метаданные для ссылки
                link_metadata = {
                    **base_metadata,
                    "message_type": "url",
                    "original_url": url,
                    "original_message": message.text
                }
                
                # Обрабатываем естественным способом
                result = await process_link_naturally(url, link_metadata)
                logger.info(f"✅ Ссылка обработана: {result[:100]}...")
                
                # Пауза между ссылками
                if i < len(urls) - 1:
                    await asyncio.sleep(2)
        else:
            logger.info("📝 Обрабатываем как текстовое сообщение")
            
            # Метаданные для текста
            text_metadata = {
                **base_metadata,
                "message_type": "text"
            }
            
            # Обрабатываем естественным способом
            result = await process_text_naturally(message.text, text_metadata)
            logger.info(f"✅ Текст обработан: {result[:100]}...")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")

@dp.message(Command("status"))
async def status_command(message: types.Message):
    """Команда для проверки статуса агента"""
    if message.chat.type in ['group', 'supergroup']:
        await message.reply(
            f"🤖 Natural MCP Collector активен!\n"
            f"📊 Мониторю группу: {message.chat.title}\n"
            f"🆔 Chat ID: {message.chat.id}\n"
            f"🧠 Использую MCP с автоматическим выбором инструментов\n"
            f"🔧 Доступны инструменты браузера и ChromaDB"
        )

@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    """Команда для получения статистики ChromaDB"""
    if message.chat.type in ['group', 'supergroup']:
        try:
            thread_id = str(uuid.uuid4())
            
            # Естественный запрос статистики
            prompt = """Мне нужна статистика ChromaDB.

Задача:
- Получи список всех коллекций в ChromaDB
- Для каждой коллекции покажи количество документов
- Представь информацию в удобном формате

Используй подходящие инструменты для получения этой информации."""

            response = await agent_runner(prompt, thread_id=thread_id)
            await message.reply(f"📊 Статистика ChromaDB:\n{response[:1000]}...")
        except Exception as e:
            await message.reply(f"❌ Ошибка получения статистики: {e}")

async def main():
    """Запуск естественного MCP Telegram агента-коллектора"""
    global agent_runner
    
    logger.info("🚀 Запуск Natural MCP Telegram Collector...")
    logger.info("🧠 Агент будет автоматически выбирать подходящие MCP инструменты")
    
    if GROUP_CHAT_ID:
        logger.info(f"🎯 Мониторинг группы с ID: {GROUP_CHAT_ID}")
    else:
        logger.info("⚠️ GROUP_CHAT_ID не указан - будут обрабатываться все группы")
    
    # Инициализируем MCP агента
    async with setup_agent() as agent:
        agent_runner = agent
        logger.info("✅ MCP агент инициализирован!")
        logger.info("🔍 Доступные команды: /status, /stats")
        logger.info("🤖 Natural MCP Collector готов к работе!")
        logger.info("📝 Отправьте сообщения в группу для тестирования")
        logger.info("🛑 Нажмите Ctrl+C для остановки")
        
        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            logger.info("\n👋 Natural MCP Collector остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 