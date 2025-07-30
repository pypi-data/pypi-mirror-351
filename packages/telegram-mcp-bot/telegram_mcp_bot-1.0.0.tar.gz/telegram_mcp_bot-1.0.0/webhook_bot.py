#!/usr/bin/env python3
"""
Unified Telegram Bot with Webhook Support
Production-ready version with webhook instead of polling
"""

import asyncio
import logging
import os
from typing import Dict, Any

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

# Import our agents
from telegram_mcp_bot.telegram_collector_direct import TelegramCollectorDirect
from telegram_mcp_bot.personal_assistant import PersonalAssistant

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class UnifiedTelegramBotWebhook:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_TOKEN")
        if not self.bot_token:
            raise ValueError("TELEGRAM_TOKEN environment variable is required")
        
        # Webhook configuration
        self.webhook_host = os.getenv("WEBHOOK_HOST", "localhost")
        self.webhook_port = int(os.getenv("WEBHOOK_PORT", "8443"))
        self.webhook_path = os.getenv("WEBHOOK_PATH", "/webhook")
        self.webhook_url = f"https://{self.webhook_host}{self.webhook_path}"
        
        self.bot = Bot(token=self.bot_token)
        self.dp = Dispatcher(storage=MemoryStorage())
        
        # Initialize agents
        self.group_agent = TelegramCollectorDirect()
        self.personal_agent = PersonalAssistant()
        
        # Setup handlers
        self.setup_handlers()
        
        logger.info("Unified Telegram Bot (Webhook) initialized")
        logger.info(f"Webhook URL: {self.webhook_url}")
    
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
    
    async def on_startup(self):
        """Initialize agents and set webhook"""
        logger.info("Starting webhook bot...")
        
        # Initialize agents
        await self.group_agent.initialize()
        await self.personal_agent.initialize()
        
        # Set webhook
        webhook_info = await self.bot.get_webhook_info()
        if webhook_info.url != self.webhook_url:
            logger.info(f"Setting webhook to {self.webhook_url}")
            await self.bot.set_webhook(
                url=self.webhook_url,
                drop_pending_updates=True
            )
        else:
            logger.info("Webhook already set correctly")
    
    async def on_shutdown(self):
        """Cleanup resources"""
        logger.info("Shutting down webhook bot...")
        
        # Delete webhook
        await self.bot.delete_webhook()
        
        # Cleanup agents
        await self.group_agent.cleanup()
        await self.personal_agent.cleanup()
        await self.bot.session.close()
    
    def create_app(self):
        """Create aiohttp application with webhook handler"""
        # Create webhook request handler
        webhook_requests_handler = SimpleRequestHandler(
            dispatcher=self.dp,
            bot=self.bot
        )
        
        # Register webhook handler on application
        webhook_requests_handler.register(app, path=self.webhook_path)
        
        # Add startup and shutdown handlers
        app.on_startup.append(lambda app: asyncio.create_task(self.on_startup()))
        app.on_shutdown.append(lambda app: asyncio.create_task(self.on_shutdown()))
        
        return app

def create_app():
    """Factory function for creating the app"""
    global unified_bot
    unified_bot = UnifiedTelegramBotWebhook()
    app = web.Application()
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=unified_bot.dp,
        bot=unified_bot.bot
    )
    webhook_requests_handler.register(app, path=unified_bot.webhook_path)
    
    # Add startup and shutdown handlers
    async def startup(app):
        await unified_bot.on_startup()
    
    async def shutdown(app):
        await unified_bot.on_shutdown()
    
    app.on_startup.append(startup)
    app.on_cleanup.append(shutdown)
    
    return app

async def main():
    """Main entry point for webhook mode"""
    try:
        unified_bot = UnifiedTelegramBotWebhook()
        app = create_app()
        
        # Run webhook server
        runner = web.AppRunner(app)
        await runner.setup()
        
        site = web.TCPSite(
            runner, 
            host="0.0.0.0", 
            port=unified_bot.webhook_port
        )
        await site.start()
        
        logger.info(f"Webhook server started on port {unified_bot.webhook_port}")
        logger.info("Press Ctrl+C to stop")
        
        # Keep running
        try:
            await asyncio.Event().wait()
        except KeyboardInterrupt:
            logger.info("Webhook bot stopped by user")
        finally:
            await runner.cleanup()
            
    except Exception as e:
        logger.error(f"Webhook bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main()) 