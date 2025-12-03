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


def get_main_keyboard():
    """Главная клавиатура"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📝 Новая заявка"), KeyboardButton(text="📋 Мои заявки")],
            [KeyboardButton(text="📊 Создать отчет")]
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
        "• Просмотреть свои заявки\n"
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
    """Просмотр заявок пользователя"""
    orders = await db.get_user_orders(message.from_user.id)
    
    if not orders:
        await message.answer("У вас пока нет заявок.", reply_markup=get_main_keyboard())
        return
    
    text = "📋 Ваши заявки:\n\n"
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
            f"Статус: {order['status']}\n\n"
        )
    
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
    
    if status in ["completed", "long_repair"]:
        await state.set_state(ReportStates.waiting_total_amount)
        await message.answer(
            "Введите общую сумму (число):",
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
    """Обработка себестоимости и сохранение отчета"""
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
            f"✅ Отчет создан для заявки #{data['order_id']}\n\n"
            f"Общая сумма: {data.get('total_amount', 0)} руб.\n"
            f"Себестоимость: {cost_price} руб.",
            reply_markup=get_main_keyboard()
        )
    except ValueError:
        await message.answer("❌ Введите корректное число.")


async def main():
    """Главная функция"""
    await db.init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

