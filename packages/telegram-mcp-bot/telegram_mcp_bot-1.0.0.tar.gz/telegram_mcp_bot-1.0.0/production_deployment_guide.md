# 🚀 Production Deployment Guide

## 📋 Введение

Этот документ содержит полное руководство по развертыванию Unified Telegram Bot в продакшн-среде.

## 🌐 1. Webhook vs Polling

### Почему Webhook лучше для продакшена?

| Критерий | Polling ❌ | Webhook ✅ |
|----------|------------|------------|
| **Скорость отклика** | 1-5 секунд задержка | Мгновенно |
| **Потребление ресурсов** | Постоянные запросы | Только при получении сообщений |
| **Масштабируемость** | Плохая | Отличная |
| **Надежность** | Зависит от стабильности соединения | Telegram гарантирует доставку |

### Настройка Webhook

1. **Скопируйте webhook версию:**
   ```bash
   cp webhook_bot.py production_bot.py
   ```

2. **Настройте переменные окружения:**
   ```bash
   # В .env файле
   WEBHOOK_HOST=your-domain.com
   WEBHOOK_PORT=8443
   WEBHOOK_PATH=/webhook
   DEPLOYMENT_MODE=webhook
   ```

3. **Запуск в продакшене:**
   ```bash
   # С Gunicorn
   gunicorn webhook_bot:create_app -w 1 -k aiohttp.GunicornWebWorker -b 0.0.0.0:8443
   
   # Или напрямую
   python webhook_bot.py
   ```

### SSL сертификат

Telegram требует HTTPS для webhook:

```bash
# Самоподписанный сертификат (для тестирования)
openssl req -newkey rsa:2048 -sha256 -nodes -keyout private.key -x509 -days 365 -out cert.pem

# Let's Encrypt (для продакшена)
certbot --nginx -d your-domain.com
```

## 🖥️ 2. Headless браузер для сервера

### ❌ Проблемы без headless режима

На сервере без GUI (Ubuntu Server, Docker и т.д.):
- Браузер не может открыть окна
- Ошибки типа "Cannot open display"
- Потребление лишних ресурсов

### ✅ Решение: Принудительный headless

#### Способ 1: Переменные окружения (рекомендуется)

```bash
# В .env файле
PLAYWRIGHT_HEADLESS=true
PLAYWRIGHT_NO_SANDBOX=true
PLAYWRIGHT_DISABLE_WEB_SECURITY=true
PLAYWRIGHT_DISABLE_DEV_SHM_USAGE=true
```

#### Способ 2: Промпт-инструкции

Промпты уже содержат инструкции для headless режима. В файле `telegram_collector_direct.py`:

```python
prompt = f"""Обработай эту ссылку:

URL: {url}

Задача:
- Перейди по ссылке
- Получи содержимое страницы  
- Верни мне текст содержимого

ВАЖНО: Всегда используй headless режим браузера!
НЕ сохраняй в ChromaDB - я сделаю это сам!"""
```

#### Способ 3: Конфигурация MCP серверов

Уже настроено в `agent_runner.py` и `agent_runner_browser_only.py`:

```python
"env": {
    "PLAYWRIGHT_HEADLESS": "true",
    "PLAYWRIGHT_NO_SANDBOX": "true",
    "PLAYWRIGHT_DISABLE_WEB_SECURITY": "true",
    # ... другие настройки
}
```

## 🔧 3. Управление ресурсами браузера

### Закрытие браузера

MCP Playwright автоматически управляет жизненным циклом браузера через контекст-менеджеры:

```python
async with setup_agent() as agent:
    # Браузер открывается
    result = await agent(prompt)
    # Браузер автоматически закрывается при выходе из контекста
```

### Мониторинг ресурсов

```bash
# Проверка процессов браузера
ps aux | grep -E "(chrome|firefox|webkit)"

# Использование памяти
free -h

# Использование CPU
top -p $(pgrep -f "unified_bot")
```

## 🐳 4. Docker развертывание

### Dockerfile

```dockerfile
FROM python:3.12-slim

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Node.js для MCP Playwright
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs

# Установка uv
RUN pip install uv

WORKDIR /app

# Копирование проекта
COPY . .

# Установка зависимостей
RUN uv sync

# Установка Playwright браузеров
RUN npx playwright install chromium
RUN npx playwright install-deps chromium

# Переменные окружения для headless режима
ENV PLAYWRIGHT_HEADLESS=true
ENV PLAYWRIGHT_NO_SANDBOX=true
ENV PLAYWRIGHT_DISABLE_WEB_SECURITY=true
ENV TOKENIZERS_PARALLELISM=false

EXPOSE 8443

CMD ["uv", "run", "python", "webhook_bot.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  telegram-bot:
    build: .
    ports:
      - "8443:8443"
    environment:
      - TELEGRAM_TOKEN=${TELEGRAM_TOKEN}
      - WEBHOOK_HOST=${WEBHOOK_HOST}
      - LLM_PROXY_API_BASE_URL=${LLM_PROXY_API_BASE_URL}
      - LLM_PROXY_API_KEY=${LLM_PROXY_API_KEY}
      - PLAYWRIGHT_HEADLESS=true
    volumes:
      - ./chroma:/app/chroma
      - ./logs:/app/logs
    restart: unless-stopped
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - telegram-bot
    restart: unless-stopped
```

## 📊 5. Мониторинг и логирование

### Systemd сервис

```bash
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Unified Telegram Bot
After=network.target

[Service]
Type=simple
User=telegram-bot
WorkingDirectory=/opt/telegram-bot
Environment=PATH=/opt/telegram-bot/.venv/bin
ExecStart=/opt/telegram-bot/.venv/bin/python webhook_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### Логирование

```python
# В production_config.py
import logging
from logging.handlers import RotatingFileHandler

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler(
            'logs/telegram_bot.log', 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5
        ),
        logging.StreamHandler()
    ]
)
```

## ⚡ 6. Оптимизация производительности

### Переменные окружения для оптимизации

```bash
# Отключение HuggingFace предупреждений
TOKENIZERS_PARALLELISM=false

# Playwright оптимизации
PLAYWRIGHT_BROWSER_TIMEOUT=30000
PLAYWRIGHT_PAGE_TIMEOUT=20000
PLAYWRIGHT_NAVIGATION_TIMEOUT=15000

# Ограничение ресурсов
REQUEST_DELAY=2000
MAX_CONCURRENT_REQUESTS=2
```

### Ограничение обработки ссылок

```python
# В telegram_collector_direct.py уже реализовано:
# - Максимум 2 ссылки за раз
# - Паузы между обработкой
# - Таймауты для избежания зависания
```

## 🔒 7. Безопасность

### Переменные окружения

```bash
# Никогда не коммитьте в git:
echo ".env" >> .gitignore
echo "*.key" >> .gitignore
echo "*.pem" >> .gitignore
```

### Файрвол

```bash
# Разрешить только необходимые порты
ufw allow 22    # SSH
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 8443  # Webhook
ufw enable
```

## 🚀 8. Быстрый старт для продакшена

### Шаг 1: Подготовка сервера

```bash
# Обновление системы
sudo apt update && sudo apt upgrade -y

# Установка зависимостей
sudo apt install -y python3 python3-pip nodejs npm git

# Установка uv
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Шаг 2: Клонирование и настройка

```bash
# Клонирование
git clone your-repo
cd telegram-mcp-bot

# Установка зависимостей
uv sync

# Копирование конфигурации
cp production.env.example .env
# Отредактируйте .env с вашими настройками
```

### Шаг 3: Установка Playwright

```bash
# Установка браузеров
npx playwright install chromium
npx playwright install-deps chromium
```

### Шаг 4: Запуск

```bash
# Тестовый запуск
uv run python webhook_bot.py

# Или с systemd
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

## 📝 9. Проверочный список

- [ ] Webhook настроен и работает
- [ ] SSL сертификат установлен
- [ ] Headless режим включен
- [ ] Логирование настроено
- [ ] Мониторинг работает
- [ ] Файрвол настроен
- [ ] Автозапуск настроен
- [ ] Backup ChromaDB настроен

## 🆘 10. Решение проблем

### Браузер не работает в headless

```bash
# Проверка переменных окружения
env | grep PLAYWRIGHT

# Тест headless режима
npx playwright open --browser chromium --headless https://example.com
```

### Webhook не получает сообщения

```bash
# Проверка webhook URL
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/getWebhookInfo"

# Установка webhook
curl -X POST "https://api.telegram.org/bot${TELEGRAM_TOKEN}/setWebhook" \
     -d "url=https://your-domain.com/webhook"
```

### Высокое потребление памяти

```bash
# Мониторинг процессов
ps aux --sort=-%mem | head -10

# Ограничение памяти для Docker
docker run --memory=1g your-bot-image
```

---

**🎯 Итог:** С этой конфигурацией ваш бот будет стабильно работать в продакшене с headless браузером, webhook API и оптимизированным потреблением ресурсов! 