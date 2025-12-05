# Руководство по устранению неполадок

## Типичные проблемы и их решения

### 1. Ошибка "Command 'python' not found" (Ubuntu/Linux)

#### Проблема: Команда python не найдена

**Симптомы:**
```
Command 'python' not found, did you mean:
  command 'python3' from deb python3
  command 'python' from deb python-is-python3
```

**Решение:**

**Вариант 1 (рекомендуется):** Используйте `python3` вместо `python`
```bash
python3 check_config.py
python3 bot.py
```

**Вариант 2:** Установите пакет для создания символической ссылки:
```bash
sudo apt-get update
sudo apt-get install python-is-python3
```

После этого команда `python` будет работать как `python3`.

**Примечание:** В документации и скриптах на Ubuntu всегда используется `python3`.

### 2. Бот не запускается

#### Проблема: Ошибка "externally-managed-environment"

**Симптомы:**
```
error: externally-managed-environment
This environment is externally managed.
```

**Причина:**
Современные версии Ubuntu (23.04+) блокируют установку пакетов системно через pip для защиты системы.

**Решение (ОБЯЗАТЕЛЬНО использовать виртуальное окружение):**

```bash
cd ~/telegram-order-bot

# Создайте виртуальное окружение
python3 -m venv venv

# Активируйте его
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt

# После этого запускайте бота через виртуальное окружение
python bot.py
```

**Важно:** Не используйте `--break-system-packages`, это может сломать систему!

**Подробная инструкция:** См. [INSTALL_DEPS.md](INSTALL_DEPS.md)

#### Проблема: ModuleNotFoundError - зависимости не установлены

**Симптомы:**
```
ModuleNotFoundError: No module named 'dotenv'
ModuleNotFoundError: No module named 'aiogram'
```

**Решение:**

1. **Создайте виртуальное окружение и установите зависимости:**
   ```bash
   cd ~/telegram-order-bot
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **После установки активируйте виртуальное окружение перед запуском:**
   ```bash
   source venv/bin/activate
   python bot.py
   ```

**Подробная инструкция:** См. [INSTALL_DEPS.md](INSTALL_DEPS.md)

#### Проблема: Ошибка "BOT_TOKEN не установлен"

**Симптомы:**
```
ValueError: BOT_TOKEN не установлен в .env файле
```

**Решение:**
1. Проверьте наличие файла `.env` в директории проекта
2. Убедитесь, что в файле указан правильный токен:
   ```
   BOT_TOKEN=ваш_токен_бота
   DATABASE_PATH=orders.db
   ```
3. Проверьте, что нет лишних пробелов или кавычек в токене

#### Проблема: Ошибка импорта модулей

**Симптомы:**
```
ModuleNotFoundError: No module named 'aiogram'
ImportError: cannot import name 'Bot' from 'aiogram'
```

**Решение:**
1. Проверьте, установлены ли все зависимости:
   
   **На Ubuntu/Linux:**
   ```bash
   pip3 install -r requirements.txt
   ```
   
   **Или если pip3 не найден:**
   ```bash
   python3 -m pip install -r requirements.txt
   ```
   
   **С правами root (если требуется):**
   ```bash
   sudo pip3 install -r requirements.txt
   ```

2. Если используете виртуальное окружение, убедитесь, что оно активировано:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. Проверьте версию Python (требуется Python 3.8+):
   ```bash
   python3 --version
   ```
   
   **Примечание:** На Ubuntu используйте `python3` вместо `python`.

4. После установки зависимостей проверьте, что они установлены:
   ```bash
   python3 -c "import aiogram; import dotenv; print('Все зависимости установлены')"
   ```

### 2. Бот запускается, но не отвечает на сообщения

#### Проблема: Бот не получает обновления

**Диагностика:**
1. Проверьте логи бота на наличие ошибок
2. Проверьте, что токен бота правильный:
   - Откройте https://api.telegram.org/bot<ВАШ_ТОКЕН>/getMe
   - Должна вернуться информация о боте

**Решение:**
1. Перезапустите бота
2. Проверьте подключение к интернету
3. Проверьте, что бот не запущен несколько раз одновременно

#### Проблема: Ошибки при обработке сообщений

**Симптомы:**
- Бот отвечает на одни команды, но не на другие
- Появляются ошибки в логах при обработке конкретных команд

**Решение:**
1. Проверьте логи на наличие исключений
2. Убедитесь, что база данных инициализирована правильно
3. Проверьте права доступа к файлу базы данных

### 3. Проблемы с базой данных

#### Проблема: Ошибка доступа к базе данных

**Симптомы:**
```
sqlite3.OperationalError: unable to open database file
```

**Решение:**
1. Проверьте права доступа к директории, где должна создаваться БД
2. Убедитесь, что указан правильный путь в `.env`
3. Проверьте, что у пользователя есть права на запись

#### Проблема: Ошибки миграции базы данных

**Симптомы:**
- Ошибки при создании таблиц
- Сообщения о несуществующих колонках

**Решение:**
1. Удалите старую базу данных и позвольте создать новую:
   ```bash
   rm orders.db
   ```
2. Перезапустите бота

### 4. Проблемы на сервере Ubuntu

#### Проблема: Systemd сервис не запускается

**Диагностика:**
```bash
sudo systemctl status telegram-order-bot.service
sudo journalctl -u telegram-order-bot.service -n 50
```

**Возможные причины:**
1. Неправильный путь к Python или виртуальному окружению
2. Отсутствие файла `.env`
3. Неправильные права доступа

**Решение:**
1. Проверьте путь к Python в service файле:
   ```bash
   sudo cat /etc/systemd/system/telegram-order-bot.service
   ```
2. Проверьте наличие и содержимое `.env`:
   ```bash
   sudo cat /opt/telegram-order-bot/.env
   ```
3. Проверьте права доступа:
   ```bash
   sudo ls -la /opt/telegram-order-bot/
   ```

#### Проблема: Бот постоянно перезапускается

**Симптомы:**
- В логах видны постоянные перезапуски
- Статус сервиса показывает "failed"

**Решение:**
1. Проверьте логи на наличие ошибок:
   ```bash
   sudo journalctl -u telegram-order-bot.service -f
   ```
2. Проверьте, что все зависимости установлены
3. Проверьте, что токен бота правильный

### 5. Проблемы с зависимостями

#### Проблема: Конфликты версий

**Решение:**
1. Обновите зависимости:
   ```bash
   pip install --upgrade -r requirements.txt
   ```
2. Используйте виртуальное окружение для изоляции зависимостей

### 6. Диагностические команды

#### Проверка работоспособности бота

1. Проверка токена:
   ```bash
   curl https://api.telegram.org/bot<ВАШ_ТОКЕН>/getMe
   ```

2. Проверка файлов проекта:
   ```bash
   ls -la /opt/telegram-order-bot/
   ```

3. Проверка процесса:
   ```bash
   ps aux | grep bot.py
   ```

4. Проверка логов (systemd):
   ```bash
   sudo journalctl -u telegram-order-bot.service --since "1 hour ago"
   ```

5. Тестовый запуск бота вручную:
   ```bash
   cd /opt/telegram-order-bot
   sudo -u telegram-bot /opt/telegram-order-bot/venv/bin/python bot.py
   ```

### 7. Чек-лист проверки

- [ ] Файл `.env` существует и содержит правильный `BOT_TOKEN`
- [ ] Все зависимости установлены (`pip install -r requirements.txt`)
- [ ] База данных создана и доступна для записи
- [ ] Бот запущен и работает (проверка через `/start`)
- [ ] Нет ошибок в логах
- [ ] На сервере: systemd service активен и включен
- [ ] На сервере: правильные права доступа к файлам

## Получение помощи

Если проблема не решена:
1. Проверьте логи на наличие ошибок
2. Убедитесь, что используете последнюю версию кода
3. Проверьте документацию aiogram: https://docs.aiogram.dev/
