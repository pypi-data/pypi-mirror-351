#!/usr/bin/env python3
"""
Тестирование поиска в ChromaDB
"""

import chromadb
from datetime import datetime

def test_chroma_search():
    """Тестирует поиск в ChromaDB"""
    print("🔍 Тестирование поиска в ChromaDB...")
    print(f"⏰ Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    try:
        # Подключаемся к ChromaDB
        chroma_client = chromadb.PersistentClient(path='./chroma')
        collection = chroma_client.get_collection("telegram_group_messages")
        
        print(f"📊 Всего документов в коллекции: {collection.count()}")
        print()
        
        # Получаем все документы с метаданными
        all_docs = collection.get(include=['documents', 'metadatas'])
        
        print("📄 Все документы в базе:")
        for i, (doc, meta) in enumerate(zip(all_docs['documents'], all_docs['metadatas']), 1):
            print(f"\n{i}. Документ:")
            print(f"   Источник: {meta.get('source', 'unknown')}")
            print(f"   Тип: {meta.get('message_type', 'unknown')}")
            print(f"   URL: {meta.get('original_url', 'нет')}")
            print(f"   Время: {meta.get('timestamp', 'unknown')[:16]}")
            print(f"   Содержимое: {doc[:200]}...")
        
        print("\n" + "="*50)
        
        # Тестируем поиск GitHub
        print("\n🔍 Поиск GitHub ссылок:")
        github_results = collection.query(
            query_texts=["github repository code"],
            n_results=5,
            include=['documents', 'metadatas']
        )
        
        if github_results['documents'][0]:
            print(f"Найдено {len(github_results['documents'][0])} результатов:")
            for i, (doc, meta) in enumerate(zip(github_results['documents'][0], github_results['metadatas'][0]), 1):
                print(f"\n{i}. GitHub результат:")
                print(f"   URL: {meta.get('original_url', 'нет')}")
                print(f"   Тип: {meta.get('message_type', 'unknown')}")
                print(f"   Содержимое: {doc[:150]}...")
        else:
            print("❌ GitHub ссылки не найдены")
        
        print("\n" + "="*50)
        
        # Тестируем общий поиск
        print("\n🔍 Общий поиск по ключевым словам:")
        general_results = collection.query(
            query_texts=["код программирование разработка"],
            n_results=3,
            include=['documents', 'metadatas']
        )
        
        if general_results['documents'][0]:
            print(f"Найдено {len(general_results['documents'][0])} результатов:")
            for i, (doc, meta) in enumerate(zip(general_results['documents'][0], general_results['metadatas'][0]), 1):
                print(f"\n{i}. Результат:")
                print(f"   Источник: {meta.get('source', 'unknown')}")
                print(f"   Содержимое: {doc[:150]}...")
        else:
            print("❌ Результаты не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    
    print("\n✅ Тестирование завершено!")

if __name__ == "__main__":
    test_chroma_search() 