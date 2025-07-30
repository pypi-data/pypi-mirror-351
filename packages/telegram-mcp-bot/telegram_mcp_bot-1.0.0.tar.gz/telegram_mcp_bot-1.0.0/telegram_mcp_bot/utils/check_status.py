#!/usr/bin/env python3
"""
Простая проверка статуса ChromaDB
"""

import chromadb
from datetime import datetime

def check_status():
    """Проверяет статус ChromaDB"""
    try:
        print("🔍 Проверка ChromaDB...")
        
        client = chromadb.PersistentClient(path='./chroma')
        collections = client.list_collections()
        
        print(f"📊 Всего коллекций: {len(collections)}")
        
        for col in collections:
            count = col.count()
            print(f"\n📁 Коллекция: {col.name}")
            print(f"   📄 Документов: {count}")
            
            if count > 0:
                # Получаем последний документ
                results = col.get(limit=1, include=['metadatas'])
                if results['metadatas'] and results['metadatas'][0]:
                    meta = results['metadatas'][0]
                    timestamp = meta.get('timestamp', 'unknown')
                    source = meta.get('source', 'unknown')
                    print(f"   🕐 Последний: {timestamp[:16]} ({source})")
                else:
                    print(f"   🕐 Последний: без метаданных")
        
        print("\n✅ Проверка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_status() 