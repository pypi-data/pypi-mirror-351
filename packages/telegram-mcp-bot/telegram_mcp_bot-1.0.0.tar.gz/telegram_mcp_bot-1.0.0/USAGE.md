# 🚀 Быстрый запуск Telegram MCP Bot

## 🎯 Для демонстрации коллегам

### 1. Подготовка
```bash
git clone <repo-url>
cd telegram-mcp-bot
uv sync
npx playwright install chromium
```

### 2. Настройка
```bash
cp env.example .env
# Отредактируйте .env с вашими токенами
```

### 3. Запуск (polling режим)
```bash
uv run python unified_bot.py
```

**Готово!** Бот работает в режиме демонстрации.

## 🏗️ Варианты запуска

### 🖥️ Локально (простой способ)
```bash
# Демо режим
python unified_bot.py

# Продакшн режим  
python webhook_bot.py
```

### 📦 Как пакет Python
```bash
# Установка
pip install -e .

# Мастер настройки
telegram-mcp-bot setup

# Запуск демо
telegram-mcp-bot demo

# Запуск продакшн
telegram-mcp-bot prod
```

### 🐳 Docker
```bash
# Демо режим
docker-compose --profile demo up

# Продакшн режим
docker-compose --profile prod up
```

## 🎮 Как пользоваться

### В групповых чатах:
1. Добавьте бота в группу
2. Отправляйте ссылки - бот их обработает
3. Используйте `/status` для статистики

### В личных сообщениях:
1. Напишите боту в личку
2. Задавайте вопросы - бот найдет информацию в базе
3. Используйте `/clear` для сброса контекста

## 🔧 Переключение режимов

### Из демо в продакшн:
```bash
# 1. Измените .env
DEPLOYMENT_MODE=webhook
WEBHOOK_HOST=your-domain.com

# 2. Запустите webhook версию
python webhook_bot.py
```

## 🆘 Помощь

- Проверка: `python check_unified_bot.py`
- Логи в консоли покажут все операции
- Команды `/status` для диагностики 