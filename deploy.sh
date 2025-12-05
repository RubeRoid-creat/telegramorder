#!/bin/bash

# Скрипт развертывания Telegram Order Bot на Ubuntu
# Использование: sudo ./deploy.sh

set -e  # Остановка при ошибке

echo "🚀 Начинаем развертывание Telegram Order Bot..."

# Проверка прав root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Пожалуйста, запустите скрипт с правами root: sudo ./deploy.sh"
    exit 1
fi

# Определение директории проекта
PROJECT_DIR="/opt/telegram-order-bot"
SERVICE_USER="telegram-bot"
SERVICE_FILE="telegram-order-bot.service"

# Получение директории, где находится скрипт
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo "📦 Установка системных зависимостей..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git

echo "👤 Создание пользователя для сервиса..."
if ! id "$SERVICE_USER" &>/dev/null; then
    useradd -r -s /bin/false -d "$PROJECT_DIR" -m "$SERVICE_USER"
    echo "✅ Пользователь $SERVICE_USER создан"
else
    echo "ℹ️ Пользователь $SERVICE_USER уже существует"
fi

echo "📂 Создание директории проекта..."
mkdir -p "$PROJECT_DIR"
chown "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"

echo "📥 Копирование файлов проекта..."
cp -r "$SCRIPT_DIR"/* "$PROJECT_DIR"/ 2>/dev/null || true
chown -R "$SERVICE_USER:$SERVICE_USER" "$PROJECT_DIR"

echo "🐍 Создание виртуального окружения..."
sudo -u "$SERVICE_USER" python3 -m venv "$PROJECT_DIR/venv"

echo "📚 Установка зависимостей Python..."
sudo -u "$SERVICE_USER" "$PROJECT_DIR/venv/bin/pip" install --upgrade pip
sudo -u "$SERVICE_USER" "$PROJECT_DIR/venv/bin/pip" install -r "$PROJECT_DIR/requirements.txt"

echo "⚙️ Настройка конфигурации..."
if [ ! -f "$PROJECT_DIR/.env" ]; then
    if [ -f "$PROJECT_DIR/.env.example" ]; then
        cp "$PROJECT_DIR/.env.example" "$PROJECT_DIR/.env"
        echo "⚠️ Создан файл .env из примера. Пожалуйста, отредактируйте его:"
        echo "   sudo nano $PROJECT_DIR/.env"
    else
        echo "⚠️ Создайте файл .env с настройками:"
        echo "   sudo nano $PROJECT_DIR/.env"
    fi
else
    echo "ℹ️ Файл .env уже существует"
fi

echo "🔧 Настройка systemd service..."
cat > "/etc/systemd/system/$SERVICE_FILE" << EOF
[Unit]
Description=Telegram Order Bot
After=network.target

[Service]
Type=simple
User=$SERVICE_USER
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/python $PROJECT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "🔄 Перезагрузка systemd..."
systemctl daemon-reload

echo "✅ Развертывание завершено!"
echo ""
echo "📋 Следующие шаги:"
echo "1. Отредактируйте файл .env с вашими настройками:"
echo "   sudo nano $PROJECT_DIR/.env"
echo ""
echo "2. Запустите сервис:"
echo "   sudo systemctl start $SERVICE_FILE"
echo ""
echo "3. Включите автозапуск:"
echo "   sudo systemctl enable $SERVICE_FILE"
echo ""
echo "4. Проверьте статус:"
echo "   sudo systemctl status $SERVICE_FILE"
echo ""
echo "5. Просмотр логов:"
echo "   sudo journalctl -u $SERVICE_FILE -f"
