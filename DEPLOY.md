# Развертывание Telegram Order Bot на Ubuntu

Это руководство поможет вам развернуть бота на сервере Ubuntu с автозапуском через systemd.

## Предварительные требования

- Сервер с Ubuntu (18.04 или новее)
- Права sudo
- Токен Telegram бота

**Важно:** На Ubuntu используйте `python3` вместо `python`. Если команда `python` не найдена, всегда используйте `python3`.

## Способ 1: Автоматическое развертывание (рекомендуется)

### Шаг 1: Клонирование репозитория на сервер

```bash
cd /opt
sudo git clone https://github.com/RubeRoid-creat/telegramorder.git telegram-order-bot
cd telegram-order-bot
```

### Шаг 2: Запуск скрипта развертывания

```bash
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

Скрипт автоматически:
- Установит необходимые зависимости (Python 3, pip, venv)
- Создаст системного пользователя `telegram-bot`
- Скопирует файлы проекта
- Создаст виртуальное окружение
- Установит зависимости Python
- Настроит systemd service

### Шаг 3: Настройка конфигурации

Отредактируйте файл `.env`:

```bash
sudo nano /opt/telegram-order-bot/.env
```

Укажите ваш токен бота:

```
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_PATH=orders.db
```

### Шаг 4: Запуск и настройка автозапуска

```bash
# Запуск сервиса
sudo systemctl start telegram-order-bot.service

# Включение автозапуска при загрузке системы
sudo systemctl enable telegram-order-bot.service

# Проверка статуса
sudo systemctl status telegram-order-bot.service
```

### Шаг 5: Просмотр логов

```bash
# Просмотр логов в реальном времени
sudo journalctl -u telegram-order-bot.service -f

# Просмотр последних 100 строк логов
sudo journalctl -u telegram-order-bot.service -n 100
```

## Способ 2: Ручное развертывание

### Шаг 1: Установка системных зависимостей

```bash
sudo apt-get update
sudo apt-get install -y python3 python3-pip python3-venv git
```

### Шаг 2: Создание пользователя для сервиса

```bash
sudo useradd -r -s /bin/false -d /opt/telegram-order-bot -m telegram-bot
```

### Шаг 3: Клонирование проекта

```bash
cd /opt
sudo git clone https://github.com/RubeRoid-creat/telegramorder.git telegram-order-bot
sudo chown -R telegram-bot:telegram-bot /opt/telegram-order-bot
```

### Шаг 4: Создание виртуального окружения и установка зависимостей

```bash
cd /opt/telegram-order-bot
sudo -u telegram-bot python3 -m venv venv
sudo -u telegram-bot venv/bin/pip install --upgrade pip
sudo -u telegram-bot venv/bin/pip install -r requirements.txt
```

### Шаг 5: Настройка конфигурации

```bash
sudo -u telegram-bot cp .env.example .env
sudo nano /opt/telegram-order-bot/.env
```

Укажите ваш `BOT_TOKEN` в файле `.env`.

### Шаг 6: Установка systemd service

```bash
sudo cp telegram-order-bot.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### Шаг 7: Запуск сервиса

```bash
sudo systemctl start telegram-order-bot.service
sudo systemctl enable telegram-order-bot.service
sudo systemctl status telegram-order-bot.service
```

## Управление сервисом

### Команды для управления

```bash
# Запуск
sudo systemctl start telegram-order-bot.service

# Остановка
sudo systemctl stop telegram-order-bot.service

# Перезапуск
sudo systemctl restart telegram-order-bot.service

# Статус
sudo systemctl status telegram-order-bot.service

# Включить автозапуск
sudo systemctl enable telegram-order-bot.service

# Отключить автозапуск
sudo systemctl disable telegram-order-bot.service
```

### Просмотр логов

```bash
# Последние логи
sudo journalctl -u telegram-order-bot.service

# Логи в реальном времени
sudo journalctl -u telegram-order-bot.service -f

# Логи за последний час
sudo journalctl -u telegram-order-bot.service --since "1 hour ago"
```

## Обновление бота

### Способ 1: Через Git (рекомендуется)

```bash
cd /opt/telegram-order-bot
sudo systemctl stop telegram-order-bot.service
sudo -u telegram-bot git pull
sudo -u telegram-bot venv/bin/pip install -r requirements.txt
sudo systemctl start telegram-order-bot.service
```

### Способ 2: Через скрипт развертывания

```bash
cd /opt/telegram-order-bot
sudo git pull
sudo ./deploy.sh
```

## Устранение неполадок

### Бот не запускается

1. Проверьте статус сервиса:
   ```bash
   sudo systemctl status telegram-order-bot.service
   ```

2. Проверьте логи:
   ```bash
   sudo journalctl -u telegram-order-bot.service -n 50
   ```

3. Проверьте файл `.env`:
   ```bash
   sudo cat /opt/telegram-order-bot/.env
   ```

4. Проверьте права доступа:
   ```bash
   sudo ls -la /opt/telegram-order-bot
   ```

### Проблемы с правами доступа

```bash
sudo chown -R telegram-bot:telegram-bot /opt/telegram-order-bot
```

### Проблемы с базой данных

База данных создается автоматически при первом запуске. Убедитесь, что у пользователя `telegram-bot` есть права на запись в директорию проекта.

## Структура директорий

```
/opt/telegram-order-bot/
├── bot.py                    # Основной файл бота
├── database.py               # Работа с БД
├── requirements.txt          # Зависимости Python
├── .env                      # Конфигурация (создается вручную)
├── .env.example             # Пример конфигурации
├── venv/                    # Виртуальное окружение
├── orders.db                # База данных (создается автоматически)
└── telegram-order-bot.service # Systemd service файл
```

## Безопасность

- Файл `.env` содержит секретные данные, убедитесь, что он не попал в Git (должен быть в `.gitignore`)
- Пользователь `telegram-bot` имеет минимальные права доступа
- База данных хранится локально на сервере

## Поддержка

При возникновении проблем проверьте логи сервиса и убедитесь, что все зависимости установлены правильно.
