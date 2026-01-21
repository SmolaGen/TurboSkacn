#!/bin/zsh

# Скрипт для запуска Claude CLI с правильными настройками для VibeProxy
# Это решает проблемы Auth conflict и "unknown provider"

# 1. Убираем конфликтующие переменные
unset ANTHROPIC_API_KEY

# 2. Настраиваем подключение к VibeProxy
export ANTHROPIC_BASE_URL="http://127.0.0.1:8317/v1"

# 3. Указываем Management Key как OAuth токен
export CLAUDE_CODE_OAUTH_TOKEN="9CDCC8DB-769D-48BD-AF4D-08F97A47BE98"

# 4. Принудительно задаем имя модели, которое понимает VibeProxy
export ANTHROPIC_MODEL="gemini-claude-sonnet-4-5"

# Дополнительные настройки для стабильности
export NO_PROXY="127.0.0.1,localhost"

echo "🚀 Запуск Claude через VibeProxy (Gemini)..."
echo "📍 Base URL: $ANTHROPIC_BASE_URL"
echo "🤖 Model: $ANTHROPIC_MODEL"
echo "----------------------------------------"

# Запускаем оригинальный Claude CLI со всеми переданными аргументами
claude "$@"
