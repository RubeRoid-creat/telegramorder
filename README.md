# Telegram Order Bot

Телеграм-бот для управления заявками на ремонт техники.

## Функционал

- Создание заявок (адрес, время, тип техники, проблема)
- Просмотр активных заявок (исключая завершенные)
- Просмотр завершенных заявок (отдельный список)
- Удаление заявок с подтверждением
- Создание отчетов по заявкам со статусами:
  - Длительный ремонт (сумма согласования, дата/время завершения, что нужно сделать)
  - Завершен (заявка автоматически перемещается в список завершенных)
  - Отмена
  - Отказ
- Отчеты содержат: общая сумма, себестоимость (для завершенных)

## Установка

1. Установите зависимости:

**На Ubuntu/Linux:**
```bash
pip3 install -r requirements.txt
```

**Или если pip3 не установлен:**
```bash
python3 -m pip install -r requirements.txt
```

**На Windows:**
```bash
pip install -r requirements.txt
```

2. Создайте файл `.env` на основе `.env.example` и укажите токен бота:
```
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_PATH=orders.db
```

3. (Опционально) Проверьте конфигурацию перед запуском:
```bash
python3 check_config.py
```

4. Запустите бота:
```bash
python3 bot.py
```

**Примечание:** На Linux (Ubuntu) используйте `python3` вместо `python`. Если команда `python` не найдена, используйте `python3`.

**Примечание:** 
- Если бот не работает, см. [TROUBLESHOOTING.md](TROUBLESHOOTING.md) для диагностики проблем.
- На Ubuntu используйте `python3` вместо `python`. См. [QUICK_FIX.md](QUICK_FIX.md) для быстрого решения.
- Если видите ошибку `ModuleNotFoundError`, установите зависимости: `pip3 install -r requirements.txt`. См. [INSTALL_DEPS.md](INSTALL_DEPS.md) для подробной инструкции.

## Устранение неполадок

Если бот не работает, см. подробное руководство: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

### Быстрая диагностика:

1. Проверьте конфигурацию:
   ```bash
   python3 check_config.py
   ```
   
   **Примечание:** Если получаете ошибку "Command 'python' not found", используйте `python3` вместо `python`.

2. Проверьте логи:
   - Локально: файл `bot.log` в директории проекта
   - На сервере: `sudo journalctl -u telegram-order-bot.service -f`

3. Типичные проблемы:
   - **Бот не отвечает**: проверьте токен в `.env`, убедитесь что бот запущен
   - **Ошибки БД**: проверьте права доступа к директории проекта
   - **Ошибки импорта**: установите зависимости `pip install -r requirements.txt`

## Использование

- `/start` - Начать работу с ботом
- `/new_order` - Создать новую заявку
- `/my_orders` - Просмотреть активные заявки (исключая завершенные)
- `/completed_orders` - Просмотреть завершенные заявки
- `/report` - Создать отчет по заявке
- `/delete_order` - Удалить заявку

**Примечания:**
- При создании отчета со статусом "Завершен" заявка автоматически перемещается из списка активных заявок в отдельный список завершенных заявок.
- При удалении заявки также удаляются все связанные с ней отчеты. Удаление требует подтверждения.

## Развертывание на сервере Ubuntu

Для развертывания бота на сервере Ubuntu с автозапуском через systemd см. подробную инструкцию в файле [DEPLOY.md](DEPLOY.md).

### Краткая инструкция:

1. Клонируйте репозиторий на сервер:
```bash
cd /opt
sudo git clone https://github.com/RubeRoid-creat/telegramorder.git telegram-order-bot
cd telegram-order-bot
```

2. Запустите скрипт развертывания:
```bash
sudo chmod +x deploy.sh
sudo ./deploy.sh
```

3. Настройте `.env` файл:
```bash
sudo nano /opt/telegram-order-bot/.env
```

4. Запустите и включите автозапуск:
```bash
sudo systemctl start telegram-order-bot.service
sudo systemctl enable telegram-order-bot.service
```

5. Проверьте статус:
```bash
sudo systemctl status telegram-order-bot.service
```

