#!/usr/bin/env python3
"""
Unified Telegram Bot with Message Routing
- Group messages -> Group Collector Agent (browser-only MCP)
- Private messages -> Personal RAG Assistant (full MCP)
"""

import asyncio
import logging
import os
from typing import Dict, Any

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage

# Import our agents
from telegram_mcp_bot.telegram_collector_direct import TelegramCollectorDirect
from telegram_mcp_bot.personal_assistant import PersonalAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedTelegramBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_TOKEN")
        if not self.bot_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Initialize agents
        self.group_agent = TelegramCollectorDirect()
        self.personal_agent = PersonalAssistant()
        
        # Setup handlers
        self.setup_handlers()
        
        logger.info("Unified Telegram Bot initialized")
    
    def setup_handlers(self):
        """Setup message handlers with routing logic"""
        
        # Command handlers (work in both private and group chats)
        @self.dp.message(Command("start"))
        async def cmd_start(message: Message):
            if message.chat.type == "private":
                await self.personal_agent.handle_start_command(message)
            else:
                await message.reply(
                    "👋 Привет! Я работаю в групповых чатах для сбора информации.\n"
                    "Для персональной помощи напишите мне в личные сообщения."
                )
        
        @self.dp.message(Command("status"))
        async def cmd_status(message: Message):
            if message.chat.type == "private":
                await self.personal_agent.handle_context_command(message)
            else:
                await self.group_agent.handle_status_command(message)
        
        @self.dp.message(Command("stats"))
        async def cmd_stats(message: Message):
            if message.chat.type != "private":
                await self.group_agent.handle_stats_command(message)
            else:
                await message.reply("Команда /stats доступна только в групповых чатах")
        
        @self.dp.message(Command("clear"))
        async def cmd_clear(message: Message):
            if message.chat.type == "private":
                await self.personal_agent.handle_clear_command(message)
            else:
                await message.reply("Команда /clear доступна только в личных сообщениях")
        
        @self.dp.message(Command("context"))
        async def cmd_context(message: Message):
            if message.chat.type == "private":
                await self.personal_agent.handle_context_command(message)
            else:
                await message.reply("Команда /context доступна только в личных сообщениях")
        
        # Main message handler with routing
        @self.dp.message()
        async def handle_message(message: Message):
            try:
                if message.chat.type == "private":
                    # Private message -> Personal RAG Assistant
                    logger.info(f"Routing private message from user {message.from_user.id} to Personal Assistant")
                    await self.personal_agent.handle_message(message)
                else:
                    # Group message -> Group Collector
                    logger.info(f"Routing group message from chat {message.chat.id} to Group Collector")
                    await self.group_agent.handle_message(message)
                    
            except Exception as e:
                logger.error(f"Error handling message: {e}")
                await message.reply(f"❌ Произошла ошибка: {str(e)}")
    
    async def start_polling(self):
        """Start the bot polling"""
        logger.info("Starting unified bot polling...")
        
        # Initialize agents
        await self.group_agent.initialize()
        await self.personal_agent.initialize()
        
        try:
            await self.dp.start_polling(self.bot)
        finally:
            # Cleanup
            await self.group_agent.cleanup()
            await self.personal_agent.cleanup()
            await self.bot.session.close()

async def main():
    """Main entry point"""
    try:
        unified_bot = UnifiedTelegramBot()
        await unified_bot.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 