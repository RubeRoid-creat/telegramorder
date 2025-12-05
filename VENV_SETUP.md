# Быстрая настройка виртуального окружения

## ⚠️ Важно! Ошибка "externally-managed-environment"

Если при установке зависимостей вы видите:
```
error: externally-managed-environment
```

**Это нормально!** Ubuntu защищает систему от повреждений. Решение - использовать виртуальное окружение.

## Быстрая настройка (3 команды)

```bash
cd ~/telegram-order-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Полная инструкция

### Шаг 1: Перейдите в директорию проекта
```bash
cd ~/telegram-order-bot
```

### Шаг 2: Создайте виртуальное окружение
```bash
python3 -m venv venv
```

Если команда не работает, установите python3-venv:
```bash
sudo apt-get update
sudo apt-get install python3-venv
```

### Шаг 3: Активируйте виртуальное окружение
```bash
source venv/bin/activate
```

После активации в начале строки терминала появится `(venv)`.

### Шаг 4: Установите зависимости
```bash
pip install -r requirements.txt
```

### Шаг 5: Настройте конфигурацию
```bash
cp .env.example .env
nano .env
```

Укажите ваш токен бота в файле `.env`.

### Шаг 6: Проверьте конфигурацию
```bash
python check_config.py
```

### Шаг 7: Запустите бота
```bash
python bot.py
```

## Важно помнить

1. **Всегда активируйте виртуальное окружение перед работой:**
   ```bash
   source venv/bin/activate
   ```

2. **Деактивация виртуального окружения:**
   ```bash
   deactivate
   ```

3. **После перезагрузки сервера нужно снова активировать:**
   ```bash
   cd ~/telegram-order-bot
   source venv/bin/activate
   ```

## Для production (автозапуск)

Используйте скрипт развертывания, который автоматически настроит виртуальное окружение и systemd service:

```bash
sudo ./deploy.sh
```

## Дополнительная информация

- Подробная инструкция: [INSTALL_DEPS.md](INSTALL_DEPS.md)
- Решение проблем: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Быстрое решение: [QUICK_FIX.md](QUICK_FIX.md)
