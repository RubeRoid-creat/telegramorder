# Быстрое решение проблем

## Ошибка "Command 'python' not found" на Ubuntu

Если при запуске бота вы видите ошибку:
```
Command 'python' not found, did you mean:
  command 'python3' from deb python3
```

### Решение:

Просто используйте `python3` вместо `python`:

```bash
# Вместо:
python check_config.py

# Используйте:
python3 check_config.py

# Вместо:
python bot.py

# Используйте:
python3 bot.py
```

### Или установите пакет для совместимости:

```bash
sudo apt-get update
sudo apt-get install python-is-python3
```

После этого команда `python` будет работать как `python3`.

## Проверка конфигурации перед запуском

```bash
python3 check_config.py
```

Этот скрипт проверит:
- ✅ Наличие и правильность файла `.env`
- ✅ Валидность токена бота
- ✅ Установленные зависимости
- ✅ Права доступа к директории

## Запуск бота

```bash
python3 bot.py
```

## Просмотр логов

Если бот не работает, проверьте логи:

```bash
# Локально
tail -f bot.log

# На сервере (systemd)
sudo journalctl -u telegram-order-bot.service -f
```

## Ошибка "ModuleNotFoundError" - зависимости не установлены

Если вы видите ошибки:
```
ModuleNotFoundError: No module named 'dotenv'
ModuleNotFoundError: No module named 'aiogram'
```

### Быстрое решение:

**На сервере Ubuntu:**
```bash
cd ~/telegram-order-bot
pip3 install -r requirements.txt
```

Если `pip3` не найден, установите его:
```bash
sudo apt-get update
sudo apt-get install python3-pip
```

Подробная инструкция по установке зависимостей: [INSTALL_DEPS.md](INSTALL_DEPS.md)

## Частые проблемы

1. **"BOT_TOKEN не установлен"** - Проверьте файл `.env`
2. **"ModuleNotFoundError"** - Установите зависимости (см. выше)
3. **"python not found"** - Используйте `python3` вместо `python`
4. **"pip not found"** - Используйте `pip3` или `python3 -m pip`

Подробнее см. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
