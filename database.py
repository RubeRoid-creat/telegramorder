import aiosqlite
import os
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum


class OrderStatus(Enum):
    """Статусы заявок"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    LONG_REPAIR = "long_repair"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REFUSED = "refused"


class Database:
    def __init__(self, db_path: str = "orders.db"):
        self.db_path = db_path

    async def init_db(self):
        """Инициализация базы данных"""
        async with aiosqlite.connect(self.db_path) as db:
            # Таблица заявок
            await db.execute("""
                CREATE TABLE IF NOT EXISTS orders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    address TEXT NOT NULL,
                    time TEXT NOT NULL,
                    equipment_type TEXT NOT NULL,
                    problem TEXT NOT NULL,
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Таблица отчетов
            await db.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER NOT NULL,
                    status TEXT NOT NULL,
                    total_amount REAL,
                    cost_price REAL,
                    agreed_amount REAL,
                    completion_date TEXT,
                    completion_time TEXT,
                    what_to_do TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (order_id) REFERENCES orders (id)
                )
            """)
            
            # Добавляем новые поля, если таблица уже существует
            try:
                await db.execute("ALTER TABLE reports ADD COLUMN agreed_amount REAL")
            except aiosqlite.OperationalError:
                pass  # Поле уже существует
            
            try:
                await db.execute("ALTER TABLE reports ADD COLUMN completion_date TEXT")
            except aiosqlite.OperationalError:
                pass
            
            try:
                await db.execute("ALTER TABLE reports ADD COLUMN completion_time TEXT")
            except aiosqlite.OperationalError:
                pass
            
            try:
                await db.execute("ALTER TABLE reports ADD COLUMN what_to_do TEXT")
            except aiosqlite.OperationalError:
                pass
            
            await db.commit()

    async def create_order(
        self,
        user_id: int,
        address: str,
        time: str,
        equipment_type: str,
        problem: str
    ) -> int:
        """Создание новой заявки"""
        async with aiosqlite.connect(self.db_path) as db:
            cursor = await db.execute("""
                INSERT INTO orders (user_id, address, time, equipment_type, problem)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, address, time, equipment_type, problem))
            await db.commit()
            return cursor.lastrowid

    async def get_user_orders(self, user_id: int, exclude_completed: bool = True) -> List[Dict]:
        """Получение заявок пользователя (по умолчанию исключает завершенные)"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            if exclude_completed:
                async with db.execute("""
                    SELECT * FROM orders 
                    WHERE user_id = ? AND status != 'completed'
                    ORDER BY created_at DESC
                """, (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]
            else:
                async with db.execute("""
                    SELECT * FROM orders 
                    WHERE user_id = ? 
                    ORDER BY created_at DESC
                """, (user_id,)) as cursor:
                    rows = await cursor.fetchall()
                    return [dict(row) for row in rows]

    async def get_completed_orders(self, user_id: int) -> List[Dict]:
        """Получение только завершенных заявок пользователя"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM orders 
                WHERE user_id = ? AND status = 'completed'
                ORDER BY created_at DESC
            """, (user_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

    async def get_order(self, order_id: int, user_id: int) -> Optional[Dict]:
        """Получение конкретной заявки"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM orders 
                WHERE id = ? AND user_id = ?
            """, (order_id, user_id)) as cursor:
                row = await cursor.fetchone()
                return dict(row) if row else None

    async def create_report(
        self,
        order_id: int,
        status: str,
        total_amount: Optional[float] = None,
        cost_price: Optional[float] = None,
        agreed_amount: Optional[float] = None,
        completion_date: Optional[str] = None,
        completion_time: Optional[str] = None,
        what_to_do: Optional[str] = None
    ) -> int:
        """Создание отчета по заявке"""
        async with aiosqlite.connect(self.db_path) as db:
            # Обновляем статус заявки
            await db.execute("""
                UPDATE orders SET status = ? WHERE id = ?
            """, (status, order_id))
            
            # Создаем отчет
            cursor = await db.execute("""
                INSERT INTO reports (order_id, status, total_amount, cost_price, 
                                   agreed_amount, completion_date, completion_time, what_to_do)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (order_id, status, total_amount, cost_price, 
                  agreed_amount, completion_date, completion_time, what_to_do))
            
            await db.commit()
            return cursor.lastrowid

    async def get_order_reports(self, order_id: int) -> List[Dict]:
        """Получение всех отчетов по заявке"""
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            async with db.execute("""
                SELECT * FROM reports 
                WHERE order_id = ? 
                ORDER BY created_at DESC
            """, (order_id,)) as cursor:
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]

