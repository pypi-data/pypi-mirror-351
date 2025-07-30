#!/usr/bin/env python3
"""
Персональный RAG-помощник для Telegram
React-агент с памятью диалогов и умным использованием RAG
"""

import asyncio
import logging
import os
import uuid
import chromadb
from datetime import datetime
from typing import Dict, Any, Optional

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

from .agent_runner import setup_agent  # Используем полный MCP (с ChromaDB)

load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Конфигурация
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
MAX_CONTEXT_LENGTH = 10  # Максимум сообщений в контексте
SUMMARIZE_THRESHOLD = 20  # Когда начинать суммаризацию

if not TELEGRAM_TOKEN:
    raise ValueError("TELEGRAM_TOKEN не установлен в .env")

class PersonalAssistant:
    """Персональный помощник с памятью и RAG"""
    
    def __init__(self):
        self.agent_runner = None
        self.user_contexts: Dict[str, list] = {}  # Контексты по user_id
        self.agent_context = None
        # Добавляем прямое подключение к ChromaDB
        self.chroma_client = None
        self.chroma_collection = None
    
    async def initialize(self):
        """Инициализация агента"""
        logger.info("🚀 Инициализация Personal RAG Assistant...")
        
        # Инициализируем прямое подключение к ChromaDB
        try:
            self.chroma_client = chromadb.PersistentClient(path='./chroma')
            self.chroma_collection = self.chroma_client.get_collection("telegram_group_messages")
            logger.info("✅ ChromaDB подключен напрямую!")
            logger.info(f"📄 Документов в коллекции: {self.chroma_collection.count()}")
        except Exception as e:
            logger.error(f"❌ Ошибка подключения к ChromaDB: {e}")
            # Не прерываем инициализацию, просто логируем ошибку
        
        # Инициализируем MCP агента (с браузером)
        self.agent_context = setup_agent()
        self.agent_runner = await self.agent_context.__aenter__()
        logger.info("✅ MCP агент инициализирован (браузер + MCP ChromaDB)!")
        
    async def cleanup(self):
        """Очистка ресурсов"""
        if hasattr(self, 'agent_context') and self.agent_context:
            await self.agent_context.__aexit__(None, None, None)
    
    def search_knowledge_base(self, query: str, n_results: int = 3) -> str:
        """Прямой поиск в базе знаний"""
        try:
            if not self.chroma_collection:
                return "База знаний недоступна"
            
            results = self.chroma_collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas']
            )
            
            if not results['documents'][0]:
                return "По вашему запросу ничего не найдено в базе знаний"
            
            # Формируем ответ
            knowledge_text = "🔍 Найдено в базе знаний:\n\n"
            for i, (doc, meta) in enumerate(zip(results['documents'][0], results['metadatas'][0]), 1):
                source = meta.get('source', 'unknown')
                url = meta.get('original_url', '')
                msg_type = meta.get('message_type', 'unknown')
                
                knowledge_text += f"{i}. Источник: {source} ({msg_type})\n"
                if url:
                    knowledge_text += f"   URL: {url}\n"
                knowledge_text += f"   Содержимое: {doc[:300]}...\n\n"
            
            return knowledge_text
            
        except Exception as e:
            logger.error(f"❌ Ошибка поиска в базе знаний: {e}")
            return f"Ошибка поиска в базе знаний: {str(e)}"
    
    def get_user_context(self, user_id: str) -> list:
        """Получает контекст пользователя"""
        if user_id not in self.user_contexts:
            self.user_contexts[user_id] = []
        return self.user_contexts[user_id]
    
    def add_to_context(self, user_id: str, message: dict):
        """Добавляет сообщение в контекст пользователя"""
        context = self.get_user_context(user_id)
        context.append(message)
        
        # Если контекст слишком длинный, суммаризируем
        if len(context) > SUMMARIZE_THRESHOLD:
            asyncio.create_task(self.summarize_context(user_id))
    
    async def summarize_context(self, user_id: str):
        """Суммаризирует старую часть контекста"""
        try:
            context = self.get_user_context(user_id)
            if len(context) <= MAX_CONTEXT_LENGTH:
                return
            
            # Берем старые сообщения для суммаризации
            old_messages = context[:-MAX_CONTEXT_LENGTH]
            recent_messages = context[-MAX_CONTEXT_LENGTH:]
            
            # Формируем текст для суммаризации
            conversation_text = ""
            for msg in old_messages:
                role = "Пользователь" if msg["role"] == "user" else "Помощник"
                conversation_text += f"{role}: {msg['content']}\n"
            
            # Суммаризируем через агента
            summary_prompt = f"""Суммаризируй эту беседу кратко, сохранив ключевые темы и факты:

{conversation_text}

Создай краткое резюме в 2-3 предложениях."""

            thread_id = f"summary_{user_id}_{uuid.uuid4()}"
            summary = await self.agent_runner(summary_prompt, thread_id=thread_id)
            
            # Заменяем старые сообщения на суммарное
            summary_message = {
                "role": "system",
                "content": f"Краткое резюме предыдущей беседы: {summary}",
                "timestamp": datetime.now().isoformat(),
                "type": "summary"
            }
            
            self.user_contexts[user_id] = [summary_message] + recent_messages
            logger.info(f"📝 Суммаризирован контекст для пользователя {user_id}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка суммаризации для {user_id}: {e}")
    
    async def process_message(self, user_id: str, message_text: str) -> str:
        """Обрабатывает сообщение пользователя"""
        try:
            # Добавляем сообщение пользователя в контекст
            user_message = {
                "role": "user",
                "content": message_text,
                "timestamp": datetime.now().isoformat()
            }
            self.add_to_context(user_id, user_message)
            
            # Получаем контекст для формирования промпта
            context = self.get_user_context(user_id)
            
            # Формируем промпт с контекстом
            context_text = ""
            for msg in context[:-1]:  # Исключаем последнее сообщение (текущее)
                if msg["role"] == "user":
                    context_text += f"Пользователь: {msg['content']}\n"
                elif msg["role"] == "assistant":
                    context_text += f"Помощник: {msg['content']}\n"
                elif msg["role"] == "system":
                    context_text += f"Контекст: {msg['content']}\n"
            
            # Проверяем, нужен ли поиск в базе знаний
            search_keywords = ["github", "ссылк", "репозитор", "код", "проект", "база", "найди", "поиск"]
            needs_search = any(keyword in message_text.lower() for keyword in search_keywords)
            
            knowledge_context = ""
            if needs_search:
                logger.info(f"🔍 Выполняем поиск в базе знаний для запроса: {message_text}")
                knowledge_context = self.search_knowledge_base(message_text)
            
            # Создаем промпт для React-агента
            prompt = f"""Ты персональный помощник пользователя в Telegram. 

КОНТЕКСТ БЕСЕДЫ:
{context_text}

ТЕКУЩИЙ ВОПРОС: {message_text}

РЕЗУЛЬТАТЫ ПОИСКА В БАЗЕ ЗНАНИЙ:
{knowledge_context}

У тебя есть доступ к инструментам:
- browser_*: веб-браузер для поиска актуальной информации

ИНСТРУКЦИЯ:
1. Если вопрос можно ответить по контексту беседы - отвечай сразу
2. Если есть результаты поиска в базе знаний - используй их в ответе
3. Если нужна актуальная информация из интернета - используй браузер
4. Отвечай дружелюбно и по существу

Твой ответ:"""

            # Генерируем ответ через React-агента
            thread_id = f"user_{user_id}"
            response = await self.agent_runner(prompt, thread_id=thread_id)
            
            # Добавляем ответ в контекст
            assistant_message = {
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now().isoformat()
            }
            self.add_to_context(user_id, assistant_message)
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения от {user_id}: {e}")
            return f"Извините, произошла ошибка при обработке вашего сообщения: {str(e)}"

    async def handle_start_command(self, message: types.Message):
        """Команда начала работы с персональным помощником"""
        await message.reply(
            "👋 Привет! Я ваш персональный AI-помощник.\n\n"
            "Я могу:\n"
            "🔍 Искать информацию в базе знаний\n"
            "💬 Отвечать на вопросы по контексту беседы\n"
            "🌐 Находить актуальную информацию в интернете\n\n"
            "Просто задайте мне любой вопрос!"
        )

    async def handle_clear_command(self, message: types.Message):
        """Команда очистки контекста беседы"""
        user_id = str(message.from_user.id)
        if user_id in self.user_contexts:
            self.user_contexts[user_id] = []
            await message.reply("🧹 Контекст беседы очищен!")
        else:
            await message.reply("Контекст уже пуст.")

    async def handle_context_command(self, message: types.Message):
        """Команда просмотра текущего контекста"""
        user_id = str(message.from_user.id)
        context = self.get_user_context(user_id)
        context_info = f"📊 Контекст беседы:\n"
        context_info += f"📄 Сообщений в памяти: {len(context)}\n"
        context_info += f"🔄 Лимит: {MAX_CONTEXT_LENGTH} сообщений\n"
        context_info += f"📝 Суммаризация при: {SUMMARIZE_THRESHOLD} сообщениях"
        await message.reply(context_info)

    async def handle_message(self, message: types.Message):
        """Обрабатывает личные сообщения пользователей"""
        
        # Игнорируем сообщения от ботов
        if message.from_user.is_bot:
            return
        
        # Игнорируем пустые сообщения
        if not message.text:
            return
        
        user_id = str(message.from_user.id)
        username = message.from_user.username or "unknown"
        
        logger.info(f"💬 Личное сообщение от @{username} (ID: {user_id}): {message.text[:100]}...")
        
        try:
            # Показываем, что бот печатает
            await message.bot.send_chat_action(message.chat.id, "typing")
            
            # Обрабатываем через персонального помощника
            response = await self.process_message(user_id, message.text)
            
            # Отправляем ответ
            await message.reply(response)
            
            logger.info(f"✅ Ответ отправлен пользователю @{username}")
            
        except Exception as e:
            logger.error(f"❌ Ошибка обработки сообщения от @{username}: {e}")
            await message.reply("Извините, произошла ошибка. Попробуйте позже.")

# Оригинальные глобальные переменные для обратной совместимости
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Глобальный экземпляр помощника
personal_assistant = None

@dp.message(Command("start"))
async def start_command(message: types.Message):
    """Команда начала работы с персональным помощником"""
    if message.chat.type == 'private':
        await message.reply(
            "👋 Привет! Я ваш персональный AI-помощник.\n\n"
            "Я могу:\n"
            "🔍 Искать информацию в базе знаний\n"
            "💬 Отвечать на вопросы по контексту беседы\n"
            "🌐 Находить актуальную информацию в интернете\n\n"
            "Просто задайте мне любой вопрос!"
        )

@dp.message(Command("clear"))
async def clear_command(message: types.Message):
    """Команда очистки контекста беседы"""
    if message.chat.type == 'private':
        user_id = str(message.from_user.id)
        if personal_assistant and user_id in personal_assistant.user_contexts:
            personal_assistant.user_contexts[user_id] = []
            await message.reply("🧹 Контекст беседы очищен!")
        else:
            await message.reply("Контекст уже пуст.")

@dp.message(Command("context"))
async def context_command(message: types.Message):
    """Команда просмотра текущего контекста"""
    if message.chat.type == 'private':
        user_id = str(message.from_user.id)
        if personal_assistant:
            context = personal_assistant.get_user_context(user_id)
            context_info = f"📊 Контекст беседы:\n"
            context_info += f"📄 Сообщений в памяти: {len(context)}\n"
            context_info += f"🔄 Лимит: {MAX_CONTEXT_LENGTH} сообщений\n"
            context_info += f"📝 Суммаризация при: {SUMMARIZE_THRESHOLD} сообщениях"
            await message.reply(context_info)

@dp.message()
async def handle_private_message(message: types.Message):
    """Обрабатывает личные сообщения пользователей"""
    
    # Только личные сообщения
    if message.chat.type != 'private':
        return
    
    # Игнорируем сообщения от ботов
    if message.from_user.is_bot:
        return
    
    # Игнорируем пустые сообщения
    if not message.text:
        return
    
    user_id = str(message.from_user.id)
    username = message.from_user.username or "unknown"
    
    logger.info(f"💬 Личное сообщение от @{username} (ID: {user_id}): {message.text[:100]}...")
    
    try:
        # Показываем, что бот печатает
        await bot.send_chat_action(message.chat.id, "typing")
        
        # Обрабатываем через персонального помощника
        response = await personal_assistant.process_message(user_id, message.text)
        
        # Отправляем ответ
        await message.reply(response)
        
        logger.info(f"✅ Ответ отправлен пользователю @{username}")
        
    except Exception as e:
        logger.error(f"❌ Ошибка обработки сообщения от @{username}: {e}")
        await message.reply("Извините, произошла ошибка. Попробуйте позже.")

async def main():
    """Запуск персонального помощника"""
    global personal_assistant
    
    logger.info("🚀 Запуск Personal RAG Assistant...")
    logger.info("🧠 React-агент с памятью диалогов и RAG")
    
    # Инициализируем MCP агента (с ChromaDB и браузером)
    async with setup_agent() as agent:
        personal_assistant = PersonalAssistant()
        personal_assistant.agent_runner = agent
        
        logger.info("✅ MCP агент инициализирован (браузер + ChromaDB)!")
        logger.info("🔍 Доступные команды: /start, /clear, /context")
        logger.info("🤖 Personal Assistant готов к работе!")
        
        try:
            await dp.start_polling(bot)
        except KeyboardInterrupt:
            logger.info("\n👋 Personal Assistant остановлен")

if __name__ == "__main__":
    asyncio.run(main()) 