#!/usr/bin/env python3
"""
Проверка статуса единого бота
"""

import asyncio
import os
import chromadb
from datetime import datetime

async def check_unified_bot_status():
    """Проверяет статус единого бота"""
    print("🔍 Проверка статуса единого Telegram бота...")
    print(f"⏰ Время проверки: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Проверяем переменные окружения
    print("📋 Переменные окружения:")
    telegram_token = os.getenv("TELEGRAM_TOKEN")
    group_chat_id = os.getenv("GROUP_CHAT_ID")
    
    print(f"   TELEGRAM_TOKEN: {'✅ Установлен' if telegram_token else '❌ Не установлен'}")
    print(f"   GROUP_CHAT_ID: {group_chat_id or '❌ Не установлен'}")
    print()
    
    # Проверяем ChromaDB
    print("💾 Статус ChromaDB:")
    try:
        chroma_client = chromadb.PersistentClient(path='./chroma')
        collections = chroma_client.list_collections()
        
        print(f"   Коллекций: {len(collections)}")
        for collection in collections:
            count = collection.count()
            print(f"   - {collection.name}: {count} документов")
        
        # Проверяем основную коллекцию
        try:
            main_collection = chroma_client.get_collection("telegram_group_messages")
            count = main_collection.count()
            print(f"   ✅ Основная коллекция: {count} документов")
        except Exception as e:
            print(f"   ❌ Основная коллекция недоступна: {e}")
            
    except Exception as e:
        print(f"   ❌ Ошибка подключения к ChromaDB: {e}")
    
    print()
    
    # Проверяем процессы
    print("🔄 Активные процессы:")
    import subprocess
    try:
        result = subprocess.run(
            ["ps", "aux"], 
            capture_output=True, 
            text=True
        )
        
        lines = result.stdout.split('\n')
        bot_processes = [line for line in lines if 'python' in line and ('unified_bot' in line or 'main.py' in line or 'personal_assistant.py' in line)]
        
        if bot_processes:
            for process in bot_processes:
                if 'grep' not in process and process.strip():
                    print(f"   📱 {process.split()[-1]} (PID: {process.split()[1]})")
        else:
            print("   ❌ Нет активных процессов ботов")
            
    except Exception as e:
        print(f"   ❌ Ошибка проверки процессов: {e}")
    
    print()
    print("✅ Проверка завершена!")

if __name__ == "__main__":
    asyncio.run(check_unified_bot_status()) 