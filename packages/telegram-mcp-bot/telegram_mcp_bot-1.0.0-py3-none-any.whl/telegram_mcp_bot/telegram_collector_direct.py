#!/usr/bin/env python3
"""
Telegram агент-коллектор с прямым обращением к ChromaDB
Использует MCP только для браузера, ChromaDB - напрямую
"""

import asyncio
import logging
import os
import re
import uuid
import chromadb
from datetime import datetime
from urllib.parse import urlparse

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

from .agent_runner_browser_only import setup_agent

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

class TelegramCollectorDirect:
    """Класс для группового агента-коллектора"""
    
    def __init__(self):
        self.agent_runner = None
        self.chroma_client = None
        self.chroma_collection = None
        self.group_chat_id = GROUP_CHAT_ID
        
    async def initialize(self):
        """Инициализация агента"""
        logger.info("🚀 Инициализация Direct Telegram Collector...")
        
        # Инициализируем ChromaDB напрямую
        try:
            self.chroma_client = chromadb.PersistentClient(path='./chroma')
            self.chroma_collection = self.chroma_client.get_collection("telegram_group_messages")
            logger.info("✅ ChromaDB подключен напрямую!")
            logger.info(f"📄 Документов в коллекции: {self.chroma_collection.count()}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к ChromaDB: {e}")
            raise
        
        # Инициализируем MCP агента (только для браузера)
        self.agent_context = setup_agent()
        self.agent_runner = await self.agent_context.__aenter__()
        logger.info("✅ MCP агент инициализирован (только браузер)!")
        
    async def cleanup(self):
        """Очистка ресурсов"""
        if hasattr(self, 'agent_context') and self.agent_context:
            await self.agent_context.__aexit__(None, None, None)
            
    def extract_urls(self, text: str) -> list[str]:
        """Извлекает URL из текста сообщения"""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)

    def is_valid_url(self, url: str) -> bool:
        """Проверяет, является ли URL валидным"""
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc])
        except:
            return False

    def save_to_chromadb(self, text: str, metadata: dict) -> str:
        """Сохраняет данные в ChromaDB напрямую"""
        try:
            doc_id = str(uuid.uuid4())
            
            logger.info(f"💾 Сохраняем в ChromaDB:")
            logger.info(f"   Текст: {text[:100]}...")
            logger.info(f"   Метаданные: {metadata}")
            
            self.chroma_collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"✅ Сохранено в ChromaDB с ID: {doc_id}")
            return f"Успешно сохранено в ChromaDB (ID: {doc_id})"
            
        except Exception as e:
            error_msg = f"Ошибка сохранения в ChromaDB: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def process_link_with_browser(self, url: str, metadata: dict) -> str:
        """Обрабатывает ссылку через MCP браузер и сохраняет в ChromaDB напрямую"""
        try:
            thread_id = str(uuid.uuid4())
            
            # Используем MCP только для браузера
            prompt = f"""Обработай эту ссылку:

URL: {url}

Задача:
- Перейди по ссылке
- Получи содержимое страницы
- Верни мне текст содержимого

НЕ сохраняй в ChromaDB - я сделаю это сам!"""

            logger.info(f"🌐 Обрабатываем ссылку через MCP браузер: {url}")
            
            # Получаем содержимое через MCP браузер
            content = await self.agent_runner(prompt, thread_id=thread_id)
            
            logger.info(f"📄 Получен контент: {content[:200]}...")
            
            # Сохраняем в ChromaDB напрямую
            save_result = self.save_to_chromadb(content, metadata)
            
            return f"Ссылка обработана через MCP браузер и сохранена: {save_result}"
            
        except Exception as e:
            error_msg = f"Ошибка обработки ссылки {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def process_text_direct(self, text: str, metadata: dict) -> str:
        """Обрабатывает текст с прямым сохранением в ChromaDB"""
        try:
            logger.info(f"📝 Обрабатываем текстовое сообщение")
            
            # Сохраняем напрямую в ChromaDB
            save_result = self.save_to_chromadb(text, metadata)
            
            return f"Текст сохранен: {save_result}"
            
        except Exception as e:
            error_msg = f"Ошибка обработки текста: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def handle_message(self, message: types.Message):
        """Обрабатывает сообщения из группового чата"""
        
        # Проверяем, что сообщение из нужной группы
        if str(message.chat.id) != str(self.group_chat_id):
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
                "source": "telegram_direct",
                "chat_id": str(message.chat.id),
                "chat_title": message.chat.title or "Unknown",
                "user_id": str(message.from_user.id),
                "username": message.from_user.username or "unknown",
                "message_id": str(message.message_id),
                "timestamp": datetime.now().isoformat(),
            }
            
            # Извлекаем ссылки из сообщения
            urls = self.extract_urls(message.text)
            
            if urls:
                logger.info(f"🔗 Найдено ссылок: {len(urls)}")
                
                # Обрабатываем каждую ссылку
                for i, url in enumerate(urls):
                    if not self.is_valid_url(url):
                        continue
                        
                    logger.info(f"🌐 Обрабатываем ссылку {i+1}: {url}")
                    
                    # Метаданные для ссылки
                    link_metadata = {
                        **base_metadata,
                        "message_type": "url",
                        "original_url": url,
                        "original_message": message.text
                    }
                    
                    # Обрабатываем через MCP браузер + прямое сохранение
                    result = await self.process_link_with_browser(url, link_metadata)
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
                
                # Обрабатываем с прямым сохранением
                result = await self.process_text_direct(message.text, text_metadata)
                logger.info(f"✅ Текст обработан: {result[:100]}...")
                
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения: {e}")

    async def handle_status_command(self, message: types.Message):
        """Команда для проверки статуса агента"""
        try:
            count = self.chroma_collection.count()
            await message.reply(
                f"🤖 Direct Telegram Collector активен!\n"
                f"📊 Мониторю группу: {message.chat.title}\n"
                f"🆔 Chat ID: {message.chat.id}\n"
                f"🔧 MCP браузер: {'✅ Готов' if self.agent_runner else '❌ Не готов'}\n"
                f"💾 ChromaDB: ✅ Прямое подключение\n"
                f"📄 Документов в базе: {count}"
            )
        except Exception as e:
            await message.reply(f"❌ Ошибка статуса: {e}")

    async def handle_stats_command(self, message: types.Message):
        """Команда для получения статистики ChromaDB"""
        try:
            count = self.chroma_collection.count()
            
            # Получаем последние документы
            results = self.chroma_collection.get(limit=5, include=['metadatas'])
            
            stats_text = f"📊 Статистика ChromaDB:\n"
            stats_text += f"📄 Всего документов: {count}\n\n"
            
            if results['metadatas']:
                stats_text += "🔍 Последние документы:\n"
                for i, meta in enumerate(results['metadatas'][:3], 1):
                    source = meta.get('source', 'unknown')
                    msg_type = meta.get('message_type', 'unknown')
                    timestamp = meta.get('timestamp', 'unknown')
                    stats_text += f"{i}. {source} ({msg_type}) - {timestamp[:16]}\n"
            
            await message.reply(stats_text)
        except Exception as e:
            await message.reply(f"❌ Ошибка получения статистики: {e}")

# Оригинальные глобальные переменные для обратной совместимости
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Глобальные переменные
agent_runner = None
chroma_client = None
chroma_collection = None

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

def save_to_chromadb(text: str, metadata: dict) -> str:
    """Сохраняет данные в ChromaDB напрямую"""
    try:
        doc_id = str(uuid.uuid4())
        
        logger.info(f"💾 Сохраняем в ChromaDB:")
        logger.info(f"   Текст: {text[:100]}...")
        logger.info(f"   Метаданные: {metadata}")
        
        chroma_collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[doc_id]
        )
        
        logger.info(f"✅ Сохранено в ChromaDB с ID: {doc_id}")
        return f"Успешно сохранено в ChromaDB (ID: {doc_id})"
        
    except Exception as e:
        error_msg = f"Ошибка сохранения в ChromaDB: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def process_link_with_browser(url: str, metadata: dict) -> str:
    """Обрабатывает ссылку через MCP браузер и сохраняет в ChromaDB напрямую"""
    try:
        thread_id = str(uuid.uuid4())
        
        # Используем MCP только для браузера
        prompt = f"""Обработай эту ссылку:

URL: {url}

Задача:
- Перейди по ссылке
- Получи содержимое страницы
- Верни мне текст содержимого

НЕ сохраняй в ChromaDB - я сделаю это сам!"""

        logger.info(f"🌐 Обрабатываем ссылку через MCP браузер: {url}")
        
        # Получаем содержимое через MCP браузер
        content = await agent_runner(prompt, thread_id=thread_id)
        
        logger.info(f"📄 Получен контент: {content[:200]}...")
        
        # Сохраняем в ChromaDB напрямую
        save_result = save_to_chromadb(content, metadata)
        
        return f"Ссылка обработана через MCP браузер и сохранена: {save_result}"
        
    except Exception as e:
        error_msg = f"Ошибка обработки ссылки {url}: {str(e)}"
        logger.error(error_msg)
        return error_msg

async def process_text_direct(text: str, metadata: dict) -> str:
    """Обрабатывает текст с прямым сохранением в ChromaDB"""
    try:
        logger.info(f"📝 Обрабатываем текстовое сообщение")
        
        # Сохраняем напрямую в ChromaDB
        save_result = save_to_chromadb(text, metadata)
        
        return f"Текст сохранен: {save_result}"
        
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
            "source": "telegram_direct",
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
                
                # Обрабатываем через MCP браузер + прямое сохранение
                result = await process_link_with_browser(url, link_metadata)
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
            
            # Обрабатываем с прямым сохранением
            result = await process_text_direct(message.text, text_metadata)
            logger.info(f"✅ Текст обработан: {result[:100]}...")
            
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения: {e}")

@dp.message(Command("status"))
async def status_command(message: types.Message):
    """Команда для проверки статуса агента"""
    if message.chat.type in ['group', 'supergroup']:
        try:
            count = chroma_collection.count()
            await message.reply(
                f"🤖 Direct Telegram Collector активен!\n"
                f"📊 Мониторю группу: {message.chat.title}\n"
                f"🆔 Chat ID: {message.chat.id}\n"
                f"🔧 MCP браузер: {'✅ Готов' if agent_runner else '❌ Не готов'}\n"
                f"💾 ChromaDB: ✅ Прямое подключение\n"
                f"📄 Документов в базе: {count}"
            )
        except Exception as e:
            await message.reply(f"❌ Ошибка статуса: {e}")

@dp.message(Command("stats"))
async def stats_command(message: types.Message):
    """Команда для получения статистики ChromaDB"""
    if message.chat.type in ['group', 'supergroup']:
        try:
            count = chroma_collection.count()
            
            # Получаем последние документы
            results = chroma_collection.get(limit=5, include=['metadatas'])
            
            stats_text = f"📊 Статистика ChromaDB:\n"
            stats_text += f"📄 Всего документов: {count}\n\n"
            
            if results['metadatas']:
                stats_text += "🔍 Последние документы:\n"
                for i, meta in enumerate(results['metadatas'][:3], 1):
                    source = meta.get('source', 'unknown')
                    msg_type = meta.get('message_type', 'unknown')
                    timestamp = meta.get('timestamp', 'unknown')
                    stats_text += f"{i}. {source} ({msg_type}) - {timestamp[:16]}\n"
            
            await message.reply(stats_text)
        except Exception as e:
            await message.reply(f"❌ Ошибка получения статистики: {e}")

async def main():
    """Запуск Telegram агента с прямым ChromaDB"""
    global agent_runner, chroma_client, chroma_collection
    
    logger.info("🚀 Запуск Direct Telegram Collector...")
    logger.info("🔧 MCP для браузера + прямое обращение к ChromaDB")
    
    # Инициализируем ChromaDB напрямую
    try:
        chroma_client = chromadb.PersistentClient(path='./chroma')
        chroma_collection = chroma_client.get_collection("telegram_group_messages")
        logger.info("✅ ChromaDB подключен напрямую!")
        logger.info(f"📄 Документов в коллекции: {chroma_collection.count()}")
    except Exception as e:
        logger.error(f"❌ Ошибка подключения к ChromaDB: {e}")
        return
    
    if GROUP_CHAT_ID:
        logger.info(f"🎯 Мониторинг группы с ID: {GROUP_CHAT_ID}")
    
    # Инициализируем MCP агента (только для браузера)
    async with setup_agent() as agent:
        agent_runner = agent
        logger.info("✅ MCP агент инициализирован (только браузер)!")
        logger.info("🔍 Доступные команды: /status, /stats")
        logger.info("🤖 Direct Collector готов к работе!")
        
        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            logger.info("\n👋 Direct Collector остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 