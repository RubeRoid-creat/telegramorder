#!/usr/bin/env python3
"""
Скрипт для проверки конфигурации бота перед запуском
"""

import os
import sys
from dotenv import load_dotenv
import requests

def check_env_file():
    """Проверка наличия и содержимого .env файла"""
    print("🔍 Проверка файла .env...")
    
    if not os.path.exists(".env"):
        print("❌ Файл .env не найден!")
        print("   Создайте файл .env на основе .env.example")
        return False
    
    load_dotenv()
    
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token or bot_token == "your_telegram_bot_token_here":
        print("❌ BOT_TOKEN не установлен или имеет значение по умолчанию")
        print("   Укажите ваш токен бота в файле .env")
        return False
    
    print("✅ Файл .env найден и содержит BOT_TOKEN")
    return True, bot_token

def check_bot_token(bot_token):
    """Проверка валидности токена бота через Telegram API"""
    print("\n🔍 Проверка токена бота...")
    
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getMe"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("ok"):
                bot_info = data.get("result", {})
                print(f"✅ Токен валиден!")
                print(f"   Бот: @{bot_info.get('username')} ({bot_info.get('first_name')})")
                return True
            else:
                print(f"❌ Токен невалиден: {data.get('description', 'Unknown error')}")
                return False
        else:
            print(f"❌ Ошибка при проверке токена: HTTP {response.status_code}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Таймаут при подключении к Telegram API")
        print("   Проверьте подключение к интернету")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка подключения: {e}")
        return False

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("\n🔍 Проверка зависимостей...")
    
    required_modules = [
        "aiogram",
        "aiosqlite",
        "dotenv"
    ]
    
    missing = []
    for module in required_modules:
        try:
            if module == "dotenv":
                __import__("dotenv")
            elif module == "aiosqlite":
                __import__("aiosqlite")
            elif module == "aiogram":
                __import__("aiogram")
            print(f"✅ {module} установлен")
        except ImportError:
            print(f"❌ {module} не установлен")
            missing.append(module)
    
    if missing:
        print(f"\n❌ Не установлены модули: {', '.join(missing)}")
        print("   Установите зависимости: pip install -r requirements.txt")
        return False
    
    return True

def check_database_dir():
    """Проверка возможности создания базы данных"""
    print("\n🔍 Проверка прав на создание базы данных...")
    
    db_path = os.getenv("DATABASE_PATH", "orders.db")
    db_dir = os.path.dirname(os.path.abspath(db_path)) or "."
    
    if not os.path.exists(db_dir):
        try:
            os.makedirs(db_dir, exist_ok=True)
            print(f"✅ Директория для БД создана: {db_dir}")
        except Exception as e:
            print(f"❌ Не удалось создать директорию: {e}")
            return False
    
    # Проверяем права на запись
    test_file = os.path.join(db_dir, ".test_write")
    try:
        with open(test_file, "w") as f:
            f.write("test")
        os.remove(test_file)
        print(f"✅ Есть права на запись в директорию: {db_dir}")
        return True
    except Exception as e:
        print(f"❌ Нет прав на запись в директорию: {e}")
        return False

def main():
    """Главная функция проверки"""
    print("=" * 50)
    print("Проверка конфигурации Telegram Order Bot")
    print("=" * 50)
    
    all_ok = True
    
    # Проверка зависимостей
    if not check_dependencies():
        all_ok = False
    
    # Проверка .env файла
    env_check = check_env_file()
    if isinstance(env_check, tuple):
        env_ok, bot_token = env_check
        if env_ok:
            # Проверка токена
            if not check_bot_token(bot_token):
                all_ok = False
        else:
            all_ok = False
    else:
        all_ok = False
    
    # Проверка базы данных
    if not check_database_dir():
        all_ok = False
    
    print("\n" + "=" * 50)
    if all_ok:
        print("✅ Все проверки пройдены! Бот готов к запуску.")
        return 0
    else:
        print("❌ Обнаружены проблемы. Исправьте их перед запуском.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
