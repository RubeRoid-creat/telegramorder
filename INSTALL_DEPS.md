# Установка зависимостей

## Проблема: ModuleNotFoundError

Если вы видите ошибки:
```
ModuleNotFoundError: No module named 'dotenv'
ModuleNotFoundError: No module named 'aiogram'
```

Это означает, что зависимости Python не установлены.

## Быстрое решение для сервера Ubuntu

### Способ 1: Установка глобально (простой способ)

```bash
# Перейдите в директорию проекта
cd ~/telegram-order-bot

# Установите зависимости
pip3 install -r requirements.txt
```

Если команда `pip3` не найдена, установите pip:
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

### Способ 2: Использование виртуального окружения (рекомендуется)

```bash
# Перейдите в директорию проекта
cd ~/telegram-order-bot

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте виртуальное окружение
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# Теперь можно запустить бота
python bot.py
```

**Важно:** После активации виртуального окружения в начале строки терминала появится `(venv)`.

### Способ 3: Использование скрипта развертывания (для production)

Если вы развертываете бота на сервере, используйте скрипт развертывания:

```bash
cd ~/telegram-order-bot
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

Скрипт автоматически:
- Установит системные зависимости
- Создаст виртуальное окружение
- Установит все зависимости Python
- Настроит systemd service для автозапуска

## Проверка установки

После установки зависимостей проверьте, что всё работает:

```bash
python3 -c "import aiogram; import dotenv; print('✅ Все зависимости установлены')"
```

Если команда выполнилась без ошибок, зависимости установлены правильно.

## Что установить, если команды не работают

Если `python3` не найден:
```bash
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv
```

Если `pip3` не найден:
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

## После установки

1. Создайте файл `.env` (если ещё не создан):
   ```bash
   cp .env.example .env
   nano .env
   ```

2. Укажите токен бота в файле `.env`

3. Проверьте конфигурацию:
   ```bash
   python3 check_config.py
   ```

4. Запустите бота:
   ```bash
   python3 bot.py
   ```

## Дополнительная информация

- Подробная инструкция по развертыванию: [DEPLOY.md](DEPLOY.md)
- Решение других проблем: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Быстрое решение проблем: [QUICK_FIX.md](QUICK_FIX.md)
