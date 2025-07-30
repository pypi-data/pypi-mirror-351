#!/usr/bin/env python3
"""
Детальная проверка метаданных в ChromaDB
"""

import chromadb
import json
from datetime import datetime

def check_metadata():
    """Проверяет метаданные в коллекции telegram_group_messages"""
    try:
        print("🔍 Проверка метаданных в telegram_group_messages...")
        
        client = chromadb.PersistentClient(path='./chroma')
        collection = client.get_collection("telegram_group_messages")
        
        count = collection.count()
        print(f"📄 Всего документов: {count}")
        
        # Получаем все документы с метаданными
        results = collection.get(
            limit=count,
            include=['metadatas', 'documents']
        )
        
        print("\n" + "="*80)
        
        for i, (doc, meta) in enumerate(zip(results['documents'], results['metadatas']), 1):
            print(f"\n📝 ДОКУМЕНТ #{i}:")
            print(f"   Текст: {doc[:100]}...")
            
            if meta:
                print(f"   📊 МЕТАДАННЫЕ:")
                for key, value in meta.items():
                    print(f"      {key}: {value}")
            else:
                print(f"   📊 МЕТАДАННЫЕ: отсутствуют")
            
            print("-" * 60)
        
        print("\n✅ Проверка завершена!")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")

if __name__ == "__main__":
    check_metadata() 