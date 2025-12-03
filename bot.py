import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from database import Database, OrderStatus

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_PATH = os.getenv("DATABASE_PATH", "orders.db")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не установлен в .env файле")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
db = Database(DATABASE_PATH)


class OrderStates(StatesGroup):
    """Состояния для создания заявки"""
    waiting_address = State()
    waiting_time = State()
    waiting_equipment = State()
    waiting_problem = State()


class ReportStates(StatesGroup):
    """Состояния для создания отчета"""
    waiting_order_id = State()
    waiting_status = State()
    waiting_total_amount = State()
    waiting_cost_price = State()
    # Состояния для длительного ремонта
    waiting_agreed_amount = State()
    waiting_completion_date = State()
    waiting_completion_time = State()
    waiting_what_to_do = State()


def get_main_keyboard():
    """Главная клавиатура"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Новая заявка"), KeyboardButton(text="📋 Мои заявки")],
            [KeyboardButton(text="✅ Завершенные заявки"), KeyboardButton(text="📊 Создать отчет")]
        ],
        resize_keyboard=True
    )


def get_report_status_keyboard():
    """Клавиатура выбора статуса отчета"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="⏳ Длительный ремонт")],
            [KeyboardButton(text="✅ Завершен")],
            [KeyboardButton(text="❌ Отмена")],
            [KeyboardButton(text="🚫 Отказ")],
            [KeyboardButton(text="🔙 Назад")]
        ],
        resize_keyboard=True
    )


@dp.message(Command("start"))
async def cmd_start(message: Message):
    """Обработчик команды /start"""
    await message.answer(
        "👋 Добро пожаловать в бот управления заявками!\n\n"
        "Вы можете:\n"
        "• Создать новую заявку\n"
        "• Просмотреть активные заявки\n"
        "• Просмотреть завершенные заявки\n"
        "• Создать отчет по заявке",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "📝 Новая заявка")
@dp.message(Command("new_order"))
async def cmd_new_order(message: Message, state: FSMContext):
    """Начало создания новой заявки"""
    await state.set_state(OrderStates.waiting_address)
    await message.answer(
        "📝 Создание новой заявки\n\n"
        "Введите адрес:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(OrderStates.waiting_address)
async def process_address(message: Message, state: FSMContext):
    """Обработка адреса"""
    await state.update_data(address=message.text)
    await state.set_state(OrderStates.waiting_time)
    await message.answer("Введите время:")


@dp.message(OrderStates.waiting_time)
async def process_time(message: Message, state: FSMContext):
    """Обработка времени"""
    await state.update_data(time=message.text)
    await state.set_state(OrderStates.waiting_equipment)
    await message.answer("Введите тип техники:")


@dp.message(OrderStates.waiting_equipment)
async def process_equipment(message: Message, state: FSMContext):
    """Обработка типа техники"""
    await state.update_data(equipment_type=message.text)
    await state.set_state(OrderStates.waiting_problem)
    await message.answer("Опишите проблему:")


@dp.message(OrderStates.waiting_problem)
async def process_problem(message: Message, state: FSMContext):
    """Обработка проблемы и сохранение заявки"""
    data = await state.get_data()
    data["problem"] = message.text
    
    order_id = await db.create_order(
        user_id=message.from_user.id,
        address=data["address"],
        time=data["time"],
        equipment_type=data["equipment_type"],
        problem=data["problem"]
    )
    
    await state.clear()
    await message.answer(
        f"✅ Заявка #{order_id} успешно создана!\n\n"
        f"Адрес: {data['address']}\n"
        f"Время: {data['time']}\n"
        f"Тип техники: {data['equipment_type']}\n"
        f"Проблема: {data['problem']}",
        reply_markup=get_main_keyboard()
    )


@dp.message(F.text == "📋 Мои заявки")
@dp.message(Command("my_orders"))
async def cmd_my_orders(message: Message):
    """Просмотр активных заявок пользователя (исключая завершенные)"""
    orders = await db.get_user_orders(message.from_user.id, exclude_completed=True)
    
    if not orders:
        await message.answer("У вас нет активных заявок.", reply_markup=get_main_keyboard())
        return
    
    text = "📋 Ваши активные заявки:\n\n"
    for order in orders:
        status_emoji = {
            "pending": "⏳",
            "in_progress": "🔧",
            "long_repair": "⏳",
            "completed": "✅",
            "cancelled": "❌",
            "refused": "🚫"
        }.get(order["status"], "❓")
        
        text += (
            f"{status_emoji} Заявка #{order['id']}\n"
            f"Адрес: {order['address']}\n"
            f"Время: {order['time']}\n"
            f"Техника: {order['equipment_type']}\n"
            f"Проблема: {order['problem']}\n"
            f"Статус: {order['status']}\n"
        )
        
        # Если это длительный ремонт, показываем информацию из отчета
        if order["status"] == "long_repair":
            reports = await db.get_order_reports(order["id"])
            latest_report = reports[0] if reports else None
            if latest_report:
                text += (
                    f"Сумма согласования: {latest_report.get('agreed_amount', 0)} руб.\n"
                    f"Дата завершения: {latest_report.get('completion_date', 'не указана')}\n"
                    f"Время завершения: {latest_report.get('completion_time', 'не указано')}\n"
                    f"Что нужно сделать: {latest_report.get('what_to_do', 'не указано')}\n"
                )
        
        text += "\n"
    
    await message.answer(text, reply_markup=get_main_keyboard())


@dp.message(F.text == "✅ Завершенные заявки")
@dp.message(Command("completed_orders"))
async def cmd_completed_orders(message: Message):
    """Просмотр завершенных заявок пользователя"""
    orders = await db.get_completed_orders(message.from_user.id)
    
    if not orders:
        await message.answer("У вас нет завершенных заявок.", reply_markup=get_main_keyboard())
        return
    
    text = "✅ Завершенные заявки:\n\n"
    for order in orders:
        # Получаем отчеты для каждой заявки
        reports = await db.get_order_reports(order["id"])
        latest_report = reports[0] if reports else None
        
        text += (
            f"✅ Заявка #{order['id']}\n"
            f"Адрес: {order['address']}\n"
            f"Время: {order['time']}\n"
            f"Техника: {order['equipment_type']}\n"
            f"Проблема: {order['problem']}\n"
        )
        
        if latest_report and latest_report.get("total_amount"):
            text += (
                f"Общая сумма: {latest_report['total_amount']} руб.\n"
                f"Себестоимость: {latest_report.get('cost_price', 0)} руб.\n"
            )
        
        text += "\n"
    
    await message.answer(text, reply_markup=get_main_keyboard())


@dp.message(F.text == "📊 Создать отчет")
@dp.message(Command("report"))
async def cmd_report(message: Message, state: FSMContext):
    """Начало создания отчета"""
    await state.set_state(ReportStates.waiting_order_id)
    await message.answer(
        "📊 Создание отчета\n\n"
        "Введите номер заявки:",
        reply_markup=ReplyKeyboardRemove()
    )


@dp.message(ReportStates.waiting_order_id)
async def process_order_id(message: Message, state: FSMContext):
    """Обработка номера заявки"""
    try:
        order_id = int(message.text)
        order = await db.get_order(order_id, message.from_user.id)
        
        if not order:
            await message.answer("❌ Заявка не найдена. Проверьте номер заявки.")
            return
        
        await state.update_data(order_id=order_id)
        await state.set_state(ReportStates.waiting_status)
        await message.answer(
            "Выберите статус отчета:",
            reply_markup=get_report_status_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректный номер заявки (число).")


@dp.message(ReportStates.waiting_status)
async def process_report_status(message: Message, state: FSMContext):
    """Обработка статуса отчета"""
    status_map = {
        "⏳ Длительный ремонт": "long_repair",
        "✅ Завершен": "completed",
        "❌ Отмена": "cancelled",
        "🚫 Отказ": "refused"
    }
    
    if message.text not in status_map:
        if message.text == "🔙 Назад":
            await state.clear()
            await message.answer("Отменено.", reply_markup=get_main_keyboard())
            return
        await message.answer("Выберите статус из предложенных.")
        return
    
    status = status_map[message.text]
    await state.update_data(status=status)
    
    if status == "completed":
        # Для завершенных заявок - общая сумма и себестоимость
        await state.set_state(ReportStates.waiting_total_amount)
        await message.answer(
            "Введите общую сумму (число):",
            reply_markup=ReplyKeyboardRemove()
        )
    elif status == "long_repair":
        # Для длительного ремонта - сумма согласования
        await state.set_state(ReportStates.waiting_agreed_amount)
        await message.answer(
            "Введите сумму согласования (число):",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        # Для отмены и отказа сумма не требуется
        data = await state.get_data()
        await db.create_report(
            order_id=data["order_id"],
            status=data["status"],
            total_amount=None,
            cost_price=None
        )
        await state.clear()
        await message.answer(
            f"✅ Отчет создан для заявки #{data['order_id']}\n"
            f"Статус: {message.text}",
            reply_markup=get_main_keyboard()
        )


@dp.message(ReportStates.waiting_total_amount)
async def process_total_amount(message: Message, state: FSMContext):
    """Обработка общей суммы"""
    try:
        total_amount = float(message.text)
        await state.update_data(total_amount=total_amount)
        await state.set_state(ReportStates.waiting_cost_price)
        await message.answer("Введите себестоимость (число):")
    except ValueError:
        await message.answer("❌ Введите корректное число.")


@dp.message(ReportStates.waiting_cost_price)
async def process_cost_price(message: Message, state: FSMContext):
    """Обработка себестоимости и сохранение отчета для завершенных заявок"""
    try:
        cost_price = float(message.text)
        data = await state.get_data()
        
        await db.create_report(
            order_id=data["order_id"],
            status=data["status"],
            total_amount=data.get("total_amount"),
            cost_price=cost_price
        )
        
        await state.clear()
        
        await message.answer(
            f"✅ Отчет создан для заявки #{data['order_id']}\n"
            f"Статус: ✅ Завершен\n\n"
            f"📌 Заявка перемещена в список завершенных заявок\n\n"
            f"Общая сумма: {data.get('total_amount', 0)} руб.\n"
            f"Себестоимость: {cost_price} руб.",
            reply_markup=get_main_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректное число.")


@dp.message(ReportStates.waiting_agreed_amount)
async def process_agreed_amount(message: Message, state: FSMContext):
    """Обработка суммы согласования для длительного ремонта"""
    try:
        agreed_amount = float(message.text)
        await state.update_data(agreed_amount=agreed_amount)
        await state.set_state(ReportStates.waiting_completion_date)
        await message.answer("Введите дату завершения (например: 2024-12-31 или 31.12.2024):")
    except ValueError:
        await message.answer("❌ Введите корректное число.")


@dp.message(ReportStates.waiting_completion_date)
async def process_completion_date(message: Message, state: FSMContext):
    """Обработка даты завершения"""
    await state.update_data(completion_date=message.text)
    await state.set_state(ReportStates.waiting_completion_time)
    await message.answer("Введите время завершения (например: 18:00):")


@dp.message(ReportStates.waiting_completion_time)
async def process_completion_time(message: Message, state: FSMContext):
    """Обработка времени завершения"""
    await state.update_data(completion_time=message.text)
    await state.set_state(ReportStates.waiting_what_to_do)
    await message.answer("Опишите, что нужно сделать:")


@dp.message(ReportStates.waiting_what_to_do)
async def process_what_to_do(message: Message, state: FSMContext):
    """Обработка описания работ и сохранение отчета для длительного ремонта"""
    data = await state.get_data()
    data["what_to_do"] = message.text
    
    await db.create_report(
        order_id=data["order_id"],
        status=data["status"],
        agreed_amount=data.get("agreed_amount"),
        completion_date=data.get("completion_date"),
        completion_time=data.get("completion_time"),
        what_to_do=data.get("what_to_do")
    )
    
    await state.clear()
    await message.answer(
        f"✅ Отчет создан для заявки #{data['order_id']}\n"
        f"Статус: ⏳ Длительный ремонт\n\n"
        f"Сумма согласования: {data.get('agreed_amount', 0)} руб.\n"
        f"Дата завершения: {data.get('completion_date')}\n"
        f"Время завершения: {data.get('completion_time')}\n"
        f"Что нужно сделать: {data.get('what_to_do')}",
        reply_markup=get_main_keyboard()
    )


async def main():
    """Главная функция"""
    await db.init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

