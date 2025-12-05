# Быстрое решение проблем

## ⚠️ Ошибка "externally-managed-environment" (самая частая проблема!)

Если при установке зависимостей вы видите эту ошибку, **используйте виртуальное окружение:**

```bash
cd ~/telegram-order-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

**Подробная инструкция:** [VENV_SETUP.md](VENV_SETUP.md)

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

**Если используете виртуальное окружение:**
```bash
source venv/bin/activate
python check_config.py
```

**Если зависимости установлены глобально:**
```bash
python3 check_config.py
```

Этот скрипт проверит:
- ✅ Наличие и правильность файла `.env`
- ✅ Валидность токена бота
- ✅ Установленные зависимости
- ✅ Права доступа к директории

## Запуск бота

**Если используете виртуальное окружение:**
```bash
source venv/bin/activate
python bot.py
```

**Если зависимости установлены глобально:**
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

## Ошибка "externally-managed-environment" при установке зависимостей

Если вы видите ошибку:
```
error: externally-managed-environment
This environment is externally managed...
```

### ⚠️ Решение: Используйте виртуальное окружение (ОБЯЗАТЕЛЬНО)

**Это единственный правильный способ на современных Ubuntu!**

```bash
cd ~/telegram-order-bot

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Теперь установите зависимости (обратите внимание - используем просто pip)
pip install -r requirements.txt

# Проверьте конфигурацию
python check_config.py

# Запустите бота
python bot.py
```

**Важно:** После активации виртуального окружения в начале строки появится `(venv)`.

## Ошибка "ModuleNotFoundError" - зависимости не установлены

Если вы видите ошибки:
```
ModuleNotFoundError: No module named 'dotenv'
ModuleNotFoundError: No module named 'aiogram'
```

### Быстрое решение:

**Создайте и используйте виртуальное окружение:**
```bash
cd ~/telegram-order-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Подробная инструкция по установке зависимостей: [INSTALL_DEPS.md](INSTALL_DEPS.md)

## Частые проблемы

1. **"BOT_TOKEN не установлен"** - Проверьте файл `.env`
2. **"ModuleNotFoundError"** - Установите зависимости (см. выше)
3. **"python not found"** - Используйте `python3` вместо `python`
4. **"pip not found"** - Используйте `pip3` или `python3 -m pip`

Подробнее см. [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
