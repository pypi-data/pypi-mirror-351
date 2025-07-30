# 🤖 Unified Telegram MCP Bot

**Умный Telegram-бот с поддержкой Model Context Protocol (MCP) для сбора информации и персонального RAG-ассистента.**

## 🎯 Особенности

### 🔄 Единая архитектура с маршрутизацией сообщений
- **Групповые чаты** → Коллектор информации (обрабатывает ссылки, сохраняет в базу)
- **Личные сообщения** → RAG-ассистент (поиск по базе + умные ответы)

### 🧠 Интеллектуальные возможности
- **Автоматическая обработка ссылок** через MCP Playwright
- **RAG (Retrieval-Augmented Generation)** с автоматическим поиском
- **Контекстная память** с автоматическим сжатием диалогов
- **Прямое подключение к ChromaDB** (минуя ненадежный MCP ChromaDB)

### 🚀 Режимы развертывания
- **Development** (polling) - для демонстрации и разработки
- **Production** (webhook) - для продакшн-серверов

## 📋 Быстрый старт

### 1. Установка зависимостей

```bash
# Клонируйте репозиторий
git clone <your-repo-url>
cd telegram-mcp-bot

# Установите uv (если еще нет)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Установите зависимости Python
uv sync

# Установите MCP Playwright
npx playwright install chromium
```

### 2. Настройка окружения

```bash
# Скопируйте пример конфигурации
cp .env.example .env

# Отредактируйте .env своими данными:
# - TELEGRAM_TOKEN (получите у @BotFather)
# - LLM_PROXY_API_KEY (ваш API ключ)
# - другие настройки по необходимости
```

### 3. Запуск для демонстрации

```bash
# Режим разработки (polling)
uv run python unified_bot.py
```

Бот готов! Добавьте его в групповой чат и напишите в личные сообщения.

## 🎮 Использование

### Командные интерфейсы

#### В групповых чатах:
- Просто отправляйте ссылки - бот автоматически их обработает
- `/status` - статистика работы бота
- `/stats` - детальная статистика обработки

#### В личных сообщениях:
- Любой вопрос - бот найдет информацию в базе и ответит
- `/start` - приветствие и инструкции
- `/clear` - очистить контекст диалога
- `/context` - показать текущий контекст

### Автоматические функции

#### Обработка ссылок в группах:
```
👤 Пользователь: https://github.com/awesome/project
🤖 Бот: ✅ Ссылка обработана и сохранена в базу
```

#### RAG-поиск в личных сообщениях:
```
👤 Пользователь: есть ли что-то про GitHub проекты?
🔍 Бот ищет в базе...
🤖 Бот: Найдено 3 репозитория: awesome/project, cool/tool...
```

## 🏗️ Архитектура системы

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Telegram      │    │   Unified Bot    │    │   ChromaDB      │
│   Messages      │───▶│   Router         │───▶│   Knowledge     │
│                 │    │                  │    │   Base          │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌──────────────────┐
                       │   MCP Playwright │
                       │   Browser        │
                       └──────────────────┘
```

### Компоненты:

#### 🔄 UnifiedTelegramBot (unified_bot.py)
- Единая точка входа
- Маршрутизация по типу чата
- Управление агентами

#### 📊 TelegramCollectorDirect (telegram_collector_direct.py)
- Обработка групповых сообщений
- MCP Playwright для ссылок
- Прямое сохранение в ChromaDB

#### 🧠 PersonalAssistant (personal_assistant.py)
- Персональный RAG-ассистент
- Автоматический поиск по ключевым словам
- Контекстная память диалогов

## 🔧 Конфигурация

### Переменные окружения (.env)

```bash
# ==================== ОСНОВНЫЕ НАСТРОЙКИ ====================
TELEGRAM_TOKEN=your_bot_token_here
LLM_PROXY_API_BASE_URL=your_llm_api_url
LLM_PROXY_API_KEY=your_api_key

# ==================== РЕЖИМ РАЗВЕРТЫВАНИЯ ====================
DEPLOYMENT_MODE=polling  # polling для демо, webhook для продакшна

# ==================== ПРОДАКШН НАСТРОЙКИ ====================
WEBHOOK_HOST=your-domain.com
WEBHOOK_PORT=8443
WEBHOOK_PATH=/webhook

# ==================== БРАУЗЕР (HEADLESS ДЛЯ СЕРВЕРОВ) ====================
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_NO_SANDBOX=true
PLAYWRIGHT_DISABLE_WEB_SECURITY=true
```

### Автоматические настройки MCP

Система автоматически настраивает MCP серверы:

```python
# Playwright с headless для серверов
"env": {
    "PLAYWRIGHT_HEADLESS": "true",
    "PLAYWRIGHT_NO_SANDBOX": "true",
    # ... другие оптимизации
}

# ChromaDB с прямым подключением
chroma_client = chromadb.PersistentClient(path="./chroma")
```

## 🚀 Переход в продакшн

### Быстрое переключение:

```bash
# 1. Смените режим в .env
DEPLOYMENT_MODE=webhook
WEBHOOK_HOST=your-domain.com

# 2. Запустите webhook версию
uv run python webhook_bot.py

# Или с Gunicorn
gunicorn webhook_bot:create_app -w 1 -k aiohttp.GunicornWebWorker -b 0.0.0.0:8443
```

### Docker развертывание:

```bash
# Сборка образа
docker build -t telegram-mcp-bot .

# Запуск с переменными окружения
docker run -d \
  -p 8443:8443 \
  -e TELEGRAM_TOKEN=$TELEGRAM_TOKEN \
  -e WEBHOOK_HOST=$WEBHOOK_HOST \
  -v ./chroma:/app/chroma \
  telegram-mcp-bot
```

### Systemd сервис:

```bash
# Создайте systemd сервис
sudo cp deploy/telegram-bot.service /etc/systemd/system/
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## 📊 Мониторинг и отладка

### Команды диагностики:

```bash
# Проверка статуса бота
uv run python check_unified_bot.py

# Тест поиска в ChromaDB
uv run python test_chroma_query.py

# Проверка MCP серверов
env | grep PLAYWRIGHT
```

### Логи и метрики:

- **Автоматическое логирование** всех операций
- **Статистика через команды** /status и /stats
- **Graceful error handling** с детальными сообщениями

## 🔧 Разработка и настройка

### Структура проекта:

```
telegram-mcp-bot/
├── telegram_mcp_bot/          # Основной пакет
│   ├── telegram_collector_direct.py
│   ├── personal_assistant.py
│   ├── agent_runner.py
│   └── chroma_utils.py
├── unified_bot.py             # Polling режим
├── webhook_bot.py             # Webhook режим  
├── production_deployment_guide.md
├── .env.example
└── production.env.example
```

### Кастомизация агентов:

#### Изменение промптов:
```python
# В telegram_collector_direct.py
SYSTEM_PROMPT = """
Ваш кастомный промпт для коллектора...
"""

# В personal_assistant.py  
SYSTEM_PROMPT = """
Ваш кастомный промпт для ассистента...
"""
```

#### Настройка поиска:
```python
# В personal_assistant.py
SEARCH_KEYWORDS = ["github", "проект", "код", "репозиторий"]  # Ваши ключевые слова
```

## 🎁 Дополнительные возможности

### MCP Tools доступные:
- **browser_navigate** - навигация по веб-страницам
- **browser_snapshot** - снимки страниц
- **Прямой ChromaDB** - надежное сохранение и поиск

### Автоматические оптимизации:
- **Ограничение ссылок** (максимум 2 за раз)
- **Паузы между запросами** (избегание rate limit)
- **Headless браузер** для серверов
- **Контекстное сжатие** диалогов

## 🆘 Решение проблем

### Частые проблемы:

#### Бот не отвечает:
```bash
# Проверьте токен
echo $TELEGRAM_TOKEN

# Проверьте процесс
ps aux | grep unified_bot
```

#### Браузер не работает:
```bash
# Установите браузеры
npx playwright install chromium

# Проверьте headless режим
env | grep PLAYWRIGHT_HEADLESS
```

#### Ошибки MCP:
```bash
# Проверьте MCP серверы
npx --version
uv --version
```

### Получение помощи:

1. Проверьте логи в консоли
2. Используйте команды `/status` для диагностики
3. Запустите `check_unified_bot.py` для полной проверки

## 📦 Как пакет Python

Система также доступна как Python пакет:

```bash
# Установка как пакет
pip install -e .

# Использование в коде
from telegram_mcp_bot import TelegramCollectorDirect, PersonalAssistant
```

## 🏆 Готово к использованию!

- ✅ **Демонстрация**: `python unified_bot.py`
- ✅ **Продакшн**: `python webhook_bot.py` 
- ✅ **Мониторинг**: команды `/status`, `/stats`
- ✅ **Документация**: полные инструкции
- ✅ **Docker**: готовые контейнеры
- ✅ **Масштабирование**: webhook + системный сервис

---

**🎯 Результат:** Полнофункциональная система для демонстрации коллегам с возможностью быстрого перехода в продакшн!

## 📄 Лицензия

MIT License - используйте свободно для любых целей.

## 🤝 Вклад в проект

Приветствуются pull requests и issues! Создавайте форки и предлагайте улучшения.
